"""Helpers for building "Practice in the simulator" deep links.

Every QR code / try-this link in the book and website seeds the sim's VFS
with a starting buffer, then runs ``nvim <file>``. The filename's extension
drives the sim's syntax-highlighting dispatch (see ``sim/src/highlight.js``
:func:`grammarForFile`), so we need to pick an extension that matches the
example's language — otherwise everything ends up as plaintext.
"""

from __future__ import annotations

import re

# Bumping this forces every browser to re-fetch /sim/ instead of using a
# cached copy. Bump whenever sim/index.html's preload semantics change.
SIM_LINK_VERSION = "3"

# Language → ``practice.<ext>`` mapping. Extensions must match the
# ``fileTypes`` arrays in ``sim/src/langs/*.js``.
_LANG_TO_EXT: dict[str, str] = {
    "python": "py", "py": "py",
    "javascript": "js", "js": "js", "node": "js",
    "typescript": "ts", "ts": "ts",
    "c": "c",
    "cpp": "cpp", "c++": "cpp", "cxx": "cpp",
    "html": "html", "htm": "html",
    "css": "css",
    "json": "json",
    "yaml": "yaml", "yml": "yaml",
    "shell": "sh", "sh": "sh", "bash": "sh", "zsh": "sh",
    "go": "go", "golang": "go",
    "rust": "rs", "rs": "rs",
    "markdown": "md", "md": "md",
    "text": "txt", "txt": "txt", "plain": "txt", "": "txt",
}


def _sniff_lang(text: str) -> str | None:
    """Best-effort guess of a language from buffer content.

    Conservative: only returns a language when the signal is strong.
    Returns ``None`` for prose-like Vim editing exercises (the bulk of
    VimFu's examples).
    """
    if not text:
        return None
    head = text[:2000]
    # Strong shebangs first.
    if re.match(r"#!\s*\S*\b(python\d?)\b", head):
        return "python"
    if re.match(r"#!\s*\S*\b(node|nodejs)\b", head):
        return "javascript"
    if re.match(r"#!\s*\S*\b(bash|sh|zsh|dash|ksh)\b", head):
        return "shell"
    # Language-distinctive markers.
    if re.search(r"^\s*#include\s*[<\"]", head, re.M):
        return "c"
    if re.search(r"^\s*(?:import|from)\s+\w+", head, re.M) and re.search(
        r"^\s*def\s+\w+\s*\(|^\s*class\s+\w+\s*[(:]", head, re.M
    ):
        return "python"
    if re.search(r"^\s*def\s+\w+\s*\(", head, re.M):
        return "python"
    if re.search(r"\bfunction\s+\w+\s*\(|=>\s*\{|\bconsole\.log\(", head):
        return "javascript"
    if re.search(r"^\s*(?:package|func|import)\s+", head, re.M) and "func " in head:
        return "go"
    if re.search(r"\bfn\s+\w+\s*\(|^\s*use\s+\w+::|let\s+mut\s+", head, re.M):
        return "rust"
    if re.search(r"<!DOCTYPE\s+html|<html\b|</\w+>", head, re.I):
        return "html"
    if re.search(r"^[\w-]+\s*\{[^}]*:[^}]*;", head, re.M):
        return "css"
    if re.match(r"\s*[\[\{]", head) and re.search(r'"\w+"\s*:', head):
        return "json"
    if re.search(r"^[A-Za-z_][\w-]*:\s*(?:\S|$)", head, re.M) and not re.search(
        r"^\s*(?:def|class|if|for|while)\b", head, re.M
    ):
        # Cheap YAML hint: ``key: value`` lines without Python-ish structure.
        if re.search(r"^\s*-\s+\w|^---\s*$", head, re.M):
            return "yaml"
    if re.search(r"^#{1,6}\s+\S|^[-*]\s+\S|^>\s+\S", head, re.M):
        return "markdown"
    return None


def practice_filename(ex: dict | None, content: str | None = None) -> str:
    """Return ``practice.<ext>`` for an example or content string.

    Resolution order:
      1. ``ex["lang"]`` (preferred — explicit declaration in the example JSON).
      2. ``ex["filename"]`` (lets an example pick its own name, e.g.
         ``Makefile``).
      3. Content sniff (conservative — only fires on strong signals).
      4. Fallback ``practice.txt``.
    """
    if isinstance(ex, dict):
        fn = ex.get("filename")
        if isinstance(fn, str) and fn.strip():
            return fn.strip()
        lang = (ex.get("lang") or "").strip().lower()
        if lang:
            ext = _LANG_TO_EXT.get(lang)
            if ext:
                return f"practice.{ext}"
    if content:
        sniffed = _sniff_lang(content)
        if sniffed:
            return f"practice.{_LANG_TO_EXT[sniffed]}"
    return "practice.txt"
