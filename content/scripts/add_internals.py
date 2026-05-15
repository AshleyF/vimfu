"""Bulk-add programmer-oriented `internals` callouts to topic JSONs.

Reads CALLOUTS list (path, title, text); for each, opens the topic JSON,
skips if a block with the same title already exists, otherwise appends a
new internals block before any trailing `qr`/`buy-prompt` block (so the
callout sits in the body, not after the call-to-action).

Idempotent — safe to re-run.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def add_internals(rel_path: str, title: str, text: str) -> str:
    p = ROOT / rel_path
    if not p.exists():
        return f"SKIP (no file): {rel_path}"
    j = json.loads(p.read_text(encoding="utf-8"))
    blocks = j.get("blocks", [])
    for b in blocks:
        if b.get("type") == "internals" and b.get("title", "").strip().lower() == title.strip().lower():
            return f"skip dup : {rel_path} :: {title}"

    new_block = {"type": "internals", "title": title, "text": text}
    insert_at = len(blocks)
    while insert_at > 0 and blocks[insert_at - 1].get("type") in ("qr", "buy-prompt"):
        insert_at -= 1
    blocks.insert(insert_at, new_block)
    j["blocks"] = blocks
    p.write_text(json.dumps(j, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return f"ADD      : {rel_path} :: {title}"


CALLOUTS = [
    ("parts/02-survival/01-open-save-quit.json",
     "Buffers carry a dirty bit",
     "Saving and quitting aren't symmetric. The buffer carries a `modified` flag that flips on the first edit and clears on a successful write. {key::q} consults that flag and refuses to exit (E37) unless you force it with {key:!}; {key::x} is a conditional `write-then-quit` that skips the write when the flag is already clear. {key:Z}{key:Z} is the same conditional path as {key::x}; {key:Z}{key:Q} is the unconditional discard path of {key::q}{key:!}. Internally these are four code paths, not four shortcuts."),

    ("parts/02-survival/02-insert-and-back.json",
     "Why Escape backs the cursor up one column",
     "Leaving insert mode is not a pure mode flip. The cursor lives in a virtual column while inserting (it can sit one cell past the last character), but normal mode requires the cursor to land on a real character. So Escape clamps the column back by one when you're past the line end. That single rule is why {key:a} then Esc leaves you under the character you appended past, and why {key:i}-Esc-{key:i} doesn't drift sideways."),

    ("parts/02-survival/03-undo-redo.json",
     "Undo units are command-shaped, not keystroke-shaped",
     "The undo system batches edits at command boundaries, not per keystroke. One normal-mode command — including a complete insert session from {key:i} through Escape — collapses into a single undo unit. That's why hitting {key:u} after typing a paragraph rips out the whole paragraph at once: the editor only inserted one undo boundary, at the moment you returned to normal mode. Internally undo is a tree of state snapshots; redo is a forward walk through that tree."),

    ("parts/03-basic-editing/01-insert-variants.json",
     "Insert entries are cursor-placement transforms",
     "{key:i}, {key:a}, {key:I}, {key:A}, {key:o}, {key:O}, {key:s}, {key:S}, {key:c} all converge into the same insert-mode state machine. What differs is a single function that decides where the insert cursor lands and whether to splice in a new line first. Treat them as `(landing-rule, [pre-edit])` pairs, not nine separate commands. Once you see this, learning a new insert-entry key reduces to memorizing its landing rule."),

    ("parts/03-basic-editing/02-word-motions.json",
     "Word motions are a token-class scanner",
     "{key:w}, {key:b}, {key:e}, {key:g}{key:e} aren't regex-driven; they classify each character into one of three token classes — word, punctuation, whitespace — and step through class boundaries. Empty lines count as a hard boundary regardless of class. The capitalized variants ({key:W}, {key:B}, {key:E}) collapse word and punctuation into a single class, so they only stop at whitespace. The implementation is one scanner with a swappable classifier."),

    ("parts/03-basic-editing/03-line-motions.json",
     "Blank vs whitespace-only is a real distinction",
     "First-non-blank motions ({key:^}, {key:_}, {key:+}, {key:-}) and screen motions ({key:H}, {key:M}, {key:L}) all hinge on two predicates the editor evaluates per line: length is zero (blank) and first non-whitespace column. A whitespace-only line is not blank — it counts as having content for paragraph motions but yields a no-op for {key:^}. Holding both predicates straight is the only way these motions feel consistent."),

    ("parts/03-basic-editing/04-file-motions.json",
     "Cursor positions are clamped per mode",
     "Normal mode pins the cursor to a real character; insert and replace allow the extra one-past-end virtual column. So a motion that lands at line end resolves differently depending on which mode you're in. The buffer doesn't store a cursor — the window does, and the window applies the mode-dependent clamp every time it's drawn."),

    ("parts/03-basic-editing/05-delete.json",
     "Delete has two cursor-landing rules",
     "Charwise delete leaves the cursor at the start of the deleted range. Linewise delete moves the cursor to the first non-blank of whatever line replaces the deletion. The post-delete landing is keyed off the deleted text's type tag ({key:d}{key:w} is charwise, {key:d}{key:d} is linewise), not off the operator key. That's why {key:d}{key:j} (linewise: deletes two lines) lands you on first-non-blank, but {key:d}{key:l} doesn't."),

    ("parts/03-basic-editing/06-change.json",
     "Change is delete-then-insert, with one historical quirk",
     "{key:c} is not a primitive: it runs the delete operator, then enters insert mode at the landing position. The famous {key:c}{key:w} = {key:c}{key:e} quirk falls out of this — change adjusts the motion's endpoint to drop the trailing whitespace so the inserted text doesn't push it. Knowing change is a composition lets you predict its behavior with any motion you've already learned."),

    ("parts/03-basic-editing/07-yank-put.json",
     "Yank produces a typed snapshot, not raw text",
     "A yank captures both payload and type (`char`, `line`, or `block`). Paste reads that type tag and chooses placement: charwise pastes after the cursor on the same line; linewise pastes on a new line below; blockwise pastes as a rectangle. The register is a tiny tagged-union struct, not a string. Mismatch the type and {key:p} appears to misbehave — it's just honoring the tag you stored."),

    ("parts/03-basic-editing/08-replace-char.json",
     "Replace mode keeps a shadow buffer",
     "{key:R} can't be implemented as 'overwrite forward' alone, because Backspace must restore each original character. So replace mode tracks a small shadow region — the line as it was at entry — and the Backspace handler diffs against that shadow to put back what you replaced. The shadow also clamps how far Backspace can go: you can never erase past your entry point."),

    ("parts/04-search-find/01-pattern.json",
     "Search is a global state machine",
     "{key:/} and {key:?} don't just jump — they write the current search pattern into a process-wide slot (also reachable as the {key:\"}{key:/} register). {key:n} and {key:N} are then re-applications of that stored pattern with direction baked in. That's why {key:c}{key:g}{key:n}, {key:*}, and the substitute command's empty pattern all work: they read or update the same shared state."),

    ("parts/04-search-find/02-word.json",
     "{key:*} synthesizes a regex from the cursor token",
     "Word search is a tiny code generator. It tokenizes the text under the cursor, wraps it in word-boundary anchors (`\\<...\\>`), and writes the result into the search-pattern slot. {key:#} is the same generator with reversed initial direction. The `g`-prefixed variants ({key:g}{key:*}, {key:g}{key:#}) drop the boundary anchors. Knowing this, you can predict exactly which token will be selected and why partial matches behave as they do."),

    ("parts/04-search-find/03-find-on-line.json",
     "{key:f}/{key:t} are a single-line cursor with replay memory",
     "Find-on-line never crosses lines, and it remembers the last `(direction, target)` pair it executed. {key:;} replays that pair; {key:,} replays it with direction flipped. So {key:f}{key:t}{key:;}{key:;} jumps to the third `t` on the line. The memory slot is per-window and survives normal-mode commands but is reset by mode changes."),

    ("parts/05-counts/01-counts.json",
     "Count parsing is a tiny lexer with context",
     "Counts aren't a separate argument — they're a prefix accumulated by a small state machine. The first digit must be `1-9` (because `0` is itself a motion to column zero); subsequent digits can include `0`. The accumulated count multiplies with any operator-applied count, so {key:2}{key:d}{key:3}{key:w} deletes six words. Internally it's `count = command_count * motion_count`, both defaulting to one."),

    ("parts/18-visual-modes/01-char-visual.json",
     "Visual mode is anchor + endpoint",
     "Charwise visual mode stores two positions: the anchor (where you pressed {key:v}) and the current cursor. Motions move the cursor; the selection is always the inclusive range between the two. There's no selection object being copied around — the renderer paints whatever sits between anchor and cursor each frame. Operators consume the resolved range and exit back to normal mode."),

    ("parts/18-visual-modes/02-line-block.json",
     "Visual-line mode normalizes to whole rows",
     "Linewise visual ({key:V}) doesn't extend the charwise range to line ends — it replaces both endpoints with `(start_of_line, end_of_line)` every frame. That normalization happens before any operator sees the selection, so paste, delete, indent, and join all get a clean row-span. It's also why moving horizontally in {key:V} mode doesn't appear to do anything: the normalization snaps it back."),

    ("parts/18-visual-modes/03-tricks.json",
     "{key:o} swaps the anchor, not the text",
     "In visual mode, {key:o} (and {key:O} for visual-block) flips which endpoint is the anchor and which is the cursor. The selection contents don't change — only which end your motions extend. After an operator runs, the cursor lands on whichever endpoint was current at consume time, so swapping ends before {key:d} or {key:y} changes where you end up."),

    ("parts/06-dot-repeat/01-repeat.json",
     "Dot replays a change recipe, not keystrokes",
     "{key:.} is not a keyboard macro. The editor records the last change — the operator, its motion or text object, its count, and (for inserts) the typed text — into a small struct. {key:.} re-executes that struct against the current cursor position. Pure motions and visual-only operations don't update the struct, which is why you can move freely between repeats without losing your dot."),

    ("parts/06-dot-repeat/02-with-counts.json",
     "Dot's count overrides the original",
     "Prefix {key:.} with a count and the replay uses your count, not the count baked into the recorded change. Internally the struct stores the original count separately; at replay time, the executor swaps in any new count provided. So `5.` after a single-line change deletes five lines, not one — the change template is reused with a new multiplier."),

    ("parts/06-dot-repeat/03-patterns.json",
     "Insert-mode dot records a transcript",
     "When the recorded change includes an insert session, the editor stores the full transcript of typed characters, newlines, and editing keys ({key:Ctrl-W}, {key:Ctrl-U}, {key:Ctrl-T}) — but not arrow-key cursor moves. That exclusion is deliberate: arrows would make replay depend on positions in the original buffer that don't exist in the new one. Replay re-runs the transcript through the same insert-mode handlers."),

    ("parts/08-wider-motions/01-sentence-paragraph.json",
     "Sentences and paragraphs are pattern-defined",
     "{key:(}, {key:)}, {key:\\{}, {key:\\}} aren't AST-aware — they scan for delimiters: a sentence ends at `.`, `!`, or `?` followed by spaces or end-of-line; a paragraph boundary is a blank line. Both motions are character-class scans, the same machinery as word motions but with different separators. That's why prose with non-standard punctuation sometimes confuses them."),

    ("parts/08-wider-motions/02-percent.json",
     "{key:%} is a depth-counting matcher",
     "{key:%} jumps from a bracket to its match, but the implementation isn't 'find the next bracket' — it scans outward keeping a depth counter. Open brackets increment, close brackets decrement; the match is wherever depth returns to zero. The same matcher backs the bracket text objects ({key:i}{key:(}, {key:a}{key:\\}}) and surround's bracket handling, so they all agree on what 'matching' means."),

    ("parts/10-marks-jumps/04-jumplist.json",
     "The jump list is a bounded ring buffer",
     "Vim records every 'big' jump (search, {key:G}, marks, {key:Ctrl-O} reach) into a per-window history capped at ~100 entries with duplicate suppression on the top. {key:Ctrl-O} walks back through the list; {key:Ctrl-I} (Tab) walks forward. Adding a new jump while in the middle of the history truncates the forward portion — same semantics as a browser back/forward stack."),

    ("parts/10-marks-jumps/05-changelist.json",
     "Change list is parallel to undo, not the same",
     "Every modification stamps the cursor position into a separate change list. {key:g}{key:;} and {key:g}{key:,} navigate it without touching the buffer state. That separation is why 'go to where I last edited' works after you've undone, redone, or jumped away — the list records positions of edits, not snapshots of edits."),

    ("parts/11-transform/01-replace-mode.json",
     "Replace mode is reversible overwrite",
     "{key:R} pushes a session-local stack of `(column, original_char)` tuples. Each typed character pops/replaces forward; each Backspace pops the top and restores the original. The session boundary forbids backspacing past your entry point — the stack is empty there. Exiting via Escape discards the stack but keeps the buffer changes."),

    ("parts/11-transform/02-indent.json",
     "Indent operators are leading-whitespace rewrites",
     "{key:>} and {key:<} are line-transform operators: for each affected line they recompute leading whitespace using `'shiftwidth'` and `'expandtab'`, then rewrite that prefix. After the rewrite, the cursor lands on the first non-blank of the first affected line — a deterministic landing rule that lets you chain {key:>}{key:.}{key:.} reliably."),

    ("parts/11-transform/03-case.json",
     "Case operators preserve motion classification",
     "{key:g}{key:u}, {key:g}{key:U}, and {key:g}{key:~} are character-level transforms, but doubled forms ({key:g}{key:u}{key:u} etc.) flip them linewise. The operator layer must therefore carry the motion's type tag through to the transformer — same tag flow that delete and yank use. This is one place the unified `(start, end, type)` interface really pays off."),

    ("parts/11-transform/04-join.json",
     "{key:J} is a whitespace-normalization pipeline",
     "Plain {key:J} doesn't just delete the newline — it strips leading whitespace from the next line, inserts one space (two after `.`, `!`, `?` if `'joinspaces'` is on, none before `)`), and lands the cursor at the join point. {key:g}{key:J} skips the entire normalization pass and just removes the newline. Two operators, one trivial, one with an opinionated formatter behind it."),

    ("parts/12-registers/01-registers-overview.json",
     "Registers are a typed key-value store",
     "Vim's register file is a `Map<char, RegisterEntry>` where each entry holds `(text, type)`. The keys are characters: lowercase letters, uppercase letters (which append to their lowercase counterpart), digits, and a fistful of special characters. Different command families write to different keys automatically. It's much closer to a multiplexed scratchpad than to a clipboard."),

    ("parts/12-registers/02-unnamed.json",
     "{key:\"}{key:\"} is the last-write bus",
     "Every yank, delete, and change writes the unnamed register in addition to whatever explicit register you named. So even a stray {key:x} can clobber a previous yank. If you want to preserve a yank across a delete, route the delete to the black-hole register: {key:\"}{key:_}{key:d}{key:d}."),

    ("parts/12-registers/03-named.json",
     "Named registers are explicit destinations",
     "Selecting a register with {key:\"}{key:a} routes the next command's output (or input, for paste) through that slot — once. The selection is consumed by the next operator, then resets. You can't 'set' a register persistently in normal mode; you can only direct individual commands at one. Capital letters ({key:\"}{key:A}) append instead of overwrite."),

    ("parts/12-registers/04-numbered.json",
     "Numbered registers split yank from delete history",
     "{key:\"}{key:0} always holds the most recent yank. {key:\"}{key:1} through {key:\"}{key:9} form a queue of the last nine deletes/changes that affected at least one line. New deletes shift the queue; new yanks don't. That separation is why you can yank one thing, delete several others, and still {key:\"}{key:0}{key:p} the original."),

    ("parts/12-registers/05-small-delete.json",
     "{key:\"}{key:-} is the small-cut side channel",
     "Deletes that don't span at least one line and don't specify a register skip the numbered queue entirely and land in {key:\"}{key:-}. The point is to keep the numbered queue full of meaningful chunks; tiny deletes ({key:x}, {key:d}{key:l}) would otherwise flush useful history out of {key:\"}{key:1}–{key:\"}{key:9} immediately."),

    ("parts/12-registers/06-clipboard.json",
     "{key:\"}{key:+} and {key:\"}{key:*} are I/O ports",
     "These registers are not memory — they delegate to the OS clipboard provider (X11 selection, Windows clipboard, macOS pasteboard). Reading them invokes a system call; writing them does too. They can be missing entirely on a build without clipboard support. Treat them as protocol endpoints with potential failure modes."),

    ("parts/12-registers/07-special.json",
     "Special registers are control channels",
     "{key:\"}{key:/} reads/writes the search pattern. {key:\"}{key:=} prompts for a Vim-script expression and yields its result on read. {key:\"}{key:_} discards anything written to it and yields nothing on read. They share the register interface but have nothing in common with regular storage — they're protocol endpoints disguised as registers."),

    ("parts/13-macros/01-record-play.json",
     "Macros are input virtualization",
     "Recording a macro stores the literal keystroke sequence into a register. Playback feeds those keystrokes back through the same input pipeline a real keyboard would feed. Every subsystem — operators, search, marks, insert — must remain callable from synthetic input. That's why macros stop on the first command that would have rung the bell: the input simulator treats a failed command as a real failed command and aborts the stream."),

    ("parts/13-macros/02-counted.json",
     "Counts re-invoke macros, they don't transform them",
     "{key:5}{key:@}{key:a} runs the recorded stream five times in sequence; it does not multiply counts inside the recording. Side effects (cursor position, register state, search state) carry over from one invocation to the next. That's how `5@a` plus a motion-at-end-of-recording produces a sweep instead of doing the same thing five times in place."),

    ("parts/13-macros/03-editing.json",
     "Macro recursion has a bounded call stack",
     "A macro can invoke another macro (or itself), but the recursion depth is capped — usually a few hundred — to prevent runaway loops. Macros are stored as plain register text, so editing a macro is just editing the text in that register: yank it onto a line, change it, then yank back into the register."),

    ("parts/14-windows-buffers-tabs/04-buffers.json",
     "Buffer state and window state are independent layers",
     "A buffer owns the text and the modified flag. A window owns a viewport (top line, leftmost column) and a cursor position. The same buffer can be open in multiple windows simultaneously, each with its own cursor. Closing a window doesn't close its buffer — buffers persist hidden until explicitly deleted with {key::}{key:b}{key:d}. Internally these are two object pools with a many-to-many relationship."),

    ("parts/14-windows-buffers-tabs/06-buffers-vs-windows-vs-tabs.json",
     "Three nested containers, not three competing concepts",
     "The data model is strictly nested: tabs contain windows, windows show buffers, buffers hold lines. A tab is a window-layout container; it doesn't own text. A window is a viewport into a buffer; it doesn't own text either. Only the buffer owns text. This explains every navigation command: {key::}{key:b}-prefixed jumps switch buffer in the current window; {key:Ctrl-W} jumps switch window in the current tab; {key:g}{key:t} jumps switch tab."),

    ("parts/15-prefix-families/01-g-overview.json",
     "{key:g} is a prefix router, not a command",
     "Vim's parser is a prefix dispatch tree: after {key:g} it waits for a second key and dispatches to a different handler depending on what arrives ({key:g}{key:g}, {key:g}{key:e}, {key:g}{key:U}, {key:g}{key:;}, …). That's why {key:g} alone does nothing — it's an open node in the tree. Same pattern for {key:z}, {key:[}, {key:]}, and the operator-pending state."),

    ("parts/15-prefix-families/02-z-overview.json",
     "{key:z} commands are viewport controllers",
     "The {key:z} family operates on the window's state, not the buffer's state. {key:z}{key:z}, {key:z}{key:t}, {key:z}{key:b} change the top-line offset; {key:z}{key:s}, {key:z}{key:e}, {key:z}{key:h}, {key:z}{key:l} change the leftmost-column offset. Folds and spell are also under {key:z} because they're presentation metadata, not buffer mutations. Think of {key:z} as 'view layer'."),

    ("parts/15-prefix-families/03-bracket-pairs.json",
     "Bracket-prefix commands are 'navigate by structure'",
     "The {key:[} and {key:]} prefixes share a theme: jump to the next/previous structural token. {key:[}{key:[}, {key:]}{key:]} jump by section; {key:[}{key:m}, {key:]}{key:m} by method; {key:[}{key:s}, {key:]}{key:s} by misspelled word; {key:[}{key:c}, {key:]}{key:c} by diff hunk. Each pair shares the same direction-flip implementation; only the structural predicate changes."),

    ("parts/16-insert-mode-power/01-exits.json",
     "Insert exit = state flip + cursor clamp + undo boundary",
     "Three things happen on Escape from insert mode, in order: the input transcript is finalized into the dot-repeat slot, an undo boundary is inserted, and the cursor is clamped back from the virtual one-past-end column to a real character. {key:Ctrl-C} skips the dot-repeat finalize step (which is why it doesn't update {key:.} the same way Esc does); {key:Ctrl-[} is a literal alias for Esc."),

    ("parts/17-ex-commands/02-substitute.json",
     "Substitute is search-pattern + replacement-template + flags",
     "{key::}{key:s} composes three subsystems: the regex engine (same one driving {key:/}); a small templating layer that expands `\\0`, `\\1`–`\\9`, `&`, `~`, `\\u`, `\\U`, `\\l`, `\\L`, `\\E`; and a flag-driven loop controller (`g`, `c`, `i`, `e`, `n`, `p`, `&`). Empty pattern reuses the last search — that's the global search-pattern slot again."),

    ("parts/18-visual-modes/06-gv.json",
     "{key:g}{key:v} reads the {key:'}{key:<} / {key:'}{key:>} marks",
     "The last visual selection is persisted into two special marks ({key:'}{key:<} for start, {key:'}{key:>} for end) plus a stored mode tag (charwise/linewise/blockwise). {key:g}{key:v} simply re-enters visual mode using those three pieces of state. The marks survive across commands, which is why you can edit, jump around, then come back with {key:g}{key:v} and find your old selection intact."),

    ("parts/19-command-line-power/01-history-window.json",
     "The command line is its own tiny modal editor",
     "Pressing {key::} opens a single-line input buffer with its own keymap, completion engine, and history ring. {key:q}{key::} promotes that input buffer into a full edit window where the entire command-line history becomes editable text — you can use normal-mode motions to find a command, then press Enter to execute the line under the cursor. It's literally Vim editing Vim's history with Vim."),

    ("parts/20-patterns-recipes/01-swap-and-duplicate.json",
     "Recipes work because everything shares the type tag",
     "{key:x}{key:p}, {key:d}{key:d}{key:p}, {key:y}{key:y}{key:p} are not magic tricks — they're proofs that the register type tag (charwise vs linewise) and the type-aware paste algorithm are coherent. {key:y}{key:y} stores `(line_text, line)`, then {key:p} reads the `line` tag and pastes on a new line below. The whole composition is a one-line regression test for the register/paste contract."),

    ("parts/20-patterns-recipes/03-cgn-dot.json",
     "{key:c}{key:g}{key:n} is the search-edit-repeat loop",
     "Three subsystems cooperate: search stores the active pattern, {key:g}{key:n} resolves to a motion that selects the next match, and {key:c} consumes that motion to replace it. The replacement also updates the dot-repeat slot, so {key:.} repeats the entire change against the next match without re-issuing the search. That's the smallest non-trivial example of dot, motion, and search composition."),

    ("parts/21-advanced/01-undo-tree.json",
     "Undo is a tree, not a stack",
     "Each undo unit creates a node in a directed graph. Linear edits build a chain; an edit after an undo creates a branch. {key:u}/{key:Ctrl-R} walk one chain; {key:g}{key:-}/{key:g}{key:+} walk by chronological time across branches; {key::}{key:earlier}/{key::}{key:later} walk by wall-clock time. Most editors throw away post-undo edits — Vim preserves them as branches you can navigate back to."),

    ("parts/21-advanced/03-op-pending.json",
     "Operator-pending is the most important hidden mode",
     "After you press an operator key like {key:d}, {key:c}, {key:y}, {key:>}, {key:<}, {key:g}{key:u}, {key:g}{key:U}, the editor enters a fourth major mode where it waits for a motion or text object to resolve a range. Until that resolves, no buffer change happens. The operator is staged with its count; the resolved motion provides `(start, end, type)`; only then does the operator function execute. This pending state is also why doubled forms ({key:d}{key:d}) work: the parser sees the operator key while in op-pending and short-circuits to 'current line, linewise.'"),

    ("parts/21-advanced/07-folding.json",
     "Folds are presentation metadata over immutable lines",
     "A fold doesn't modify the buffer. It's a `(start_line, end_line, state)` triple stored in window-side metadata, and the renderer hides those rows when state is closed. Fold methods (manual, indent, marker, syntax, expr) are different constructors for that triple — manual is user-supplied; indent computes from leading whitespace; marker scans for `{{{` / `}}}`; syntax asks the highlighter; expr evaluates a Vim-script expression per line."),

    ("parts/21-advanced/08-config.json",
     "Options partition into rendering, editing, and behavior",
     "Vim's option set is not flat. Rendering options (`'number'`, `'wrap'`, `'cursorline'`) only affect what the window draws. Editing options (`'shiftwidth'`, `'expandtab'`, `'autoindent'`) feed into the operator/insert layer. Behavior options (`'ignorecase'`, `'hlsearch'`, `'incsearch'`) configure subsystems like search. The `:set` command is one interface, but it dispatches across three subsystems with different reload semantics."),
]


def main(argv):
    added = 0
    skipped = 0
    missing = 0
    for rel, title, text in CALLOUTS:
        msg = add_internals(rel, title, text)
        if msg.startswith("ADD"):
            added += 1
        elif msg.startswith("skip dup"):
            skipped += 1
        else:
            missing += 1
        print(msg)
    print(f"\nADDED={added}  SKIPPED_DUP={skipped}  MISSING_FILE={missing}")


if __name__ == "__main__":
    main(sys.argv)
