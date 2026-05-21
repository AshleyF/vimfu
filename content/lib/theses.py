"""Per-part thesis paragraphs.

A short (3-5 sentence) introduction printed at the top of each part's
first topic page, right under the chapter title. The thesis explains
*why this part exists* and what the reader will get out of it -- it is
not a summary of the topics that follow.

Style guide: plain prose, conversational, mode names in ``\\textit{...}``,
no key pills (those don't read well inside large italic text).
"""

from __future__ import annotations


# Map of part directory name -> thesis paragraph (LaTeX-ready prose).
PART_THESES: dict[str, str] = {
    "01-foundations": (
        "Vim is the way it is because of decisions made on hardware "
        "most readers have never touched. This chapter is the "
        "prerequisite for everything else: what \\textit{modal} really "
        "means, why you would ever want it, and the strange history "
        "that put hjkl under your fingers. By the end you should be "
        "convinced---or at least intrigued enough to keep going."
    ),
    "02-survival": (
        "The smallest possible useful subset of Vim: enough to open a "
        "file, change a word, undo a mistake, save, and quit without "
        "panic. You are not learning fluency here. You are learning "
        "escape velocity---enough to use Vim \\textit{today}, in real "
        "work, while you build everything else on top."
    ),
    "03-basic-editing": (
        "The verb-and-motion grammar that the rest of the book is just "
        "remixes of. Move by words and lines, delete with \\texttt{d}, "
        "change with \\texttt{c}, yank with \\texttt{y}, put with "
        "\\texttt{p}. Once these click as a \\textit{language} and "
        "stop feeling like trivia, every later chapter will read as "
        "variations on the same theme."
    ),
    "04-search-find": (
        "Pinpoint motion. \\texttt{f} finds a character on the current "
        "line; \\texttt{/} searches the whole file; \\texttt{*} looks "
        "for the word under the cursor everywhere. The point is to "
        "\\textit{teleport} to where you want to be instead of "
        "stepping there one character at a time."
    ),
    "05-counts": (
        "Most Vim commands take a numeric prefix that says ``do this "
        "$N$ times.'' Once you internalise \\texttt{5j}, \\texttt{3dw}, "
        "\\texttt{10p}, the count stops being a feature and becomes a "
        "\\textit{thought} that comes for free with every motion or "
        "operator."
    ),
    "06-dot-repeat": (
        "\\texttt{.} repeats the last \\textit{change}, exactly. It is "
        "Vim's secret weapon: any edit you can express as one "
        "operation is now also a one-keystroke macro. This chapter is "
        "short because the idea is small---and powerful because of "
        "what it composes with."
    ),
    "07-text-objects": (
        "Move from operating on \\textit{positions} to operating on "
        "\\textit{things}. \\texttt{ciw} changes a word as a unit. "
        "\\texttt{da\"} deletes a quoted string including the quotes. "
        "\\texttt{vip} selects a paragraph. Text objects are why one "
        "keystroke in Vim can do the work of five keystrokes anywhere "
        "else."
    ),
    "08-wider-motions": (
        "When word-by-word is too small, jump by sentence, paragraph, "
        "screen, matching bracket, or WORD. These are the motions that "
        "let you cross the page with a few keys instead of paging "
        "through it line by line."
    ),
    "09-scrolling-screen": (
        "How to move \\textit{the viewport} without moving the cursor"
        "---and how to put the cursor wherever you want on the screen "
        "without scrolling. The cursor and the screen are two separate "
        "things, and Vim gives you commands for both."
    ),
    "10-marks-jumps": (
        "Bookmarks, the jumplist, the changelist, and the alternate "
        "file. Together they make ``go back to where I was'' a "
        "one-keystroke move---even after wandering around the file or "
        "jumping across files."
    ),
    "11-transform": (
        "Reshape text that already exists: change case, indent, join "
        "lines, sort, format---without retyping it. These are the "
        "commands you reach for when the content is right but the "
        "\\textit{shape} is wrong."
    ),
    "12-registers": (
        "Vim has dozens of clipboards. The unnamed register, the yank "
        "register, named registers \\texttt{a}--\\texttt{z}, numbered "
        "cut registers \\texttt{1}--\\texttt{9}, the system clipboard, "
        "the expression register. Most users only use one. Knowing "
        "the others is the difference between ``copy-paste'' and "
        "``I have a slot for every snippet I'm carrying around right "
        "now.''"
    ),
    "13-macros": (
        "Record any sequence of keystrokes once into a register, and "
        "replay it any number of times against any number of lines. "
        "Macros are the bridge from ``I have to do this same edit "
        "twenty times'' to ``I press \\texttt{@q} and walk away.''"
    ),
    "14-windows-buffers-tabs": (
        "Three layers of ``more than one file at once.'' A "
        "\\textit{buffer} is a file loaded in memory. A "
        "\\textit{window} is a viewport onto a buffer. A "
        "\\textit{tab} is a layout of windows. Once those three "
        "words mean different things in your head, multi-file editing "
        "in Vim stops feeling strange."
    ),
    "15-prefix-families": (
        "Vim has a handful of prefix keys---\\texttt{g}, \\texttt{z}, "
        "\\texttt{Ctrl-W}, \\texttt{[}, \\texttt{]}---and each opens "
        "up a whole sub-menu of commands. Learning a family at a time "
        "is more efficient than memorising commands one by one."
    ),
    "16-insert-mode-power": (
        "Insert mode is more than just typing. There is completion, "
        "undo-friendly chunking, register paste, mid-line digraphs, "
        "indent control, and a small set of normal-mode-style commands "
        "that work without ever leaving insert."
    ),
    "17-ex-commands": (
        "The \\texttt{:} line. Everything from saving a file to "
        "running a substitution to executing arbitrary normal-mode "
        "keystrokes against an arbitrary range of lines. Ex is the "
        "``everything else'' mode---and once you can read an ex "
        "command, half of Vim's reputation for arcaneness disappears."
    ),
    "18-visual-modes": (
        "Sometimes the cleanest move is to highlight first and then "
        "operate. Character, line, and block selections---and what "
        "you can do with them once you have them. Visual mode is the "
        "bridge between the way other editors work and the way Vim "
        "works the rest of the time."
    ),
    "19-command-line-power": (
        "The interactive \\texttt{:} line itself: history, the "
        "wildmenu, ranges, the command-line window (\\texttt{q:}), "
        "and ex-mode editing tricks. Learning these turns the colon "
        "line from an oracle you consult into a tool you wield."
    ),
    "20-patterns-recipes": (
        "Specific, recurring keystroke patterns: block-comment a "
        "paragraph, search-and-replace with confirm, edit diff hunks, "
        "build files with quickfix, work with substitutions over "
        "visual selections. Less ``new commands'' and more "
        "``well-worn paths through commands you already know.''"
    ),
    "21-advanced": (
        "The high-leverage power-user surface: folding for collapsing "
        "structure, the built-in terminal, mappings for shaping your "
        "own dialect, tags for jumping to definitions, configuration "
        "for making it stick. These are the things that, once you "
        "have added them, you couldn't go back from."
    ),
    "22-tmux": (
        "Not Vim. A separate program that \\textit{complements} "
        "Vim---panes, windows, sessions, copy mode, prefix keys---and "
        "is most of why Vim users live happily on the command line. "
        "If you only ever read one non-Vim chapter, this is the one."
    ),
    "99-appendices": (
        "Reference material: a keyboard walk, a complete key "
        "reference, a motion taxonomy, a synonyms table, a learning "
        "path. These are pages to flip \\textit{to}, not pages to "
        "read through."
    ),
}


def thesis_for(part_dir: str) -> str | None:
    """Return the thesis text for a part directory, or ``None``."""
    return PART_THESES.get(part_dir)
