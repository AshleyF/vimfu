# vt-term bridge

Tiny WebSocket↔PTY proxy.  Lets the canvas terminal talk to a real
shell on your local machine.

## Install

```
pip install -r requirements.txt
```

## Run

```
python proxy.py                              # bind 127.0.0.1:7681, default shell
python proxy.py --shell bash --port 9000
python proxy.py --shell C:\Windows\System32\cmd.exe
```

Then open `terminal/index.html` in a browser, type `ws://localhost:7681`
in the URL box, and click **Connect**.

## Protocol

Client → server (JSON text frames):

| message                                          | meaning              |
| ------------------------------------------------ | -------------------- |
| `{"type":"input","data":"ls\r"}`                 | write to PTY         |
| `{"type":"resize","rows":24,"cols":80}`          | TIOCSWINSZ           |

Server → client:

| message                          | meaning                |
| -------------------------------- | ---------------------- |
| binary frames                    | raw PTY output bytes   |
| `{"type":"exit","code":0}`       | child exited           |

## Cross-platform

- **Windows** — uses `pywinpty` (ConPTY).
- **macOS / Linux** — uses stdlib `pty.fork()`.

Same proxy script, no platform-specific wiring elsewhere.
