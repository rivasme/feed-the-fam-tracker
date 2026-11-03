#!/usr/bin/env python3
"""Grading helpers: compute Fit, Opportunity, decision and confidence, and move batches of roles in and out of graders.

  python3 grading/grade_v2.py batches2        # list roles that have a role file but no grade; write grading/pending2/batchN.txt (15 per batch)
  python3 grading/grade_v2.py ingest2         # merge grading/pending2-out/*.json into tracker-app/grades2.json and the decision columns of tracker.csv
  python3 grading/grade_v2.py show A.json     # compute and print Fit, Opportunity, decision and confidence for each role in a grader's file
  python3 grading/grade_v2.py agree A.json B.json   # compare two graders' outputs for the same roles

Weights, cutoffs, caps and the decision matrix are in docs/grading-spec-v2.md. Change them only on purpose, in this file
and in tracker-app/template.html together.
tracker.csv is your own file and is never committed. If it does not exist, it is created from tracker.example.csv.
"""
import collections, csv, datetime, glob, json, os, re, shutil, sys

ROOT = os.environ.get("FTF_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(ROOT, "tracker.csv")
G2 = os.path.join(ROOT, "tracker-app", "grades2.json")
FW = dict(skills=35, seniority=25, domain=20, evidence=20)
OW = dict(comp=40, loc=25, level=20, stage=15)
P = dict(A=4, B=3, C=2, D=1, F=0)
MATRIX = {"A": {"A": "apply", "B": "apply", "C": "consider", "D": "consider"},
          "B": {"A": "apply", "B": "apply", "C": "consider", "D": "skip"},
          "C": {"A": "consider", "B": "consider", "C": "skip", "D": "skip"}}


def ensure_csv():
    if not os.path.exists(CSV):
        shutil.copy(os.path.join(ROOT, "tracker.example.csv"), CSV)
        print("created tracker.csv from tracker.example.csv")


def profile_min_k():
    """The person's minimum pay in $K, from profile/profile.json, or None."""
    p = os.path.join(ROOT, "profile", "profile.json")
    try:
        v = float(re.sub(r"[^0-9.]", "", str(json.load(open(p)).get("min", ""))) or 0)
        return v or None
    except Exception:
        return None


def grade(d, W, cap_dim):
    w = s = 0
    for k in W:
        if d.get(k) in P:
            w += W[k]
            s += W[k] * P[d[k]]
    if w == 0:
        return None, 0
    x = s / w
    L = "A" if x >= 3.4 else "B" if x >= 2.6 else "C" if x >= 1.8 else "D" if x >= 1 else "F"
    if d.get(cap_dim) == "F" and L in "AB":
        L = "C"
    return L, sum(1 for k in W if d.get(k) in P)


def evidence_from_reqs(reqs):
    # A: every must-have supported. B: none missing and at least half supported. C: none missing but under half supported, or one missing with at least half of the others supported.
    # D: one missing with under half of the others supported, or two missing. F: more than two must-haves missing.
    m = [r["status"] for r in reqs if r.get("type") == "must"] or [r["status"] for r in reqs]
    if not m:
        return None
    s, miss = m.count("supported"), m.count("missing")
    if miss == 0:
        return "A" if s == len(m) else "B" if s * 2 >= len(m) else "C"
    others = len(m) - miss
    if miss == 1:
        return "C" if others and (m.count("supported") * 2 >= others) else "D"
    return "D" if miss == 2 else "F"


def evaluate(e):
    e = dict(e)
    e["fit"] = dict(e["fit"])
    ev = evidence_from_reqs(e.get("reqs", []))
    if ev:
        e["fit"]["evidence"] = ev
    f, nf = grade(e["fit"], FW, "seniority")
    o, no = grade(e["opp"], OW, "comp")
    if f is None or o is None:
        return dict(fit=f, opp=o, decision="unrated", conf="Low", n=nf + no)
    g = {k: v["r"] for k, v in e["gates"].items()}
    n = nf + no
    text = e.get("text", "notes")
    conf = "High" if n >= 7 and text == "full" else "Low" if (n <= 4 or text == "title") else "Medium"
    if any(v == "fail" for k, v in g.items() if k != "interm"):
        return dict(fit=f, opp=o, decision="skip", conf=conf, n=n)
    fc = "D" if f in "DF" else f
    oc = "D" if o in "DF" else o
    d = "skip" if fc == "D" else MATRIX[fc][oc]
    if d in ("apply", "consider") and (g.get("interm") == "fail" or "unknown" in g.values() or conf == "Low"):
        d = "research"
    return dict(fit=f, opp=o, decision=d, conf=conf, n=n)


def load(path):
    return {os.path.basename(e["file"]): e for e in json.load(open(path))}


def show(path):
    for k, e in load(path).items():
        r = evaluate(e)
        print(f"{k[:50]:50} Fit {r['fit']} Opp {r['opp']} {r['decision']:9} {r['conf']}")


def agree(a, b):
    A, B = load(a), load(b)
    common = sorted(set(A) & set(B))
    c = collections.Counter()
    diffs = []
    for k in common:
        ra, rb = evaluate(A[k]), evaluate(B[k])
        for m in ("fit", "opp"):
            c[m + "_same"] += ra[m] == rb[m]
            if ra[m] and rb[m]:
                c[m + "_within1"] += abs(P[ra[m]] - P[rb[m]]) <= 1
        c["decision_same"] += ra["decision"] == rb["decision"]
        if ra["decision"] != rb["decision"] or ra["fit"] != rb["fit"] or ra["opp"] != rb["opp"]:
            diffs.append((k, ra, rb))
    n = len(common)
    print(f"roles compared: {n}")
    for m in ("fit", "opp"):
        print(f"{m}: same letter {c[m+'_same']}/{n} ({100*c[m+'_same']//max(n,1)}%), within one letter {c[m+'_within1']}/{n} ({100*c[m+'_within1']//max(n,1)}%)")
    print(f"decision: same {c['decision_same']}/{n} ({100*c['decision_same']//max(n,1)}%)")
    for k, ra, rb in diffs:
        print(" -", k[:46], "|", ra["fit"], ra["opp"], ra["decision"], "vs", rb["fit"], rb["opp"], rb["decision"])


def batches2(n_per=15):
    ensure_csv()
    rows = [r for r in csv.DictReader(open(CSV, encoding="utf-8")) if r.get("tier") != "removed" and r.get("role_file")]
    files = []
    for r in rows:
        rf = r["role_file"]
        p = rf if os.path.isabs(rf) else os.path.join(ROOT, rf)
        if os.path.exists(p) and rf not in files:
            files.append(rf)
    done = json.load(open(G2)) if os.path.exists(G2) else {}
    pend = [f for f in files if os.path.basename(f) not in done]
    os.makedirs(os.path.join(ROOT, "grading", "pending2"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "grading", "pending2-out"), exist_ok=True)
    for f in glob.glob(os.path.join(ROOT, "grading", "pending2", "batch*.txt")):
        os.remove(f)
    k = 0
    for i in range(0, len(pend), n_per):
        k += 1
        open(os.path.join(ROOT, "grading", "pending2", f"batch{k}.txt"), "w").write("\n".join(pend[i:i + n_per]) + "\n")
    print(f"{len(pend)} roles need grades -> {k} batch file(s) in grading/pending2/")


def ingest2():
    ensure_csv()
    os.makedirs(os.path.dirname(G2), exist_ok=True)
    done = json.load(open(G2)) if os.path.exists(G2) else {}
    new = 0
    floor = profile_min_k()
    for f in sorted(glob.glob(os.path.join(ROOT, "grading", "pending2-out", "*.json"))):
        for e in json.load(open(f)):
            ok = set(e.get("fit", {})) == set(FW) and set(e.get("opp", {})) == set(OW) and set(e.get("gates", {})) >= {"pay", "remote", "interm"}
            if not ok or any(v not in (*P, None) for v in list(e["fit"].values()) + list(e["opp"].values())):
                print("skipped invalid entry:", e.get("file"))
                continue
            pg = e["gates"].get("pay", {})
            if floor and pg.get("r") == "fail":  # pay rule: a range passes when its top reaches the minimum
                nums = [x for x in (float(re.sub(r"[,k]", "", m.group(1).lower())) * (1000 if m.group(1).lower().endswith("k") else 1)
                                    for m in re.finditer(r"\$?\s?(\d{2,3}(?:,\d{3})+|\d{2,3}\s?[kK])", pg.get("q", ""))) if x >= 30000]
                if len(nums) >= 2 and max(nums) >= floor * 1000 and "top of range" not in pg["q"]:
                    pg["r"] = "pass"
                    pg["q"] += " (floor under $%dK, top of range reaches $%dK)" % (floor, max(nums) / 1000)
            rec = {k: e.get(k) for k in ("gates", "fit", "opp", "reqs", "text", "legit", "why", "match", "gaps")}
            rec["c"] = evaluate(e)
            done[os.path.basename(e["file"])] = rec
            new += 1
    json.dump(done, open(G2, "w"), indent=1, ensure_ascii=False)
    rd = csv.DictReader(open(CSV, encoding="utf-8"))
    fn = list(rd.fieldnames)
    rows = list(rd)
    add = ["gate_result", "fit_grade", "opp_grade", "decision", "confidence", "legit_flag", "grade_v2_src"]
    fn += [c for c in add if c not in fn]
    today = datetime.date.today().isoformat()
    for r in rows:
        for c in add:
            r.setdefault(c, "")
        e = done.get(os.path.basename(r.get("role_file", ""))) if r.get("role_file") else None
        if e:
            g = e["gates"]
            bad = [f"{v['r']}:{k}" for k, v in g.items() if v["r"] in ("fail", "unknown")]
            r.update(gate_result=" ".join(bad) or "pass", fit_grade=e["c"]["fit"] or "", opp_grade=e["c"]["opp"] or "", decision=e["c"]["decision"],
                     confidence=e["c"]["conf"], legit_flag="yes" if e.get("legit") else "", grade_v2_src="scored v2 " + today)
    with open(CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fn)
        w.writeheader()
        w.writerows(rows)
    print(f"merged {new} grades; rebuild the page with tracker-app/build.py")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    {"batches2": batches2, "ingest2": ingest2, "show": lambda: show(sys.argv[2]), "agree": lambda: agree(sys.argv[2], sys.argv[3])}.get(cmd, lambda: print(__doc__))()
