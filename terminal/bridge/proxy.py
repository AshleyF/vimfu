"""
WebSocket ↔ PTY bridge for vt-term.

Run on the machine where you want shells to live; the browser
connects via WebSocket and gets raw PTY output back.

Wire protocol — client → server (JSON text frames):

    {"type": "input",  "data": "..."}              # bytes/string to write to PTY
    {"type": "resize", "rows": 24, "cols": 80}     # window resize

Server → client:

    binary frames        # raw PTY output bytes
    {"type": "exit",  "code": N}                   # process exited

Cross-platform:

    Windows  → pywinpty (ConPTY)
    macOS/Linux → stdlib pty.fork()

Usage:

    python bridge/proxy.py                         # bind 127.0.0.1:7681, run default shell
    python bridge/proxy.py --shell bash --port 9000
    python bridge/proxy.py --shell "C:\\Windows\\System32\\cmd.exe"
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import signal
import threading
from typing import Optional

# UTF-8 stdout on Windows (cp1252) — VT terminal status prints arrows, etc.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import websockets
except ImportError:
    print("error: pip install -r bridge/requirements.txt", file=sys.stderr)
    sys.exit(1)

IS_WIN = sys.platform == "win32"


# ─────────────────────────────────────────────────────────────────────
# PTY abstraction
# ─────────────────────────────────────────────────────────────────────

class PtyBase:
    """Common interface for Windows/Unix PTYs."""

    def write(self, data: bytes) -> None: raise NotImplementedError
    def read(self) -> Optional[bytes]:    raise NotImplementedError
    def resize(self, rows: int, cols: int) -> None: raise NotImplementedError
    def close(self) -> None: raise NotImplementedError
    def isalive(self) -> bool: raise NotImplementedError
    @property
    def exitcode(self) -> Optional[int]: raise NotImplementedError


class WindowsPty(PtyBase):
    def __init__(self, shell: str, rows: int, cols: int):
        from winpty import PtyProcess
        self.proc = PtyProcess.spawn(shell, dimensions=(rows, cols))

    def write(self, data: bytes) -> None:
        try:
            self.proc.write(data.decode("utf-8", errors="replace"))
        except Exception:
            pass

    def read(self) -> Optional[bytes]:
        try:
            chunk = self.proc.read(8192)
            if chunk is None:
                return None
            return chunk.encode("utf-8", errors="replace")
        except EOFError:
            return None
        except Exception:
            return b""

    def resize(self, rows: int, cols: int) -> None:
        try:
            self.proc.setwinsize(rows, cols)
        except Exception:
            pass

    def close(self) -> None:
        try: self.proc.terminate(force=True)
        except Exception: pass

    def isalive(self) -> bool:
        try: return self.proc.isalive()
        except Exception: return False

    @property
    def exitcode(self) -> Optional[int]:
        try: return self.proc.exitstatus
        except Exception: return None


class UnixPty(PtyBase):
    def __init__(self, shell: str, rows: int, cols: int):
        import pty, fcntl, struct, termios
        argv = shell.split()
        pid, fd = pty.fork()
        if pid == 0:
            os.execvp(argv[0], argv)
        self.pid = pid
        self.fd = fd
        self._alive = True
        self._exit = None
        winsize = struct.pack("HHHH", rows, cols, 0, 0)
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

    def write(self, data: bytes) -> None:
        try: os.write(self.fd, data)
        except OSError: pass

    def read(self) -> Optional[bytes]:
        import select
        try:
            r, _, _ = select.select([self.fd], [], [], 0.05)
            if not r: return b""
            chunk = os.read(self.fd, 8192)
            if not chunk:
                self._alive = False
                return None
            return chunk
        except OSError:
            self._alive = False
            return None

    def resize(self, rows: int, cols: int) -> None:
        import fcntl, struct, termios
        try:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)
        except OSError: pass

    def close(self) -> None:
        try: os.close(self.fd)
        except OSError: pass
        try:
            os.kill(self.pid, signal.SIGTERM)
            _, status = os.waitpid(self.pid, 0)
            self._exit = os.WEXITSTATUS(status) if os.WIFEXITED(status) else -1
        except OSError: pass
        self._alive = False

    def isalive(self) -> bool: return self._alive
    @property
    def exitcode(self) -> Optional[int]: return self._exit


def make_pty(shell: str, rows: int, cols: int) -> PtyBase:
    return WindowsPty(shell, rows, cols) if IS_WIN else UnixPty(shell, rows, cols)


def default_shell() -> str:
    if IS_WIN:
        return os.environ.get("COMSPEC") or "C:\\Windows\\System32\\cmd.exe"
    return os.environ.get("SHELL") or "/bin/bash"


# ─────────────────────────────────────────────────────────────────────
# WS session
# ─────────────────────────────────────────────────────────────────────

async def session(ws, shell: str):
    print(f"[session] new client from {ws.remote_address}")
    pty = make_pty(shell, 24, 80)
    loop = asyncio.get_running_loop()

    stopping = asyncio.Event()

    # Reader thread: PTY → ws.send
    queue: asyncio.Queue = asyncio.Queue()

    def reader_thread():
        while not stopping.is_set():
            chunk = pty.read()
            if chunk is None:
                loop.call_soon_threadsafe(queue.put_nowait, None)
                return
            if chunk:
                loop.call_soon_threadsafe(queue.put_nowait, chunk)
        # done

    t = threading.Thread(target=reader_thread, daemon=True)
    t.start()

    async def pump_out():
        while True:
            item = await queue.get()
            if item is None:
                await ws.send(json.dumps({"type": "exit", "code": pty.exitcode or 0}))
                return
            try:
                await ws.send(item)
            except websockets.ConnectionClosed:
                return

    async def pump_in():
        try:
            async for msg in ws:
                if isinstance(msg, bytes):
                    pty.write(msg)
                    continue
                try:
                    obj = json.loads(msg)
                except Exception:
                    continue
                t = obj.get("type")
                if t == "input":
                    data = obj.get("data", "")
                    if isinstance(data, str):
                        pty.write(data.encode("utf-8", errors="replace"))
                elif t == "resize":
                    pty.resize(int(obj.get("rows", 24)), int(obj.get("cols", 80)))
        finally:
            stopping.set()
            pty.close()

    await asyncio.gather(pump_out(), pump_in())
    print(f"[session] closed; exitcode={pty.exitcode}")


async def amain(args):
    async def handler(ws):
        try:
            await session(ws, args.shell)
        except Exception as e:
            print(f"[session] error: {e}", file=sys.stderr)

    print(f"vt-term bridge listening on ws://{args.host}:{args.port}")
    print(f"  shell  = {args.shell}")
    print(f"  open   = file:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'index.html')).replace(os.sep, '/')}")
    async with websockets.serve(handler, args.host, args.port, max_size=2**24):
        await asyncio.Future()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=7681)
    p.add_argument("--shell", default=default_shell())
    args = p.parse_args()
    try:
        asyncio.run(amain(args))
    except KeyboardInterrupt:
        print("\n[bye]")


if __name__ == "__main__":
    main()
