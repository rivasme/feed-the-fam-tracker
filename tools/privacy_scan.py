#!/usr/bin/env python3
"""Fail if personal data slipped into the repo.

  python3 tools/privacy_scan.py [--denylist FILE] [PATH ...]      (PATH defaults to the repo root)

Always checks for things that never belong in a shared repo: absolute home-directory paths, links to published claude.ai
artifacts, email addresses other than example addresses, and phone-number patterns.
With --denylist it also checks every line of FILE against all text files. Keep your deny-list OUTSIDE the repo (it names
the very things you want to keep out). One entry per line; blank lines and lines starting with # are ignored. Matching is
case-insensitive and ignores differences in whitespace:
  some phrase          plain text, matched anywhere
  w:word               whole word only
  r:regex              a regular expression
Exit code 0 means no hits.
"""
import os, re, sys

SKIP_DIRS = {".git", "node_modules", "__pycache__", "dist"}
TEXT_EXT = {".md", ".json", ".csv", ".tsv", ".txt", ".py", ".js", ".mjs", ".html", ".css", ".yml", ".yaml", ".toml", ".sh", ".gitignore", ".gitkeep", ""}
BUILTIN = [
    ("absolute home path", re.compile(r"/Users/[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+|C:\\Users\\[A-Za-z0-9._ -]+")),
    ("published artifact link", re.compile(r"claude\.ai/(code/)?artifact/", re.I)),
    ("email address", re.compile(r"[A-Za-z0-9._%+-]+@(?!example\.(com|org|net)\b)[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("phone number", re.compile(r"(?<!\d)(\+?1[ .-])?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")),
]


def norm(s):
    return re.sub(r"\s+", " ", s.lower())


def load_deny(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        if ln.startswith("r:"):
            out.append((ln, re.compile(ln[2:], re.I)))
        elif ln.startswith("w:"):
            out.append((ln, re.compile(r"\b" + re.escape(norm(ln[2:])) + r"\b")))
        else:
            out.append((ln, re.compile(re.escape(norm(ln)))))
    return out


def files(paths):
    for p in paths:
        if os.path.isfile(p):
            yield p
            continue
        for d, dirs, fs in os.walk(p):
            dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
            for f in fs:
                if os.path.splitext(f)[1].lower() in TEXT_EXT or f.startswith("."):
                    yield os.path.join(d, f)


def main():
    args = sys.argv[1:]
    deny = []
    if "--denylist" in args:
        i = args.index("--denylist")
        deny = load_deny(args[i + 1])
        del args[i:i + 2]
    paths = args or [os.path.dirname(os.path.dirname(os.path.abspath(__file__)))]
    hits = 0
    scanned = 0
    me = os.path.abspath(__file__)
    for f in files(paths):
        if os.path.abspath(f) == me:
            continue  # this file describes the patterns it looks for
        try:
            text = open(f, encoding="utf-8").read()
        except Exception:
            continue
        scanned += 1
        for n, line in enumerate(text.split("\n"), 1):
            for label, rx in BUILTIN:
                if rx.search(line):
                    print(f"{f}:{n}: {label}")
                    hits += 1
            nl = norm(line)
            for entry, rx in deny:
                if rx.search(nl):
                    print(f"{f}:{n}: deny-list entry {entry[:60]!r}")
                    hits += 1
    print(f"scanned {scanned} files, {hits} hit(s)")
    sys.exit(1 if hits else 0)


if __name__ == "__main__":
    main()
