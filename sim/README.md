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

## Documentation

- [Reference.md](Reference.md) — Quick reference of all keys and key combinations and what they do, for users.
- [VimBehavior.md](VimBehavior.md) — Comprehensive technical specification of Vim behavior, detailed enough to derive a correct implementation from.

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

## Known Limitations

- **`Ctrl-W` (browser intercepts)** — The simulator fully implements all
  `Ctrl-W` commands (window splits, navigation, insert-mode word delete, shell
  word delete), but desktop browsers reserve `Ctrl-W` as "close tab" and
  intercept the keystroke before JavaScript can capture it. Calling
  `preventDefault()` has no effect on this browser-reserved shortcut.
  **Workaround: use `Ctrl-Q` instead** — the simulator maps `Ctrl-Q` → `Ctrl-W`
  so every `Ctrl-W` command works via `Ctrl-Q` (e.g. `Ctrl-Q s` to split,
  `Ctrl-Q w` to cycle windows). On touch devices the virtual keyboard's Ctrl
  modifier also works fine because it synthesizes the key event in JavaScript,
  bypassing the browser.

- **`Ctrl-Z` (suspend)** — Not implemented. In real Vim on Unix, `Ctrl-Z` sends
  SIGTSTP to suspend the editor, and `fg` resumes it. This project was developed
  on Windows where ConPTY does not support Unix job control signals, so we were
  unable to generate ground truth captures for this feature. The simulator
  currently ignores `Ctrl-Z`. A future effort on macOS or Linux could capture
  the suspend/resume behavior and add support. See also: lesson 234 in the
  curriculum, which explains the concept but demos `:!` as the cross-platform
  alternative.

## Resetting the Filesystem

The simulator persists files in `localStorage`. To clear all saved files and
restore the default seed content (welcome.md, demo.py, notes.txt), add `?reset`
to the URL:

```
index.html?reset
```

The flag is automatically stripped from the URL after clearing, so a subsequent
refresh won't re-clear.
