# Contributing

Thanks for helping. People using this are often stressed and tired, so please be kind.

## The most useful thing you can do

Tell me how it went. Use the **How it went** issue form or start a **Show and tell** discussion: what you used it for, what worked, what broke, what you changed for your role.

## Pull requests

Code review is welcome. Good pull requests:

- Fix a bug, improve wording, or make a part easier to understand.
- Add something that helps other roles (new rubric examples, new Build idea examples, translations).
- Stay small and say what changed and why.
- Pass the tests: run `python3 tools/tests/run_tests.py` (needs Python 3, Node.js 22 or newer, and Google Chrome).

## Privacy first

Never put any of this in an issue, discussion, commit or pull request:

- your résumé, phone number, email or address;
- real application data, company names from your search, or recruiter details;
- screenshots that show any of the above.

`tracker.csv`, `roles/`, `logs/` and your profile files are ignored by git on purpose. Keep it that way.

## No selling

This project is licensed for noncommercial use (PolyForm Noncommercial 1.0.0). Please don't use it to run a paid product or service, and don't submit changes meant to do that. By contributing, you agree your work is licensed under the same terms.

## Releasing a new version

Versions are numbered MAJOR.MINOR.PATCH (for example 1.2.0). Users' copies only learn about a release when `VERSION` on `main` is higher than theirs, so every change you want users told about needs a bump.

1. Pick the number. Wording or bug fix that changes nothing for the user: PATCH (1.1.1). New feature that breaks nothing: MINOR (1.2.0). A change that needs users to do something or breaks their existing files: MAJOR (2.0.0). When unsure, use MINOR.
2. Put the number in `VERSION` and add a section at the top of `CHANGELOG.md` with three lists, written for users: **What changed for you**, **Claude Code will offer to do this after you update** (steps for their existing roles or files, if any), and **If you update by hand**. `tools/check_update.py` copies the first two into the Update available modal, for every version newer than theirs.
3. Run `python3 tools/tests/run_tests.py`, merge to `main`, then publish a GitHub Release named after the version (for example v1.2.0) with the same notes, so people who Watch the repo get an email.
