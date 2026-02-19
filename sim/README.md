# VimFu Simulator

A web-based Vim simulator that runs entirely client-side. Built to accompany
the VimFu book and video series.

## Architecture

```
Model (src/engine.js)
  ├── Buffer        – text content as array of lines
  ├── Cursor        – row, col position
  ├── Mode          – normal, insert
  └── Screen        – produces Frame dicts matching the project's frame format

Controller (src/controller.js)
  └── Accepts DOM key events → dispatches to engine

View (src/renderer.js)
  └── Takes a Frame dict → renders to a <canvas> or DOM grid
```

## Testing

Tests compare the simulator's screen output against actual Neovim running
via the ShellPilot PTY infrastructure. This ensures pixel-perfect fidelity
with real Vim behaviour.

```bash
npm test              # unit tests (Jest)
npm run test:compare  # full ground-truth comparison against Neovim
```

## Running

Open `index.html` in a browser. No server required.
