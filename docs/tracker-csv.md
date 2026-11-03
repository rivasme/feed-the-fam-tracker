# tracker.csv and the other data files

`tracker.csv` is **your own file**. It is not committed (it is in `.gitignore`). The repo ships `tracker.example.csv`, which has the header and no rows. Everything that reads the CSV (`tracker-app/build.py`, `tools/merge_crawl.py`, `grading/grade_v2.py`, and every Claude Code prompt) reads `tracker.csv` and falls back to `tracker.example.csv` when it is missing. The first crawl merge or grading run creates `tracker.csv` by copying the example.

## Columns

| Column | Meaning |
|---|---|
| `tier` | `1` to `4` are roles found by a crawl or by hand (`4` is "new, not yet applied"). `9` is "other applications and roles you added". `removed` hides a row. |
| `order` | A number used to sort roles within a tier. |
| `company`, `title` | As posted. |
| `employment_type` | Full-time, contract, and so on, or "not stated". |
| `role_family` | Free text, or "not stated". |
| `posted_pay` | The posted pay, quoted. The page reads the amounts to sort by pay. |
| `level` | The level the posting names. |
| `remote_terms` | What the posting says about remote, hybrid or onsite work. |
| `years_required`, `education_language` | Quoted from the posting, or "not stated". |
| `fit_score_10` | Always empty. Fit and Opportunity letters are computed by `grading/grade_v2.py`. |
| `apply_link` | The posting link. The tracker never applies for you. |
| `date_checked` | When the link was last verified. |
| `status` | `Not applied`, `Applied`, `Interviewing`, `Offer`, `Rejected` or `Passed`. |
| `role_file` | Path to the role file, for example `roles/acme--senior-analyst.md`. |
| `date_applied`, `date_response` | `YYYY-MM-DD`. |
| `notes` | Notes written by Claude Code. The page shows them read-only as "Left by Claude". Your own notes live in the page. A note that starts `CHECK:` flags a row, and one containing `New in the <label> crawl` marks the role as new. |
| `events` | Activity log: `YYYY-MM-DD\|Text` entries joined by ` ;; `. |
| `gate_result`, `fit_grade`, `opp_grade`, `decision`, `confidence`, `legit_flag`, `grade_v2_src` | Filled in by `python3 grading/grade_v2.py ingest2`. |

## Other files the build reads (all optional)

| File | What it is |
|---|---|
| `roles/*.md` | One role file per role, written by the crawl. Plain text with the posting's details and quoted requirements. |
| `tracker-app/grades2.json` | The grades, written by `grade_v2.py ingest2`. Not committed. |
| `profile/profile.json` | Your profile. See `docs/profile-schema.md`. Not committed. |
| `logs/crawl-log.json` | A JSON array shown in the Crawl log panel. Each entry: `{"d":"YYYY-MM-DD","t":"short title","res":"one-line result","why":"what you looked for","lanes":[["lane name", roles_kept, "what was searched and found"]],"blocked":["anything blocked"],"note":"optional"}`. Not committed. |

## Crawl results

`python3 tools/merge_crawl.py new-crawlN YYYY-MM-DD` reads `new-crawlN/results/*.tsv` (tab separated) with this header:
`company, title, apply_link, posted_pay, level, employment_type, remote_terms, years_required, education_language, fit_score_10, date_checked, role_file, source_found_on`.
It skips roles already in the CSV, copies role files into `roles/`, checks each link, flags a hard degree requirement in the note, and writes a backup of your CSV to `logs/` first.
