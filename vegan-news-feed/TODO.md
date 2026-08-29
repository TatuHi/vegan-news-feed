# To-do

Open items across both `vegan-news-feed` and `vegan-news-feed-review`, kept here so a future Claude Code session — with no memory of past conversations — can read this file and act on it directly, without needing prior chat context to reconstruct what's outstanding and why.

Relationship to the other docs: `PROCESS.md` documents what was decided and why, in the past tense, as a design history. This file documents what's still open, in enough detail to action. **Whenever an item here is resolved, remove it and, if the change is significant, add an entry to `PROCESS.md`'s iteration history instead — don't just delete silently.** Whenever a new open item comes up in conversation, add it here, not just in chat, or it will be lost the moment the conversation ends.

## vegan-news-feed

- **`elaintenystava.fi` add/skip decision deferred.** SEY's own "Eläinten ystävä" publication feed — currently excluded because it heavily overlaps `sey.fi/feed/`, which was already a judgment call about pet-rescue-story noise (see `PROCESS.md` iteration 3). Revisit after observing a few weeks of `sey.fi` in practice: add `elaintenystava.fi/feed/` to `references/feeds.md` if `sey.fi` alone turns out too thin, otherwise leave as-is.
- **`evals/evals.json` doesn't cover what's been built since the original 3 cases.** Missing coverage: cross-day history dedup (`history.py show`/`record`), direct-link resolution over Google News redirects, mechanical near-duplicate detection (`normalize_title` in `fetch_feeds.py`), noisy-source filtering (a `sey.fi` pet-rescue story correctly getting excluded), the always-record run-marker (step 7), the `gaps`/backfill workflow, and the step 2 topic-balance tiebreaker. Add eval prompts exercising each.
- **No-news fallback branch never exercised on a real quiet day.** Step 5's "Ei merkittäviä uutisia tänään" message and step 7's `"type": "run", "result": "no_news"` marker are implemented and reasoned through, but never actually triggered by a real day with zero relevant news. Confirm behavior next time it happens naturally, or force a dry run with an artificially narrow relevance bar to check the whole path end-to-end.

## vegan-news-feed-review

- (Resolved 2026-08-29, kept for context) Two bugs surfaced on the first real week-of-data run: a cross-directory Write needing `--add-dir`, and — more fundamentally — files inside `~/.claude/skills/` being treated as "sensitive" by Claude Code, blocking Write without a human present. Fixed by moving `proposals/` output to `~/.config/vegan-news/proposals/` and adding a second `--add-dir` to `run_weekly_review.sh`; verified with a real headless Write test (`exit 0`). See `PROCESS.md` iteration 7.
- **Scheduled 2026-08-29 (Sundays 13:15) via a LaunchAgent, but never yet fired by the real timer.** `~/Library/LaunchAgents/com.tatuhirvonen.vegan-news-feed-review.weekly.plist`, loaded with `launchctl bootstrap gui/502`, confirmed registered (`Weekday=0, Hour=13, Minute=15`). Unlike `vegan-news-feed`'s scheduling (`PROCESS.md` iteration 6), this was set up without waiting for a real near-term trigger to prove the mechanism end-to-end — the individual failure modes that bit the daily digest (PATH, Keychain-via-cron, sensitive-file Write) are already independently fixed/verified in this script, but the LaunchAgent trigger path itself for *this* script has not been. Worth checking the first real Sunday firing (log at `~/Library/Logs/vegan-news-feed-review.log`, or `launchctl print gui/502/com.tatuhirvonen.vegan-news-feed-review.weekly` for last exit code) rather than assuming it worked.

## Cross-cutting / meta

- **Keep this file current.** This item is itself the answer to "the to-do list needs to be documented for later use" — this file *is* that documentation. Update it whenever the to-do list changes in conversation; don't let it drift back into being chat-only state.
