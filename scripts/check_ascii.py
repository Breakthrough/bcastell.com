#!/usr/bin/env python3
#
#      bcastell.com: personal website of Brandon Castellano
#   --------------------------------------------------------------
#       [  Site: https://www.bcastell.com/                      ]
#       [  Repo: https://github.com/Breakthrough/bcastell.com  ]
#
# Copyright (C) 2026 Brandon Castellano <http://www.bcastell.com>.
#
"""Repo-wide ASCII check.

Scans all git-tracked text files for non-ASCII characters and reports each as
``path:line:col: U+XXXX (NAME) 'ch' -> 'suggestion'``. Files where non-ASCII is
intentional are listed in ``.github/ascii-allowlist.txt`` (one path or glob per
line; ``#`` starts a comment). Stdlib only; runs in well under a second.

Exit code 0 = clean, 1 = findings (or git failure).
"""

import subprocess
import sys
import unicodedata
from fnmatch import fnmatch
from pathlib import Path

BINARY_EXTS = {
    ".png",
    ".ico",
    ".jpg",
    ".jpeg",
    ".gif",
    ".bmp",
    ".pdf",
    ".7z",
    ".zip",
    ".gz",
    ".tar",
    ".exe",
    ".msi",
    ".dll",
    ".so",
    ".dylib",
    ".dat",
    ".enc",
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".mp4",
    ".avi",
    ".mkv",
    ".mov",
    ".webm",
    ".whl",
}

SUGGESTIONS = {
    "\N{EM DASH}": "--",
    "\N{EN DASH}": "-",
    "\N{HORIZONTAL ELLIPSIS}": "...",
    "\N{RIGHTWARDS ARROW}": "->",
    "\N{LEFT RIGHT ARROW}": "<->",
    "\N{MULTIPLICATION SIGN}": "x",
    "\N{MICRO SIGN}": "u",
    "\N{ALMOST EQUAL TO}": "~=",
    "\N{COPYRIGHT SIGN}": "(C)",
    "\N{REGISTERED SIGN}": "(R)",
    "\N{TRADE MARK SIGN}": "(TM)",
    "\N{DEGREE SIGN}": " deg",
    "\N{LEFT DOUBLE QUOTATION MARK}": '"',
    "\N{RIGHT DOUBLE QUOTATION MARK}": '"',
    "\N{LEFT SINGLE QUOTATION MARK}": "'",
    "\N{RIGHT SINGLE QUOTATION MARK}": "'",
    "\N{NO-BREAK SPACE}": " ",
}


def load_allowlist(path: Path) -> list[str]:
    if not path.exists():
        return []
    patterns = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            patterns.append(line)
    return patterns


def is_allowed(rel_path: str, patterns: list[str]) -> bool:
    return any(fnmatch(rel_path, pat) for pat in patterns)


def tracked_files() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], text=True)
    return [line for line in out.splitlines() if line]


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    allowlist = load_allowlist(repo_root / ".github" / "ascii-allowlist.txt")
    findings = []
    for rel in tracked_files():
        if Path(rel).suffix.lower() in BINARY_EXTS:
            continue
        if is_allowed(rel, allowlist):
            continue
        full = repo_root / rel
        try:
            text = full.read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError):
            continue
        for lineno, line in enumerate(text.splitlines(), start=1):
            for col, ch in enumerate(line, start=1):
                if ord(ch) > 0x7F:
                    name = unicodedata.name(ch, "?")
                    suggest = SUGGESTIONS.get(ch, "")
                    suggest_str = f" -> '{suggest}'" if suggest else ""
                    findings.append(
                        f"{rel}:{lineno}:{col}: U+{ord(ch):04X} ({name}) '{ch}'{suggest_str}"
                    )
    if findings:
        print("Non-ASCII characters found in tracked files:", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        print(
            f"\n{len(findings)} finding(s). To allow a file, add a glob to "
            ".github/ascii-allowlist.txt with a justification comment.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
