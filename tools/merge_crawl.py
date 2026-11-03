#!/usr/bin/env python3
"""Merge a crawl's results into tracker.csv (new roles only, fit score left blank).

  python3 tools/merge_crawl.py new-crawl1 2026-11-05

Reads <crawl dir>/results/*.tsv with this tab-separated header (see docs/tracker-csv.md):
  company, title, apply_link, posted_pay, level, employment_type, remote_terms, years_required,
  education_language, fit_score_10, date_checked, role_file, source_found_on
Skips roles already in tracker.csv, copies each role file into roles/, checks each link's HTTP status, and writes a note
on each new row (flags for a hard degree requirement, then "New in the <label> crawl ..."). It never applies to anything.

tracker.csv is your own file and is never committed. If it does not exist yet it is created by copying tracker.example.csv.
A backup of the current tracker.csv goes to logs/ first. Then grade the new rows:
  python3 grading/grade_v2.py batches2   (grade the batches with agents)   ->   python3 grading/grade_v2.py ingest2
"""
import csv, datetime, glob, os, re, shutil, subprocess, sys

ROOT = os.environ.get("FTF_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) < 2:
    sys.exit(__doc__)
crawl = sys.argv[1].strip("/")
label = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
NC = os.path.join(ROOT, crawl)
CSV = os.path.join(ROOT, "tracker.csv")
if not os.path.exists(CSV):
    shutil.copy(os.path.join(ROOT, "tracker.example.csv"), CSV)
    print("created tracker.csv from tracker.example.csv")
os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "roles"), exist_ok=True)
shutil.copy(CSV, os.path.join(ROOT, "logs", f"tracker-before-{crawl}.csv"))
rdr = csv.DictReader(open(CSV, encoding="utf-8"))
fields = list(rdr.fieldnames)
rows = list(rdr)


def key(co, ti):
    return (re.sub(r"[^a-z0-9]", "", co.lower()), re.sub(r"[^a-z0-9]", "", ti.lower())[:40])


have = {key(r["company"], r["title"]) for r in rows}
cand = []
for f in sorted(glob.glob(os.path.join(NC, "results", "*.tsv"))):
    for r in csv.DictReader(open(f, encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE):
        r = {k: (v or "").strip().strip('"') for k, v in r.items() if k}
        r["src"] = os.path.basename(f)
        cand.append(r)
out, seen, dropped = [], set(), []
for r in cand:
    k = key(r.get("company", ""), r.get("title", ""))
    if not k[0] or k in seen or k in have:
        dropped.append((r.get("company", ""), r.get("title", ""), "duplicate"))
        continue
    seen.add(k)
    out.append(r)


def code(u):
    try:
        return subprocess.run(["curl", "-s", "-o", "/dev/null", "-L", "-m", "20", "-w", "%{http_code}", u], capture_output=True, text=True).stdout
    except Exception:
        return "err"


nums = [int(r["order"]) for r in rows if r.get("tier") == "4" and (r.get("order") or "").isdigit()]
base = max(nums + [0])
new = []
for i, r in enumerate(out, base + 1):
    rf = r.get("role_file", "")
    src = os.path.join(ROOT, rf) if rf else ""
    if rf and os.path.exists(src):
        shutil.copy(src, os.path.join(ROOT, "roles", os.path.basename(rf)))
    c = code(r.get("apply_link", ""))
    flags = []
    ed = (r.get("education_language", "") or "").lower()
    if "bachelor" in ed and "equivalent" not in ed and " or " not in ed and "not stated" not in ed:
        flags.append("DEGREE FLAG: hard degree requirement.")
    if "PAY FLAG" in r.get("posted_pay", ""):
        flags.append("PAY FLAG: see posted pay.")
    note = " ".join(flags) + (" " if flags else "") + f"New in the {label} crawl (found on: {r.get('source_found_on', '')[:60]}). Link returned HTTP {c} when fetched."
    d = {f: "" for f in fields}
    d.update(tier="4", order=str(i), company=r["company"], title=r["title"], employment_type=r.get("employment_type", ""), role_family="not stated",
             posted_pay=re.sub(r"^PAY FLAG: ", "", r.get("posted_pay", "")), level=r.get("level", ""),
             remote_terms=r.get("remote_terms", ""), years_required=r.get("years_required", ""),
             education_language=r.get("education_language", ""), fit_score_10="", apply_link=r.get("apply_link", ""), date_checked=r.get("date_checked", ""),
             status="Not applied", role_file=("roles/" + os.path.basename(rf)) if rf else "", notes=note)
    d = {k: v for k, v in d.items() if k in fields}
    new.append(d)
    print(c, r["company"], "|", r["title"][:50])
rows += new
with open(CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=fields)
    w.writeheader()
    w.writerows(rows)
print("added", len(new))
print("dropped", dropped)
