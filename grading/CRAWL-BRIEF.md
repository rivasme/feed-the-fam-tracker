# Crawl brief: rules for finding and grading new roles

Use this in every crawl brief.

- This tool never fills out or submits an application. Do not apply to anything, create accounts, sign in, or enter personal information.
- Do NOT assign a 1-10 fit score. Leave `fit_score_10` blank on new tracker rows.
- Capture every field the grader needs in the role file: title, company, link, date checked, pay (quoted), level, employment type, remote terms, years asked, education language, and the posting's key requirements (quoted). Write "not stated" when missing.
- Results go in `new-crawlN/results/<lane>.tsv` with this header (tab separated): `company, title, apply_link, posted_pay, level, employment_type, remote_terms, years_required, education_language, fit_score_10, date_checked, role_file, source_found_on`. Role files go in `new-crawlN/roles/`.
- Verify each link through the employer's public job-board data and note the date checked. Log anything blocked or unreadable. Stop a source that rate-limits you; never work around it.
- After the crawl, run `python3 tools/merge_crawl.py new-crawlN YYYY-MM-DD`. If `tracker.csv` does not exist it is created from `tracker.example.csv`.
- Then grade the new rows: run `python3 grading/grade_v2.py batches2`. Give each `grading/pending2/batchN.txt` to one grader agent with `grading/rubric-v2.md` and `grading/profile.md`, writing to `grading/pending2-out/batchN.json`. Then run `python3 grading/grade_v2.py ingest2` and rebuild the page.
- Grading: gates (pay floor, remote, employment type, degree, eligibility, liveness, avoid list, intermediary), a Fit letter (skills 35, seniority 25, domain 20, evidence 20) and an Opportunity letter (compensation 40, location 25, level 20, stage 15), plain A to F. Letters, confidence and the decision are computed by `grading/grade_v2.py`, never typed. Cutoffs: A 3.4, B 2.6, C 1.8, D 1.0; an F on seniority caps Fit at C and an F on compensation caps Opportunity at C.
- Decisions: Apply now, Consider, Research first, Skip; ungraded roles are Not Rated (see `docs/grading-spec-v2.md`).
- Add an entry to `logs/crawl-log.json` when the crawl finishes (format in `docs/tracker-csv.md`).
- Ask the user before changing weights, cutoffs or this rule.
