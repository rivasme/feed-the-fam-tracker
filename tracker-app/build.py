#!/usr/bin/env python3
"""Build the tracker page.

  python3 tracker-app/build.py tracker-app/dist/index.html          # first-run tour on (the default)
  python3 tracker-app/build.py tracker-app/dist/index.html --no-tour # no automatic tour

Reads, relative to the repo root:
  tracker.csv            your roles (falls back to tracker.example.csv, which has no rows)
  tracker-app/grades2.json   optional, written by `python3 grading/grade_v2.py ingest2`
  profile/profile.json   optional, see docs/profile-schema.md
  logs/crawl-log.json    optional, see docs/tracker-csv.md
  roles/*.md             optional role files named in the CSV

Writes one self-contained HTML file. See docs/tracker-csv.md for the CSV columns.
"""
import csv, datetime, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get("FTF_ROOT") or os.path.dirname(HERE)  # FTF_ROOT lets the tests build from fixture data


CODE_ROOT = os.path.dirname(HERE)  # where the tracker code (and its VERSION file) lives


def app_info():
    """Version of this copy, and whether the repo has newer commits. Never fails the build, never changes files."""
    info = {"v": "", "behind": 0, "latest": ""}
    try:
        info["v"] = open(os.path.join(CODE_ROOT, "VERSION"), encoding="utf-8").read().strip()[:20]
    except OSError:
        pass
    if os.environ.get("FTF_NO_UPDATE_CHECK") or not os.path.isdir(os.path.join(CODE_ROOT, ".git")):
        return info
    try:
        run = lambda *a: subprocess.run(["git", "-C", CODE_ROOT, *a], capture_output=True, text=True, timeout=8)
        run("fetch", "--quiet")
        n = run("rev-list", "--count", "HEAD..@{u}")
        if n.returncode == 0 and n.stdout.strip().isdigit():
            info["behind"] = int(n.stdout.strip())
        if info["behind"]:
            lv = run("show", "@{u}:VERSION")
            if lv.returncode == 0:
                info["latest"] = lv.stdout.strip()[:20]
    except (OSError, subprocess.SubprocessError):
        pass
    return info


def first_existing(*names):
    for n in names:
        p = os.path.join(ROOT, n)
        if os.path.exists(p):
            return p
    return None


def load_json(rel, default):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return default
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception as e:  # a broken optional file should not stop the build
        print(f"warning: could not read {rel}: {e}", file=sys.stderr)
        return default


def clean(s, n=230):
    s = re.sub(r"\s+", " ", (s or "").replace("**", "")).strip()
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."


def add_days(d, n):
    return (datetime.date.fromisoformat(d) + datetime.timedelta(days=n)).isoformat()


STATUS = {"Not applied": "new", "Applied": "applied", "Interviewing": "interview", "Offer": "offer", "Rejected": "rejected", "Passed": "passed"}


def paymid(p):
    """Midpoint of a posted pay range in $K, for sorting. Hourly rates are annualised (x 2,080 hours)."""
    p = p or ""
    if re.search(r"(?i)per hour|/hr|an hour", p):
        v = [int(n) * 2.08 for n in re.findall(r"\$\s?(\d{2,3})(?![\d,kK])", p)]
    else:
        v = []
        for m in re.finditer(r"\$?\s?(\d{2,3})(?:,(\d{3})|\s?[kK])", p):
            x = int(m.group(1)) if m.group(2) is None else int(m.group(1) + m.group(2)) / 1000
            if x >= 60:
                v.append(x)
    return round((min(v) + max(v)) / 2, 1) if v else None


def posting(rf):
    """The role file's text, without the grader's verification notes, for the Tailor and Regrade prompts."""
    if not rf:
        return ""
    p = rf if os.path.isabs(rf) else os.path.join(ROOT, rf)
    if not os.path.exists(p):
        return ""
    out = []
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.startswith("Verification note") or ln.startswith("## Verification") or ln.strip().lower().startswith("## posting text"):
            break
        if re.match(r"- \*\*(Fit score|Strengths matched|Gaps)", ln) or ln.startswith("- **Direct apply"):
            continue
        out.append(ln.replace("**", ""))
    return re.sub(r"\n{2,}", "\n", "\n".join(out)).strip()[:3500]


def section(rf, heading, stop_at_posting=False, cap=2500):
    """The text under one '## heading' in a role file."""
    if not rf:
        return ""
    p = rf if os.path.isabs(rf) else os.path.join(ROOT, rf)
    if not os.path.exists(p):
        return ""
    out, on = [], False
    for ln in open(p, encoding="utf-8").read().split("\n"):
        if ln.strip().lower().startswith("## " + heading):
            on = True
            continue
        if on and ln.startswith("## "):
            break
        if on:
            out.append(ln.replace("**", ""))
    return re.sub(r"\n{3,}", "\n\n", "\n".join(out)).strip()[:cap]


def build(out_path, tour=True):
    csv_path = first_existing("tracker.csv", "tracker.example.csv")
    if not csv_path:
        sys.exit("No tracker.csv or tracker.example.csv found in " + ROOT)
    G2 = load_json("tracker-app/grades2.json", {})
    profile = load_json("profile/profile.json", {})
    crawls = load_json("logs/crawl-log.json", [])
    today = datetime.date.today()
    cutoff = (today - datetime.timedelta(days=21)).isoformat()  # only seed a follow-up date that is not long past

    roles = []
    for r in csv.DictReader(open(csv_path, encoding="utf-8")):
        r = {k: (v or "") for k, v in r.items() if k}
        if r.get("tier") not in ("1", "2", "3", "4", "9"):
            continue
        ext = r["tier"] == "9"
        rf = r.get("role_file", "")
        rid = ("x-" + re.sub(r"[^a-z0-9]+", "-", (r["company"] + "-" + r["title"]).lower()).strip("-")[:60]) if ext else \
            re.sub(r"[^A-Za-z0-9_-]", "-", rf.replace("roles/", "").replace(".md", ""))[:120]
        if not rid or rid == "x":
            rid = "r-" + re.sub(r"[^a-z0-9]+", "-", (r["company"] + "-" + r["title"]).lower()).strip("-")[:60]
        st = STATUS.get(r.get("status", ""), "new")
        notes = r.get("notes", "")
        seed = {}
        if st != "new":
            seed["status"] = st
            log = []
            da = r.get("date_applied", "")
            if da:
                seed["applied"] = da
                if st == "applied" and add_days(da, 7) >= cutoff:
                    seed["followUp"] = add_days(da, 7)
            if r.get("date_response"):
                seed["response"] = r["date_response"]
            if r.get("events"):
                for e in r["events"].split(" ;; "):
                    if "|" in e:
                        d, t = e.split("|", 1)
                        log.append({"d": d.strip(), "t": t.strip()})
            else:
                if da:
                    log.append({"d": da, "t": "Applied"})
                if r.get("date_response"):
                    log.append({"d": r["date_response"], "t": "Rejection email received" if st == "rejected" else "Response received"})
            if notes:
                seed["notes"] = notes
            if notes.startswith("CHECK:"):
                seed["check"] = True
            seed["log"] = sorted(log, key=lambda x: x["d"])
            iv = [e for e in seed["log"] if re.match(r"(?i)(interview|1st round interview|final interview)", e["t"])]
            if iv:
                seed["iv"] = iv
        elif notes:
            seed["notes"] = notes
        g2 = None
        e = G2.get(os.path.basename(rf)) if rf else None
        if e:
            g2 = {k: e.get(k) for k in ("gates", "fit", "opp", "reqs", "text", "legit", "why", "match", "gaps")}
            g2["src"] = "scored"
            g2["date"] = (r.get("grade_v2_src", "") or "").split(" ")[-1] or today.isoformat()
        try:
            order = int(r.get("order") or 0)
        except ValueError:
            order = 0
        roles.append(dict(
            id=rid, tier=int(r["tier"]), co=r["company"], title=r["title"],
            pay=clean(r.get("posted_pay"), 150), level=clean(r.get("level"), 90),
            type=clean(r.get("employment_type"), 60),
            rem=clean(r.get("remote_terms"), 220),
            yrs=clean(r.get("years_required"), 130), edu=clean(r.get("education_language"), 160),
            fit=r.get("fit_score_10", ""), url=r.get("apply_link", ""), file=rf, ext=ext,
            new=bool(re.search(r"\bNew in the .* crawl", notes)), pm=paymid(r.get("posted_pay")),
            seed=seed, ord=order, g=None, g2=g2, post=posting(rf), full=section(rf, "posting text", cap=12000)))
    roles.sort(key=lambda x: (x["tier"], x["ord"]))

    tpl = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

    def js(v):  # safe to embed inside a <script> tag
        return json.dumps(v, ensure_ascii=False).replace("</", "<\\/").replace("<!--", "<\\!--")

    html = (tpl.replace("__ROLES__", js(roles)).replace("__PROFILE__", js(profile if isinstance(profile, dict) else {}))
            .replace("__CRAWLS__", js(crawls if isinstance(crawls, list) else [])).replace("__ONB_AUTO__", "true" if tour else "false").replace("__APP__", js(app_info())))
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(html)
    print(f"built {out_path} with {len(roles)} role(s) from {os.path.relpath(csv_path, ROOT)}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    build(args[0], tour="--no-tour" not in sys.argv)
