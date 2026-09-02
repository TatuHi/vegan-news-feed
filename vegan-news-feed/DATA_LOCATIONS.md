# Where your data actually lives

This repo is the *code*. Everything below is *runtime data* — it lives outside the repo, per-machine, and cloning or pulling this repo never touches it. If you're setting this up for the first time, `README.md`'s Setup section creates these for you; this file is just the map, kept in one place instead of scattered across prose.

| What | Path | Why it's outside the repo |
|---|---|---|
| Discord webhook secret | `~/.config/vegan-news/.env` | Never committed to git; `chmod 600` restricts it to your own account |
| Send history — cross-day dedup, topic-balance tiebreaker, gap detection, **and a growing corpus of what was actually relevant** (not strictly limited to what was broadcast — see `PROCESS.md` iteration 10) | `~/.config/vegan-news/sent_history.json` | Per-machine runtime state, not code; grows daily. Entries recovered after the fact via an improved query (not actually sent) carry `"recovered_via"` alongside `"backfilled": true`, so `item_count` on a `"run"` entry still truthfully reflects what a viewer actually saw that day |
| `vegan-news-feed-review`'s proposals | `~/.config/vegan-news/proposals/` | Files inside `~/.claude/skills/` are treated as "sensitive" by Claude Code and block the Write tool without a human present to approve it — a scheduled review run would silently produce nothing if proposals stayed inside the skill folder. Moved out in `PROCESS.md` iteration 7, after discovering this the hard way on a real run. |

**If you want to back up or migrate your data**, `~/.config/vegan-news/` is the entire thing — copy that one folder, not anything under `~/.claude/skills/`.

**Setup creates these for you** (see `README.md`):
```bash
mkdir -p ~/.config/vegan-news/proposals
cp .env.example ~/.config/vegan-news/.env
chmod 600 ~/.config/vegan-news/.env
```
`sent_history.json` doesn't need pre-creating — `scripts/history.py` creates it on first `record` call.
