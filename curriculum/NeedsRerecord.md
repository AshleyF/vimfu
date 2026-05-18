# Videos That Need to Be Re-recorded

This file lists video recordings that completed "successfully" but are silently broken, along with the reason. Re-run each lesson, then remove its entry.

## Oh-My-Zsh update prompt at recording start

When Oh-My-Zsh's auto-update timer fires, it injects a `[oh-my-zsh] Would you like to update? [Y/n]` prompt at the top of the terminal *before* the recording starts. The prompt's `[Y/n]` reader eats the first keystrokes the script sends, so the demo never runs as authored. The recording then completes silently with a broken video.

This was found by scanning all logs under `shellpilot/videos/` for `[oh-my-zsh]` + `would you like to (update|check for updates)`. `shellpilot/viewer.py:start_recording` now hard-fails on this so future recordings can't slip through — see `curriculum/Instructions.md` under *Oh-My-Zsh update prompt corrupts recordings*.

### Affected lessons

| Lesson slug                  | Log file                                                           |
| ---------------------------- | ------------------------------------------------------------------ |
| `0530a_send_literal_prefix`  | `shellpilot/videos/0530a_send_literal_prefix/0530a_send_literal_prefix.log` |
| `0530b_auto_unzoom`          | `shellpilot/videos/0530b_auto_unzoom/0530b_auto_unzoom.log`        |
| `0530c_pane_auto_close`      | `shellpilot/videos/0530c_pane_auto_close/0530c_pane_auto_close.log` |

### To re-record

1. Run `omz update` in a regular shell (or `zsh -ic 'omz update'`) so the prompt is gone.
2. Re-run each lesson script. Shellpilot will now raise `RuntimeError` at recording start if Oh-My-Zsh is still asking — so a clean run is your signal that the recording is good.
3. Delete the entry from this file once the lesson is re-recorded and verified.
