"""Per-part thesis paragraphs.

A short (3-5 sentence) introduction printed at the top of each part's
first topic page, right under the chapter title. The thesis explains
*why this part exists* and what the reader will get out of it -- it is
not a summary of the topics that follow.

Source format follows the same conventions as topic JSON content (see
``content/StyleGuide.md``):

* Keys you press: ``{key:X}`` -> rendered as boxed pills.
* Ex commands, file names, family names, option names, unix commands:
  Markdown backticks -> rendered as monospace.
* Mode names: Markdown italics, lowercase, e.g. ``*normal mode*``.
* No trailing prepositions; no plain-text key references.

Strings here are passed through ``render_inline`` in
``render_latex.py``, so all the usual markup works.
"""

from __future__ import annotations


PART_THESES: dict[str, str] = {
    "01-foundations": (
        "Vim is the way it is because of decisions made on hardware "
        "most readers have never touched. This chapter is the "
        "prerequisite for everything else: what *modal* really means, "
        "why you would ever want it, and the strange history that put "
        "{key:h}{key:j}{key:k}{key:l} under your fingers. By the end "
        "you should be convinced -- or at least intrigued enough to "
        "keep going."
    ),
    "02-survival": (
        "Here is the smallest possible useful subset of Vim: enough "
        "to open a file, change a word, undo a mistake, save, and "
        "quit without panic. You are not learning fluency here. You "
        "are learning escape velocity -- enough to use Vim *today,* "
        "in real work, while you build everything else on top of it."
    ),
    "03-basic-editing": (
        "Here is the verb-and-motion grammar from which the rest of "
        "the book is just remixes. Move by words and lines; delete "
        "with {key:d}, change with {key:c}, yank with {key:y}, put "
        "with {key:p}. Once these click as a *language* and stop "
        "feeling like trivia, every later chapter will read as "
        "variations on the same theme."
    ),
    "04-search-find": (
        "This chapter is about pinpoint motion. {key:f} finds a "
        "character on the current line; {key:/} searches the whole "
        "file; {key:*} looks for the word under the cursor everywhere. "
        "The point is to *teleport* to where you want to be instead of "
        "stepping there one character at a time."
    ),
    "05-counts": (
        "Most Vim commands take a numeric prefix that means \"do this "
        "$N$ times.\" Once you internalise {key:5}{key:j}, "
        "{key:3}{key:d}{key:w}, {key:1}{key:0}{key:p}, the count "
        "stops being a feature and becomes a *thought* that comes for "
        "free with every motion or operator."
    ),
    "06-dot-repeat": (
        "{key:.} repeats the last *change,* exactly. It is Vim's "
        "secret weapon: any edit you can express as one operation is "
        "now also a one-keystroke macro. This chapter is short "
        "because the idea is small -- and powerful because of how "
        "well it composes with everything else."
    ),
    "07-text-objects": (
        "Here you move from operating on *positions* to operating on "
        "*things.* {key:c}{key:i}{key:w} changes a word as a unit. "
        "{key:d}{key:a}{key:\"} deletes a quoted string including the "
        "quotes. {key:v}{key:i}{key:p} selects a paragraph. Text "
        "objects are why one keystroke in Vim can do the work of five "
        "keystrokes anywhere else."
    ),
    "08-wider-motions": (
        "When word-by-word is too small, jump by sentence, paragraph, "
        "screen, matching bracket, or WORD. These are the motions "
        "that let you cross the page with a few keys instead of "
        "paging through it line by line."
    ),
    "09-scrolling-screen": (
        "Here is how to move *the viewport* without moving the "
        "cursor -- and how to put the cursor wherever you want on the "
        "screen without scrolling. The cursor and the screen are two "
        "separate things, and Vim gives you commands for both."
    ),
    "10-marks-jumps": (
        "Bookmarks, the jumplist, the changelist, and the alternate "
        "file. Together they make \"go back to where I was\" a "
        "one-keystroke move -- even after wandering around the file "
        "or jumping across files."
    ),
    "11-transform": (
        "Here is how to reshape text that already exists: change "
        "case, indent, join lines, sort, format -- without retyping "
        "it. These are the commands you reach for when the content is "
        "right but the *shape* is wrong."
    ),
    "12-registers": (
        "Vim has dozens of clipboards. The unnamed register, the yank "
        "register, named registers `a`--`z`, numbered cut registers "
        "`1`--`9`, the system clipboard, the expression register. "
        "Most users only use one. Knowing the others is the "
        "difference between \"copy-paste\" and \"I have a slot for "
        "every snippet I'm carrying around right now.\""
    ),
    "13-macros": (
        "Record any sequence of keystrokes once into a register, and "
        "replay it any number of times against any number of lines. "
        "Macros are the bridge from \"I have to do this same edit "
        "twenty times\" to \"I press {key:@}{key:q} and walk away.\""
    ),
    "14-windows-buffers-tabs": (
        "There are three layers of \"more than one file at once.\" A "
        "*buffer* is a file loaded in memory. A *window* is a "
        "viewport onto a buffer. A *tab* is a layout of windows. "
        "Once those three words mean different things in your head, "
        "multi-file editing in Vim stops feeling strange."
    ),
    "15-prefix-families": (
        "Vim has a handful of prefix keys -- `g`, `z`, `Ctrl-W`, `[`, "
        "`]` -- and each opens up a whole sub-menu of commands. "
        "Learning a family at a time is more efficient than "
        "memorising commands one by one."
    ),
    "16-insert-mode-power": (
        "*Insert mode* is more than just typing. It offers "
        "completion, undo-friendly chunking, register paste, mid-line "
        "digraphs, indent control, and a small set of normal-mode-style "
        "commands that work without ever leaving *insert mode.*"
    ),
    "17-ex-commands": (
        "Now we reach the {key::} line. Everything from saving a file "
        "to running a substitution to executing arbitrary normal-mode "
        "keystrokes against an arbitrary range of lines lives here. "
        "*Ex mode* is the \"everything else\" mode -- and once you "
        "can read an *ex* command, half of Vim's reputation for "
        "arcaneness disappears."
    ),
    "18-visual-modes": (
        "Sometimes the cleanest move is to highlight first and "
        "operate second. Character, line, and block selections -- and "
        "what you can do with them once you have them. *Visual mode* "
        "is the bridge between the way other editors work and the "
        "way Vim works the rest of the time."
    ),
    "19-command-line-power": (
        "Here is the interactive {key::} line itself: history, the "
        "wildmenu, ranges, the command-line window ({key:q}{key::}), "
        "and *ex mode* editing tricks. Learning these turns the colon "
        "line from an oracle you consult into a tool you wield."
    ),
    "20-patterns-recipes": (
        "Here are specific, recurring keystroke patterns: "
        "block-comment a paragraph, search-and-replace with confirm, "
        "edit diff hunks, build files with quickfix, work with "
        "substitutions over visual selections. Less \"new commands\" "
        "and more \"well-worn paths through commands you already "
        "know.\""
    ),
    "21-advanced": (
        "Here is the high-leverage power-user surface: folding for "
        "collapsing structure, the built-in terminal, mappings for "
        "shaping your own dialect, tags for jumping to definitions, "
        "and configuration for making it all stick. These are "
        "additions that, once you have made them, you will refuse to "
        "live without."
    ),
    "22-tmux": (
        "This chapter is not about Vim. `tmux` is a separate program "
        "that *complements* Vim -- panes, windows, sessions, copy "
        "mode, prefix keys -- and is most of why Vim users live "
        "happily on the command line. If you only ever read one "
        "non-Vim chapter, this is the one."
    ),
    "99-appendices": (
        "Here is the reference material: a keyboard walk, a complete "
        "key reference, a motion taxonomy, a synonyms table, a "
        "learning path. These are pages you flip *to* when you need "
        "an answer, not pages you read straight through."
    ),
}


def thesis_for(part_dir: str) -> str | None:
    """Return the thesis source text for a part directory, or ``None``."""
    return PART_THESES.get(part_dir)
