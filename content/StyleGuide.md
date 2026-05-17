# VimFu Style Guide

This guide governs how Vim keys, key sequences, Ex commands, placeholders,
and register names are written throughout the book, website, videos, and
shorts. The rules apply to topic titles, headings, body prose, table
cells, captions, the index, the table of contents, and headers/footers.

The single most important rule:

> **Key presses are never written as plain text.** Any time a glyph in
> the prose represents a key you would press, it must be marked up — as
> a boxed key cap, a monospace token, or one of the other forms below.

---

## When to use what

### 1. Boxed key caps — for keys you actually press

A boxed cap (a "pill" in code) means "press this physical key." Use it
for:

- **Single key presses.** Examples: <kbd>j</kbd>, <kbd>Esc</kbd>,
  <kbd>Tab</kbd>, <kbd>0</kbd>, <kbd>$</kbd>.
- **Sequences of presses that don't spell a word.** Render each key
  as its own pill, adjacent.
  - `dw` (delete word) → <kbd>d</kbd><kbd>w</kbd>
  - `ci"` (change inside quotes) → <kbd>c</kbd><kbd>i</kbd><kbd>"</kbd>
  - `hjkl` → <kbd>h</kbd><kbd>j</kbd><kbd>k</kbd><kbd>l</kbd>
  - `gg`, `gU`, `:wq` → each character its own pill
- **Listed sets of keys.** Even when prose says "the keys h, j, k, l,"
  each one gets a pill. *Never* run `hjkl` together as plaintext.
- **Modifier chords.** A modifier held with another key is one
  press, so it goes in *one* pill that contains the chord:
  <kbd>Ctrl-W</kbd>, <kbd>Ctrl-A</kbd>, <kbd>Alt-Enter</kbd>. Not
  <kbd>Ctrl</kbd><kbd>W</kbd>.
- **Named special keys.** <kbd>Esc</kbd>, <kbd>Enter</kbd>,
  <kbd>Backspace</kbd>, <kbd>Tab</kbd>, <kbd>Space</kbd>,
  <kbd>Leader</kbd>, <kbd>F2</kbd>.

Markup in JSON: `{key:h}{key:j}{key:k}{key:l}`, or the shorthand
`{key:hjkl}` (the renderer splits multi-letter ASCII runs into
per-character pills automatically — see `_split_key_for_wrap` in
`render_latex.py`).

### 2. Monospace (no box) — for commands, placeholders, and named things

Use `\code{...}` / `<code>...</code>` / Markdown backticks for anything
that is *not* "press this key" but *is* a literal string of characters
the reader will type, see, or refer to:

- **Ex commands**, including abbreviated forms.
  - `:set hlsearch`, `:nohlsearch`, `:noh`, `:wq`, `:%s/foo/bar/g`,
    `:e file.txt`. Even though `:noh` looks like a "key sequence", it
    is an *abbreviation* for `:nohlsearch` — it spells something. That
    makes it a command, not a series of key presses, so it goes in
    monospace, not boxed.
- **Operator/motion placeholders.** When describing the grammar
  generically, the *whole template* — placeholder word, braces, and
  all — goes in monospace.
  - `r{c}` — replace with `{c}`
  - `c{motion}` — change over `{motion}`
  - `"{r}p` — paste from register `{r}`
- **Named registers when referred to as registers** (not as the
  sequence you'd type to use them). `""`, `"/`, `":`, `"+`, `"_`,
  `"0`, `"a`. The double quote here is part of the register's *name*,
  not a key you press in isolation. When the prose is talking *about*
  the register, monospace.
  - "The unnamed register, `""`, holds the most recent delete or
    yank."
  - But when describing actually using one: "Paste from the system
    clipboard with <kbd>"</kbd><kbd>+</kbd><kbd>p</kbd>" — each key
    its own pill.
- **Option names and settings:** `hlsearch`, `expandtab`,
  `relativenumber`, `'shiftwidth'` (the option name itself).
- **File names and paths:** `~/.vimrc`, `init.lua`,
  `~/.config/nvim/`.
- **Family names that aren't a literal key sequence.** When the prose
  refers to "the `g` family", "the `z` family", "the `Ctrl-W` family",
  "the `[` family" — the family *name* is monospace because we are
  using it as a noun (the name of the group), not telling the reader
  to press anything yet. *Inside* an example that uses one of those
  keys, it becomes a pill again.
- **Lower-case Unix command / program names referred to as commands.**
  `vi`, `ed`, `ex`, `nvim`, `less`, `bash`, `zsh`, `tmux`, `git`. They
  are command names you would type at a shell, so they take monospace
  even when the surrounding prose is talking about the program as a
  whole (e.g. "modal editing did not start with `vi`, it started with
  `ed`"). Capitalised proper-noun forms like *Vim*, *Neovim*, *Emacs*
  are normal prose.

Markup in JSON: standard Markdown backticks — `` `:set hlsearch` ``,
`` `g` family ``, `` `c{motion}` ``.

### 3. Pure prose — never for keys

If a glyph or short word is referring to a key, command, register,
option, or path, it must be in *one of the two forms above*. Plain
text like "press hjkl" or "use the g family" is not allowed.

---

## Why both forms?

Pills tell the reader "do this with your fingers." They are visually
distinct, scannable, and read at a glance even inside long prose
paragraphs. Code/monospace tells the reader "this is a name you will
see or type in a more literal sense" — a command at the `:` prompt,
the spelling of an option, the path to a config file.

The line between them is the line between *kinesthetic* and
*lexical*: pills are about pressing keys; monospace is about
identifying things by name or by literal spelling.

---

## Specific consequences

### Topic / chapter titles

The book uses **pills in the body** but **monospace in the TOC,
headers, and PDF bookmarks** (TikZ pills can't survive into those
contexts). The renderer handles this automatically: write the title
once using `{key:...}` markup, and the body shows pills, the TOC
shows monospace.

- ✅ `"title": "Move with {key:hjkl}"` — body: `Move with` + 4 pills;
  TOC: `Move with hjkl` (monospace).
- ❌ `"title": "Move with hjkl"` — body and TOC both render plain
  text. Wrong everywhere.

### Headings inside topics (`{"type": "heading", ...}`)

Same rule: use `{key:...}` markup, get pills.

- ✅ `"text": "Why {key:hjkl}?"`
- ❌ `"text": "Why hjkl?"`

### Table cells, captions, narration

`{key:...}` and Markdown backticks both work and render the same way
in all of these. Use whichever makes the source most readable.

### The index

Every distinct key in the prose gets indexed under "Keys" by default.
This is built from `{key:...}` markup. Code-style monospace tokens
(`` `:set hlsearch` ``) are *not* indexed — they're commands, not
keys.

If a topic has a `keys: [...]` array on its frontmatter, those keys
are also indexed at the chapter heading (separately from the keys in
the prose).

### Modifier chords in JSON

Write them with a hyphen inside `{key:...}`: `{key:Ctrl-W}`,
`{key:Alt-Enter}`. The renderer recognises the chord and emits one
pill — *not* per-character splitting.

### Letter sequences

`{key:hjkl}` → four pills (split). `{key:gg}` → two pills. `{key:wq}`
→ two pills. The renderer splits multi-letter pure-letter runs
because those represent independent presses.

To force a *single* pill containing multiple letters (rare — almost
always wrong), use a name the renderer recognises as one key:
`{key:Esc}`, `{key:Tab}`, etc.

---

## Audit checklist

When editing or reviewing book / website content:

1. Search for bare key tokens in prose: `hjkl`, `gg`, `wq`, `dw`,
   single-character key names where the context is "press this."
   They should all be `{key:...}` or backtick'd, never plain.
2. Topic and heading titles: same rule. If the title mentions a key,
   wrap it.
3. The same key may be a *pill* in one sentence (instruction) and
   *monospace* in another (name of a family / register). Both are
   correct in their own contexts.
4. Don't put multiple keys inside one pill unless they form a real
   chord with a modifier. <kbd>dw</kbd> as one pill is wrong;
   <kbd>d</kbd><kbd>w</kbd> as two pills is right;
   <kbd>Ctrl-W</kbd> as one pill is right.
5. Placeholder templates like `r{c}` are *one* monospace token,
   including the braces and placeholder word — they're a grammar
   fragment, not key presses.

---

## Mode names

Mode names — *normal mode*, *insert mode*, *visual mode*, *visual-line
mode*, *visual-block mode*, *command-line mode*, *replace mode*,
*operator-pending mode*, *terminal mode*, *select mode* — are always
**lowercase italic**, even mid-sentence. They are common-noun terms,
not proper nouns. The italic distinguishes the term from prose without
the visual shout of bold or all-caps.

- ✅ "Press {key:i} to enter *insert mode*."
- ✅ "*Normal mode* is the default." (sentence-start; capital N stays
  inside the italic span)
- ❌ "Press i to enter Insert Mode." (capitalised + roman)
- ❌ "Press i to enter **insert mode**." (bold)
- ❌ "Press i to enter INSERT MODE." (all-caps)

Markup in JSON: standard Markdown italic, `*insert mode*`.

### Punctuation after italic

When italic text is followed by punctuation (`,` `.` `:` `;` `!` `?`
`—`), the punctuation goes **inside** the italic span. This is a
standard typographic rule that fixes the awkward kerning between an
italic glyph and an upright punctuation mark.

- ✅ `*insert mode:*` keys you type appear as text.
- ❌ `*insert mode*:` keys you type appear as text. (kerning gap)

This applies to *any* italic span, not just mode names.

---

## Key sequence spacing

Adjacent key pills that form one sequence ({key:d}{key:d},
{key:c}{key:i}{key:"}, {key:g}{key:g}) must have **no space** between
them in the source. Literal spaces inside the JSON between `{key:...}`
tokens render as visible gaps and are wrong.

- ✅ `{key:d}{key:d}` — two pills, touching.
- ❌ `{key:d} {key:d}` — two pills with a literal space between.

Exception: when prose actually lists keys ("the keys h, j, k, l"),
commas and spaces between the pills are part of the prose, not the
sequence, and are fine.

---

## Placeholders in grammar templates

When showing a generic grammar/formula, write the *entire* template as
a single monospace token (backticks), with curly-braced parameter
names inside it.

- ✅ `` `f{c}` ``, `` `t{c}` ``, `` `r{c}` ``, `` `c{motion}` `` —
  the placeholder word and braces are *part of* the template.
- ✅ `` `/{pattern}` ``, `` `?{pattern}` ``, `` `{n}G` `` — counts and
  patterns also use the same `{name}` form.
- ❌ `{key:f}{c}` — mixing a pill with a stray `{c}` in prose. The
  reader can't tell whether `{c}` is monospace, a literal brace, or a
  pill.
- ❌ `{key:/}pattern` — same problem. Use `` `/{pattern}` ``.

Multi-form grammar formulas (Backus-Naur style) go in a fenced code
block:

```
[count] ["reg] operator [count] motion
```

Brackets are conventional shorthand for *optional*; curly braces are
parameter placeholders.

---

## Backus-Naur "or" alternatives

When a command has two equivalent forms (e.g. doubled-operator
shortcuts), pick *one* — the shorter or more common one — and don't
clutter prose with both.

- ✅ "{key:g}{key:U}{key:U} uppercases the current line."
- ❌ "{key:g}{key:U}{key:g}{key:U} (or {key:g}{key:U}{key:U})
  uppercases the current line."

If both forms genuinely matter (e.g. a synonym table or reference
appendix), list them in a dedicated table. Don't inline alternatives
in narrative prose.

---

## No gray background on monospace

Inline `\code{}` and the `\codeblock` environment render plain
monospace without a colored background. Reasons: short punctuation
glyphs (hyphens, slashes) sit lower in the box and look like the
background is "shrinking"; literal spaces inside monospace runs don't
get the background at all, producing visible gaps; and gray pillows
clutter the page when the text already differs by font.

Keep monospace purely typographic: same color as body text, no fill,
no border. The font shift alone is enough signal.
