#!/usr/bin/env python3
"""Smoke tests for the starter kit, run in a real (headless) Chrome.

  python3 tools/tests/run_tests.py                       # all suites
  python3 tools/tests/run_tests.py --denylist FILE       # also run the privacy scan with your own deny-list
  CHROME="/path/to/chrome" python3 tools/tests/run_tests.py

Needs Python 3, Node 22 or newer, and Google Chrome. Builds the page from throwaway fixture data (never from your own
tracker.csv), loads it in Chrome, runs each suite in tools/tests/ and prints PASS or FAIL lines.
Suites: empty (new user, zero roles, the first-run tour), graded (one graded role, a profile, strengths and gaps) and scripts
(merge_crawl.py, grade_v2.py and build.py on throwaway data).
"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
BUILD = os.path.join(REPO, "tracker-app", "build.py")


def make_root(kind, tmp):
    root = os.path.join(tmp, kind)
    for d in ("roles", "logs", "profile", "tracker-app"):
        os.makedirs(os.path.join(root, d), exist_ok=True)
    header = open(os.path.join(REPO, "tracker.example.csv")).read()
    if kind == "empty":
        shutil.copy(os.path.join(REPO, "tracker.example.csv"), os.path.join(root, "tracker.example.csv"))
        return root
    cols = header.strip().split(",")
    row = dict.fromkeys(cols, "")
    row.update(tier="4", order="1", company="Acme Analytics", title="Senior Data Analyst", employment_type="Full-time", role_family="data",
               posted_pay="$100K-$130K", level="Senior", remote_terms="Remote, USA", years_required="5+ years of data analysis", education_language="not stated",
               apply_link="https://example.com/jobs/1", date_checked="2026-11-01", status="Not applied", role_file="roles/acme-analytics--senior-data-analyst.md",
               notes="New in the 2026-11-01 crawl (found on: example board). Link returned HTTP 200 when fetched.")
    import csv
    with open(os.path.join(root, "tracker.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader(); w.writerow(row)
    open(os.path.join(root, "roles", "acme-analytics--senior-data-analyst.md"), "w").write(
        "# Senior Data Analyst\n- Company: Acme Analytics\n- Posted pay: $100K-$130K\n- Remote: Remote, USA\n- Years: 5+ years of data analysis\nDuties: build dashboards in Tableau and write SQL.\n\n## Condensed\n\n**What it is:** Analytics role on the growth team.\n**Must-haves:** SQL, Tableau.\n\n## Posting text\n\nFull posting: Acme Analytics wants a Senior Data Analyst to own dashboards.\n")
    gates = {k: {"r": "pass", "q": "not stated"} for k in ("pay", "remote", "type", "degree", "elig", "live", "avoid", "interm")}
    gates["pay"]["q"] = "$100K-$130K"
    g2 = {"acme-analytics--senior-data-analyst.md": {
        "gates": gates, "fit": {"skills": "B", "seniority": "A", "domain": "A", "evidence": "B"}, "opp": {"comp": "B", "loc": "B", "level": "A", "stage": None},
        "reqs": [{"req": "5+ years of data analysis", "type": "must", "status": "supported", "ev": "Senior Data Analyst"}, {"req": "Tableau dashboards", "type": "must", "status": "supported", "ev": "dashboards"},
                 {"req": "dbt", "type": "nice", "status": "missing", "ev": "none"}],
        "text": "notes", "legit": [], "why": ["Dashboards and SQL match the core duties.", "Pay clears the floor."], "match": ["SQL and Tableau dashboards", "Reporting automation"], "gaps": ["No dbt experience"]}}
    json.dump(g2, open(os.path.join(root, "tracker-app", "grades2.json"), "w"))
    json.dump({"first": "Maria", "last": "Lopez", "titles": ["Data Analyst", "BI Analyst"], "levels": ["Senior"], "remote": "Hybrid or remote", "city": "Austin, TX", "min": 90, "target": 110,
               "types": ["Full-time"], "avoid": "no crypto", "start": "2026-10-01", "facts": ["Fixture fact: six years of SQL and Tableau."],
               "axes": [["SQL", 4.5, "Daily use.", "SQL"], ["Dashboards", 4, "Tableau work.", "Dashboards"], ["Python", 2.5, "Light scripting.", "Python"], ["dbt", 1, "None documented.", "dbt"]],
               "strengths": [["SQL and Tableau", "Six years of daily use.", "Asked for in 70% of postings."], ["Reporting automation", "Cut report time.", "Asked for in 30%."]],
               "gaps": [["No dbt experience", "Not documented.", "Flagged on 20% of roles."]]}, open(os.path.join(root, "profile", "profile.json"), "w"))
    json.dump([{"d": "2026-11-01", "t": "Fixture crawl", "res": "3 roles found", "why": "Testing the log.", "lanes": [["Example board", 3, "Found three roles."]], "blocked": ["One page needed a login"], "note": "Fixture."}],
              open(os.path.join(root, "logs", "crawl-log.json"), "w"))
    return root


def run_suite(name, tour, tmp):
    root = make_root(name, tmp)
    out = os.path.join(tmp, name + ".html")
    env = dict(os.environ, FTF_ROOT=root, FTF_NO_UPDATE_CHECK="1")
    cmd = [sys.executable, BUILD, out] + ([] if tour else ["--no-tour"])
    r = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if r.returncode:
        return ["FAIL build: " + (r.stderr or r.stdout).strip()[-300:]]
    html = open(out).read()
    pre = open(os.path.join(HERE, "prelude.js")).read()
    suite = open(os.path.join(HERE, f"suite_{name}.js")).read()
    page = os.path.join(tmp, name + "_test.html")
    open(page, "w").write(html + "\n<script>\n" + pre + "\n" + suite + "\n</script>\n")
    jsf = os.path.join(tmp, name + ".js")
    open(jsf, "w").write("\n".join(re.findall(r"<script>(.*?)</script>", html, re.S)))
    syn = subprocess.run(["node", "--check", jsf], capture_output=True, text=True)
    lines = []
    if syn.returncode:
        lines.append("FAIL page script has a syntax error: " + syn.stderr.strip()[:200])
    res = subprocess.run(["node", os.path.join(HERE, "run.mjs"), page, "90"], capture_output=True, text=True)
    lines += res.stdout.strip().split("\n")
    return lines


def main():
    deny = None
    if "--denylist" in sys.argv:
        deny = sys.argv[sys.argv.index("--denylist") + 1]
    tmp = tempfile.mkdtemp(prefix="ftf-tests-")
    total_pass = total_fail = 0
    for name, tour in (("empty", True), ("graded", False)):
        print(f"== suite: {name}")
        lines = run_suite(name, tour, tmp)
        for ln in lines:
            print("  " + ln)
            if ln.startswith("PASS"):
                total_pass += 1
            elif ln.startswith(("FAIL", "NO RESULT", "RUNNER ERROR")):
                total_fail += 1
            elif ln.startswith("PAGE_ERRORS") and not ln.strip().endswith(" 0"):
                total_fail += 1
    print("== suite: scripts")
    r = subprocess.run([sys.executable, os.path.join(HERE, "test_scripts.py")], capture_output=True, text=True)
    for ln in r.stdout.strip().split("\n"):
        if ln.startswith(("PASS", "FAIL")):
            print("  " + ln)
            total_pass += ln.startswith("PASS")
            total_fail += ln.startswith("FAIL")
    if r.returncode and "FAIL" not in r.stdout:
        print("  FAIL scripts suite crashed: " + r.stderr[-200:])
        total_fail += 1
    if deny:
        print("== privacy scan")
        r = subprocess.run([sys.executable, os.path.join(REPO, "tools", "privacy_scan.py"), "--denylist", deny, REPO], capture_output=True, text=True)
        print("  " + (r.stdout.strip() or r.stderr.strip()).replace("\n", "\n  "))
        if r.returncode:
            total_fail += 1
    print(f"\n{total_pass} passed, {total_fail} failed")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
