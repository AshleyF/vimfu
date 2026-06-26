/**
 * Thin client wrapper for the WebSocket↔PTY bridge.
 *
 * Wire format (text + binary):
 *   - Binary frames carry raw PTY output bytes (host → client).
 *   - Text frames may carry JSON control messages:
 *       {"type":"title","value":"..."}     (currently unused; server-driven)
 *       {"type":"exit","code":0}
 *
 *   Client → server is always JSON:
 *       {"type":"input","data":"..."}
 *       {"type":"resize","rows":24,"cols":80}
 *
 * The wrapper auto-reconnects on close unless `close()` is called.
 */

export class TerminalSocket {
  constructor(url, { autoReconnect = true } = {}) {
    this.url = url;
    this.autoReconnect = autoReconnect;
    this.onOpen = null;
    this.onClose = null;
    this.onData = null;     // (Uint8Array) =>
    this.onExit = null;     // (code) =>
    this._closed = false;
    this._connect();
  }

  _connect() {
    this.ws = new WebSocket(this.url);
    this.ws.binaryType = 'arraybuffer';

    this.ws.addEventListener('open', () => {
      if (this.onOpen) this.onOpen();
    });

    this.ws.addEventListener('message', (ev) => {
      if (typeof ev.data === 'string') {
        try {
          const msg = JSON.parse(ev.data);
          if (msg.type === 'exit' && this.onExit) this.onExit(msg.code);
        } catch (_) { /* ignore */ }
      } else {
        if (this.onData) this.onData(new Uint8Array(ev.data));
      }
    });

    this.ws.addEventListener('close', () => {
      if (this.onClose) this.onClose();
      if (this.autoReconnect && !this._closed) {
        setTimeout(() => this._connect(), 1000);
      }
    });
  }

  send(data) {
    if (this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: 'input', data }));
  }

  resize(rows, cols) {
    if (this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ type: 'resize', rows, cols }));
  }

  close() {
    this._closed = true;
    try { this.ws.close(); } catch (_) {}
  }
}
