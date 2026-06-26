# Sixel test fixtures

Real-world sixel files used to exercise the decoder.  Sourced from
[csdvrx/sixel-testsuite](https://github.com/csdvrx/sixel-testsuite),
which collects test images for xterm, mlterm, foot, wezterm and other
sixel-capable terminals.

| file                  | size      | what it is                                          |
| --------------------- | --------- | --------------------------------------------------- |
| `minimal-sixel.six`   |   86 B    | 14×7, two colors — smallest valid sixel             |
| `go.six`              |   96 B    | 64×6 single-band gradient                            |
| `3-sixels.six`        |  255 B    | 8-color test pattern, three bands tall              |
| `text-test.sixel`     | 5.3 KB    | 64×64 image with raster attributes                  |
| `me.six`              | 4.4 KB    | 160×160 grayscale portrait                          |
| `snake.six`           |  348 KB   | 600×450 full-color libsixel-quantized photo         |

Each file is the complete `ESC P … ESC \` envelope produced by tools
like `img2sixel`, so they can be `cat`'d straight to a sixel-capable
terminal or fed verbatim to `term.write()` in the demo page.

The unit tests in `test/sixel_fixtures.test.js` verify the decoder
parses each one without errors and reports the correct image
dimensions / pixel count / palette size.  The Playwright tests in
`test/demo.pw.test.js` go end-to-end: load the fixture in the demo
page, verify the canvas contains the expected colors.
