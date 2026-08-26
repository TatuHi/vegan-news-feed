# To-do

Open items across both `vegan-news-feed` and `vegan-news-feed-review`, kept here so a future Claude Code session — with no memory of past conversations — can read this file and act on it directly, without needing prior chat context to reconstruct what's outstanding and why.

Relationship to the other docs: `PROCESS.md` documents what was decided and why, in the past tense, as a design history. This file documents what's still open, in enough detail to action. **Whenever an item here is resolved, remove it and, if the change is significant, add an entry to `PROCESS.md`'s iteration history instead — don't just delete silently.** Whenever a new open item comes up in conversation, add it here, not just in chat, or it will be lost the moment the conversation ends.

## vegan-news-feed

- **`elaintenystava.fi` add/skip decision deferred.** SEY's own "Eläinten ystävä" publication feed — currently excluded because it heavily overlaps `sey.fi/feed/`, which was already a judgment call about pet-rescue-story noise (see `PROCESS.md` iteration 3). Revisit after observing a few weeks of `sey.fi` in practice: add `elaintenystava.fi/feed/` to `references/feeds.md` if `sey.fi` alone turns out too thin, otherwise leave as-is.
- **`evals/evals.json` doesn't cover what's been built since the original 3 cases.** Missing coverage: cross-day history dedup (`history.py show`/`record`), direct-link resolution over Google News redirects, mechanical near-duplicate detection (`normalize_title` in `fetch_feeds.py`), noisy-source filtering (a `sey.fi` pet-rescue story correctly getting excluded), the always-record run-marker (step 7), the `gaps`/backfill workflow, and the step 2 topic-balance tiebreaker. Add eval prompts exercising each.
- **No-news fallback branch never exercised on a real quiet day.** Step 5's "Ei merkittäviä uutisia tänään" message and step 7's `"type": "run", "result": "no_news"` marker are implemented and reasoned through, but never actually triggered by a real day with zero relevant news. Confirm behavior next time it happens naturally, or force a dry run with an artificially narrow relevance bar to check the whole path end-to-end.

## vegan-news-feed-review

- **Never actually run against a real week of rich-schema data yet.** The only real run so far (2026-08-26) hit the "history too thin, don't fabricate findings" branch — correct behavior, but the actual pattern-analysis logic (source contribution counts, summary-quality judgment, content-idea genuineness) has not yet been exercised against real multi-day, rich-schema (`summary`/`source`-populated) history. Revisit once `vegan-news-feed` has accumulated roughly a week of runs under the current schema.

## Cross-cutting / meta

- **Keep this file current.** This item is itself the answer to "the to-do list needs to be documented for later use" — this file *is* that documentation. Update it whenever the to-do list changes in conversation; don't let it drift back into being chat-only state.
