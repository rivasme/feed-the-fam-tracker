# profile/profile.json

The page and the Claude Code scripts read your profile from `profile/profile.json`. It is your own file: it is not committed. Copy `profile/profile.example.json` to start. Every key is optional.

The welcome tour in the page saves the same answers in your browser (key `jt-onb`). **Answers saved in the tour win over this file**, so you can build a page for yourself and still change things in the tour.

| Key | Type | Meaning |
|---|---|---|
| `first`, `last` | string | Your name. The first name is used by the hourly pep talks and in prompts. |
| `titles` | array of strings, or one comma-separated string | The kinds of roles you want. Domain matching and the crawl criteria use them. |
| `levels` | array of strings | For example `["Senior", "Lead"]`. |
| `remote` | `"Remote"`, `"Hybrid or remote"` or `"Onsite ok"` | The remote and location rule for the pay-floor and remote gates. |
| `city` | string | The place you can work from or near. |
| `min`, `target` | number, in $K | Minimum base pay that passes the pay gate; the pay that earns an A for compensation. |
| `types` | array of strings | `"Full-time"`, `"Contract"`, `"Part-time"`. Types you leave out fail the employment-type gate. |
| `avoid` | string | Companies, industries or requirements to skip. |
| `start` | `YYYY-MM-DD` | When your search started. The Overview timeline begins here. |
| `facts` | array of strings | Extra facts for the Assistant and the prompts, on top of the structured résumé. |
| `dont` | array of strings | Things the tool must never claim for you. Sensible defaults apply when it is empty. |
| `axes` | array of `[name, score 0-5, evidence note, short label]` | The evidence radar on the Strengths & Gaps tab (at least 3 entries). Written by the market-fit analysis prompt. |
| `strengths` | array of `[name, what proves it, how often postings ask for it]` | The Strengths list. |
| `gaps` | array of `[name, what is missing, how often postings flag it]` | The Gaps list. |
| `pageUrl` | string | The link of your published tracker page, so the rebuild prompt updates the same page. |
| `resume` | string | Optional raw résumé text. |
| `resumeData` | object | The résumé read into sections (the tour writes this in your browser; you rarely set it by hand). Shape: `{name, headline, contact, summary, exp:[{title:"Job title · Company", dates, sub, bullets:[...]}], skills:[{label, items:[...]}], cert}`. |

The build reads this file at build time (`python3 tracker-app/build.py ...`) and injects it into the page. Rebuild after you change it.
