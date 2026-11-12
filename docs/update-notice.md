# logs/update-notice.json

Written by `python3 tools/check_update.py` (Claude Code runs it at the start of every prompt you paste). Read by `tracker-app/build.py`, which bakes it into the page. Not committed (it is in `logs/`).

```json
{
  "update": true,
  "checked": "2026-11-12",
  "current": "1.1.0",
  "latest": "1.2.0",
  "behind": 3,
  "changes": ["Plain-language line for each change in the new version(s)."],
  "steps": ["A step to do after updating, if the changelog lists one."]
}
```

- `update` is `false` when you are current; the page then shows nothing but the version.
- The page ignores a notice whose `latest` is not newer than your `VERSION`, so it clears itself after you update.
- `changes` and `steps` come from the "What changed for you" and "Do this after you update" lists in `CHANGELOG.md`.
