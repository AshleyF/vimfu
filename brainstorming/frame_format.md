# Frame Format Specification

The **Frame** is the intermediate data structure for a terminal screenshot.
It captures everything needed to reproduce the visual appearance of a
terminal screen at a single point in time.

## JSON Schema

```json
{
  "rows": 20,
  "cols": 40,
  "cursor": { "row": 5, "col": 12, "visible": true },
  "defaultFg": "d4d4d4",
  "defaultBg": "000000",
  "lines": [
    {
      "text": "power 99                                ",
      "runs": [
        { "n": 6, "fg": "d4d4d4", "bg": "000000" },
        { "n": 2, "fg": "ff8700", "bg": "000000", "b": true },
        { "n": 32, "fg": "d4d4d4", "bg": "000000" }
      ]
    },
    "..."
  ]
}
```

## Field reference

### Top level

| Field       | Type     | Description                              |
|------------ |--------- |------------------------------------------|
| `rows`      | int      | Terminal height                          |
| `cols`      | int      | Terminal width                           |
| `cursor`    | object   | Cursor position and visibility           |
| `defaultFg` | string   | Default foreground color (6-digit hex, no `#`) |
| `defaultBg` | string   | Default background color                 |
| `lines`     | array    | One entry per row (length = `rows`)      |

### Line

| Field  | Type   | Description                                    |
|------- |------- |------------------------------------------------|
| `text` | string | Plain characters, padded to `cols` with spaces |
| `runs` | array  | Styling runs (lengths must sum to `cols`)       |

### Run

| Field | Type   | Required | Description                           |
|------ |------- |--------- |---------------------------------------|
| `n`   | int    | yes      | Number of consecutive cells           |
| `fg`  | string | yes      | Foreground color (6-digit hex)        |
| `bg`  | string | yes      | Background color (6-digit hex)        |
| `b`   | bool   | no       | Bold                                  |
| `i`   | bool   | no       | Italic                                |
| `u`   | bool   | no       | Underline                             |
| `r`   | bool   | no       | Reverse (already resolved into fg/bg) |
| `s`   | bool   | no       | Strikethrough                         |

**Note**: The `fg` and `bg` values are *resolved* — `"default"` has been
replaced with the actual hex color, `"reverse"` has been applied (fg/bg
swapped), and named colors have been converted to hex. Renderers never
need to interpret terminal semantics — just draw the colors.

## Compact variant

For maximum compactness, use an array instead of an object for runs:

```json
"runs": [[6,"d4d4d4","000000"],[2,"ff8700","000000","b"],[32,"d4d4d4","000000"]]
```

Where the optional 4th element is a flags string (`"bius"` etc.).

## Lesson file (sequence of frames with narration)

A full lesson for book rendering would be:

```json
{
  "title": "Repeat Last Change",
  "number": 71,
  "sections": [
    { "type": "say", "text": "The dot command is the most powerful key in Vim." },
    { "type": "say", "text": "Press dot to repeat your last change." },
    { "type": "keys", "keys": "dd", "overlay": "delete line" },
    { "type": "frame", "frame": { "rows": 20, "cols": 40, "..." : "..." } },
    { "type": "say", "text": "Now press dot to delete the next line too." },
    { "type": "keys", "keys": ".", "overlay": "repeat" },
    { "type": "frame", "frame": { "..." : "..." } }
  ]
}
```

This is what a renderer reads to produce a book page.

## Generating frames from pyte

```python
def capture_frame(screen, default_fg="d4d4d4", default_bg="000000"):
    """Capture the current pyte Screen as a Frame dict."""
    lines = []
    for row in range(screen.lines):
        chars = []
        runs = []
        prev = None  # (fg, bg, flags)
        run_len = 0

        for col in range(screen.columns):
            cell = screen.buffer[row][col]
            chars.append(cell.data if cell.data else " ")

            fg = resolve_color(cell.fg, cell.bold, True, default_fg)
            bg = resolve_color(cell.bg, cell.bold, False, default_bg)

            if cell.reverse:
                fg, bg = bg, fg

            flags = ""
            if cell.bold: flags += "b"
            if cell.italics: flags += "i"
            if cell.underscore: flags += "u"
            if cell.strikethrough: flags += "s"

            key = (fg, bg, flags)
            if key == prev:
                run_len += 1
            else:
                if prev:
                    runs.append(make_run(run_len, *prev))
                prev = key
                run_len = 1

        if prev:
            runs.append(make_run(run_len, *prev))

        lines.append({
            "text": "".join(chars),
            "runs": runs
        })

    return {
        "rows": screen.lines,
        "cols": screen.columns,
        "cursor": {
            "row": screen.cursor.y,
            "col": screen.cursor.x,
            "visible": not screen.cursor.hidden
        },
        "defaultFg": default_fg,
        "defaultBg": default_bg,
        "lines": lines
    }

def make_run(n, fg, bg, flags):
    run = {"n": n, "fg": fg, "bg": bg}
    if "b" in flags: run["b"] = True
    if "i" in flags: run["i"] = True
    if "u" in flags: run["u"] = True
    if "s" in flags: run["s"] = True
    return run
```
