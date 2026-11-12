# Changelog

Newest first. To update your copy, see "Updating" in the README: `git pull`, then rebuild and republish the page.

## 1.1.0

**What changed for you**
- **Status and match are separate on role cards.** Status (what you did: Not applied, Applied, Interviewing...) is a solid pill at the top right. Match (what the grade suggests) is a dashed "Match: ..." tag in the bottom row, colored by urgency: Apply now green, Consider blue, Research first amber, Skip muted. Match now shows on every role and fades once you act on it, instead of disappearing.
- **Strengths & Gaps is one card** with the graph on the left and strengths and gaps on the right. It is now graded live against the roles marked Apply now or Consider, and "How this is graded" explains how.
- **The page and top bar are centered** on wide screens.
- **Version and updates:** the bottom of the side nav shows your version. Every prompt you paste into Claude Code now starts with an update check (`tools/check_update.py`). If there is a newer version, the next rebuild adds an Update available button under the version. It opens what is new and a Copy update prompt button that pulls the update for you.
- **Pep talk** moved into Settings (the gear). The on/off switch is there; "Send me one now" is gone.
- **The page remembers where you were** (screen, role, filters, scroll) and puts you back after you come back from Claude Code or the page reloads.
- **Each crawled role is saved as a condensed summary plus the full posting.** Regrade, résumé tailoring, letters and interview prep now use them.

**Do this after you update**
1. `git pull`, then rebuild and republish the page.
2. Roles crawled before this version have no condensed summary. They keep working (the page falls back to the saved notes). To add summaries to older roles, ask Claude Code: "For each role file without a Condensed section, fetch the posting and add one, following grading/CRAWL-BRIEF.md."

## 1.0.0

First public release.
