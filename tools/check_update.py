#!/usr/bin/env python3
"""Ask the repository whether there is a newer version, and write logs/update-notice.json for the page.

  python3 tools/check_update.py

Read-only except for logs/update-notice.json: it runs `git fetch`, compares VERSION with the one on the
upstream branch, and copies the CHANGELOG entries newer than yours into the notice. The page shows the notice
under the version in the side nav the next time you rebuild it. Prints one line:
  UPDATE AVAILABLE 1.1.0 -> 1.2.0   |   UP TO DATE 1.1.0   |   COULD NOT CHECK: <reason>
The notice format is in docs/update-notice.md. It never pulls or changes any other file.
"""
import datetime, json, os, re, subprocess, sys

CODE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.environ.get("FTF_ROOT") or CODE_ROOT


def git(*a):
    return subprocess.run(["git", "-C", CODE_ROOT, *a], capture_output=True, text=True, timeout=20)


def vt(v):
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3])


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"[*`]", "", s)).strip()


def entries(changelog, current):
    """Changelog entries newer than `current`: (version, what changed, steps to do after updating)."""
    out = []
    for block in re.split(r"(?m)^## ", changelog)[1:]:
        head, _, body = block.partition("\n")
        v = re.match(r"\s*v?(\d+\.\d+(?:\.\d+)?)", head)
        if not v or vt(v.group(1)) <= vt(current):
            continue
        changes, steps, manual, into = [], [], [], None
        for ln in body.split("\n"):
            s = ln.strip()
            if re.match(r"\*\*what changed", s, re.I):
                into = changes
            elif re.match(r"\*\*(do this|claude code will offer)", s, re.I):
                into = steps
            elif re.match(r"\*\*if you update by hand", s, re.I):
                into = manual
            elif re.match(r"(?:[-*]|\d+\.)\s+", s) and into is not None:
                into.append(clean(re.sub(r"^(?:[-*]|\d+\.)\s+", "", s)))
        out.append((v.group(1), changes, steps))  # manual steps are for people who skip the update prompt, so the page does not show them
    return out


def write(notice):
    p = os.path.join(ROOT, "logs", "update-notice.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(notice, open(p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


def main():
    try:
        current = open(os.path.join(CODE_ROOT, "VERSION"), encoding="utf-8").read().strip()
    except OSError:
        print("COULD NOT CHECK: no VERSION file in this copy (it predates versioning; run git pull to get it)")
        return 1
    try:
        if not os.path.isdir(os.path.join(CODE_ROOT, ".git")):
            raise RuntimeError("this folder is not a git clone")
        f = git("fetch", "--quiet")
        if f.returncode:
            raise RuntimeError("git fetch failed: " + f.stderr.strip()[:120])
        latest = git("show", "@{u}:VERSION")
        if latest.returncode:
            raise RuntimeError("the upstream branch has no VERSION file")
        latest = latest.stdout.strip()
        behind = git("rev-list", "--count", "HEAD..@{u}").stdout.strip()
        log = git("show", "@{u}:CHANGELOG.md")
    except (OSError, RuntimeError, subprocess.SubprocessError) as e:
        print("COULD NOT CHECK: " + str(e))
        return 1
    today = datetime.date.today().isoformat()
    if vt(latest) > vt(current):
        ents = entries(log.stdout if log.returncode == 0 else "", current)
        write({"update": True, "checked": today, "current": current, "latest": latest, "behind": int(behind) if behind.isdigit() else 0,
               "changes": [c for _, ch, _ in ents for c in ch][:12], "steps": [s for _, _, st in ents for s in st][:8]})
        print(f"UPDATE AVAILABLE {current} -> {latest}")
    else:
        write({"update": False, "checked": today, "current": current, "latest": latest, "behind": 0, "changes": [], "steps": []})
        print(f"UP TO DATE {current}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
