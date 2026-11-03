#!/usr/bin/env python3
"""Tests for the command-line pieces: merge_crawl.py, grade_v2.py and build.py, run against a throwaway copy of the repo layout.
They prove that tracker.csv is created from tracker.example.csv on first use and that the crawl -> grade -> build path works.
  python3 tools/tests/test_scripts.py
"""
import csv, json, os, shutil, subprocess, sys, tempfile

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond)))
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else " -> " + str(detail)))


def run(args, root):
    return subprocess.run([sys.executable] + args, env=dict(os.environ, FTF_ROOT=root), capture_output=True, text=True)


root = tempfile.mkdtemp(prefix="ftf-scripts-")
shutil.copy(os.path.join(REPO, "tracker.example.csv"), root)
os.makedirs(os.path.join(root, "new-crawl1", "results"))
os.makedirs(os.path.join(root, "new-crawl1", "roles"))
os.makedirs(os.path.join(root, "profile"))
json.dump({"min": 90, "first": "Maria"}, open(os.path.join(root, "profile", "profile.json"), "w"))
hdr = "company\ttitle\tapply_link\tposted_pay\tlevel\temployment_type\tremote_terms\tyears_required\teducation_language\tfit_score_10\tdate_checked\trole_file\tsource_found_on"
rows = [
    "Acme Analytics\tSenior Data Analyst\thttp://127.0.0.1:9/a\t$100K-$130K\tSenior\tFull-time\tRemote, USA\t5+ years\tnot stated\t\t2026-11-01\tnew-crawl1/roles/acme.md\tExample board",
    "Beta Retail\tReporting Analyst\thttp://127.0.0.1:9/b\t$60K-$70K\tMid\tFull-time\tOnsite\t2 years\tBachelor's degree required\t\t2026-11-01\tnew-crawl1/roles/beta.md\tExample board",
    "Acme Analytics\tSenior Data Analyst\thttp://127.0.0.1:9/dup\t$100K\tSenior\tFull-time\tRemote\t5+ years\tnot stated\t\t2026-11-01\t\tExample board",
]
open(os.path.join(root, "new-crawl1", "results", "lane.tsv"), "w").write(hdr + "\n" + "\n".join(rows) + "\n")
open(os.path.join(root, "new-crawl1", "roles", "acme.md"), "w").write("# Senior Data Analyst\nAcme Analytics. SQL and Tableau.\n")
open(os.path.join(root, "new-crawl1", "roles", "beta.md"), "w").write("# Reporting Analyst\nBeta Retail.\n")

check("tracker.csv does not exist before the first run", not os.path.exists(os.path.join(root, "tracker.csv")))
r = run([os.path.join(REPO, "tools", "merge_crawl.py"), "new-crawl1", "2026-11-05"], root)
check("merge_crawl runs", r.returncode == 0, r.stderr[-300:])
csvp = os.path.join(root, "tracker.csv")
check("merge_crawl created tracker.csv from tracker.example.csv", os.path.exists(csvp))
data = list(csv.DictReader(open(csvp))) if os.path.exists(csvp) else []
check("two new roles merged, the duplicate dropped", [d["company"] for d in data] == ["Acme Analytics", "Beta Retail"], [d["company"] for d in data])
check("notes say the role is new and flag a hard degree", "New in the 2026-11-05 crawl" in data[0]["notes"] and "DEGREE FLAG" in data[1]["notes"])
check("role files copied into roles/ and a backup written to logs/", os.path.exists(os.path.join(root, "roles", "acme.md")) and any(f.startswith("tracker-before-") for f in os.listdir(os.path.join(root, "logs"))))
check("columns match the example header", list(data[0].keys()) == open(os.path.join(REPO, "tracker.example.csv")).read().strip().split(","))

r = run([os.path.join(REPO, "grading", "grade_v2.py"), "batches2"], root)
batch = os.path.join(root, "grading", "pending2", "batch1.txt")
check("batches2 lists both roles for grading", r.returncode == 0 and os.path.exists(batch) and len(open(batch).read().split()) == 2, r.stdout + r.stderr)


def entry(file, pay_r, fit, opp):
    g = {k: {"r": "pass", "q": "not stated"} for k in ("pay", "remote", "type", "degree", "elig", "live", "avoid", "interm")}
    g["pay"] = {"r": pay_r, "q": "quote"}
    return {"file": file, "gates": g, "fit": fit, "opp": opp, "reqs": [{"req": "x", "type": "must", "status": "supported", "ev": "y"}], "text": "notes", "legit": [], "why": ["a"], "match": ["b"], "gaps": ["c"]}


out = os.path.join(root, "grading", "pending2-out")
os.makedirs(out, exist_ok=True)
json.dump([entry("roles/acme.md", "pass", {"skills": "A", "seniority": "A", "domain": "A", "evidence": "A"}, {"comp": "A", "loc": "A", "level": "A", "stage": None}),
           entry("roles/beta.md", "fail", {"skills": "B", "seniority": "B", "domain": "B", "evidence": "B"}, {"comp": "D", "loc": "C", "level": "C", "stage": None}),
           {"file": "roles/bad.md", "gates": {}, "fit": {}, "opp": {}}], open(os.path.join(out, "batch1.json"), "w"))
r = run([os.path.join(REPO, "grading", "grade_v2.py"), "ingest2"], root)
check("ingest2 merges the grades and skips the invalid entry", r.returncode == 0 and "merged 2 grades" in r.stdout and "skipped invalid entry" in r.stdout, r.stdout + r.stderr)
data = list(csv.DictReader(open(csvp)))
check("good role becomes Apply now", data[0]["decision"] == "apply" and data[0]["fit_grade"] == "A", data[0])
check("failed pay gate becomes Skip", data[1]["decision"] == "skip" and "fail:pay" in data[1]["gate_result"], data[1])
g2 = json.load(open(os.path.join(root, "tracker-app", "grades2.json")))
check("grades2.json written with computed letters", set(g2) == {"acme.md", "beta.md"} and g2["acme.md"]["c"]["decision"] == "apply")

page = os.path.join(root, "page.html")
r = run([os.path.join(REPO, "tracker-app", "build.py"), page], root)
html = open(page).read() if os.path.exists(page) else ""
check("build.py builds from the merged data", r.returncode == 0 and "Acme Analytics" in html and "Beta Retail" in html, r.stdout + r.stderr)
check("build injects the profile and turns the tour on by default", '"first": "Maria"' in html.replace('"first":"Maria"', '"first": "Maria"') and "const ONB_AUTO=true" in html)
r = run([os.path.join(REPO, "tracker-app", "build.py"), page, "--no-tour"], root)
check("--no-tour turns the tour off", "const ONB_AUTO=false" in open(page).read())
os.remove(csvp)
r = run([os.path.join(REPO, "tracker-app", "build.py"), page], root)
check("build.py falls back to tracker.example.csv when tracker.csv is missing", r.returncode == 0 and "tracker.example.csv" in r.stdout and "with 0 role(s)" in r.stdout, r.stdout + r.stderr)
check("the repo itself has no tracker.csv", not os.path.exists(os.path.join(REPO, "tracker.csv")))

bad = [n for n, ok in results if not ok]
print(f"\n{len(results) - len(bad)} passed, {len(bad)} failed")
sys.exit(1 if bad else 0)
