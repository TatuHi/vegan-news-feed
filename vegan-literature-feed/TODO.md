# To-do

Open items for `vegan-literature-feed`, kept here so a future Claude Code session — with no memory of past conversations — can read this file and act on it directly. See `PROCESS.md` for why each of these was deliberately deferred rather than built now (the user explicitly asked for a minimum-viable version, to return to later).

## Not yet built

- **No scheduling.** No `run_daily.sh`/LaunchAgent wrapper exists yet — the skill only runs when invoked manually/interactively. When building one, copy `vegan-news-feed/scripts/run_daily.sh`'s pattern directly rather than rediscovering its three already-solved bugs: pin the Python path (`X | None` syntax needs 3.10+), pin the `claude` binary path (missing from a scheduled process's PATH), and use a macOS LaunchAgent, never cron (cron can't reach Keychain-based `claude` login) — see `../vegan-news-feed/PROCESS.md` iterations 6-7 for the full story.
- **No curated literature source list.** `scripts/fetch_pubmed.py` only queries PubMed's E-utilities API — there's no `references/sources.md` (the literature equivalent of `vegan-news-feed/references/feeds.md`) curating actual journal RSS feeds across nutrition, animal welfare science, environmental science, and ag/food policy. This would cover the agriculture/environment/policy gap (see below) more reliably than the current ad hoc `WebSearch` fallback in `SKILL.md` step 1.
- **`fetch_pubmed.py`'s `DEFAULT_QUERY` is a first-pass broad query, not tuned.** It returns real, parseable PubMed results (verified against the live API — see `PROCESS.md`), but is noisy: a test run surfaced clearly irrelevant veterinary-medicine results (e.g. swine gut histology, ewe sedation protocols) alongside relevant ones. This is currently left to the agent's step-2 judgment to filter, same as `vegan-news-feed`'s raw RSS data — but the query itself could likely be tightened with more specific MeSH terms once there's real usage experience to tune against.
- **Peer-reviewed-only vs. preprints was decided in favor of peer-reviewed-only, but not revisited.** If the "publish first" goal turns out to be poorly served by peer-review's inherent lag, revisit including bioRxiv/medRxiv with clear preprint flagging — this was a deliberate v1 choice, not a permanent one (see `PROCESS.md`).
- **Cadence: daily was chosen to start, with an explicit plan to loosen to weekly if too sparse** — but there's no scheduling yet (see above), so this hasn't actually been observed in practice. Revisit once it's running for real.

## Never actually run end-to-end

- **Only `fetch_pubmed.py` has been tested against real data** (a live PubMed query, verified to return sane, parseable results including a correctly-flagged review article). The rest of the pipeline — relevance/scientific-weight judgment (step 2), summary writing with caveats (step 3), the WebSearch fallback for the agriculture/environment/policy gap (step 1), message formatting (step 5), and an actual Discord send (step 6) — has never been run for real, only designed and reasoned through. Run it once manually before trusting it, the same discipline `vegan-news-feed` applied throughout its own build.
- **`evals/evals.json`'s 4 entries have never been executed** — written as specs only, same caveat as `vegan-news-feed`'s evals (see its own `TODO.md`).

## Open questions for later

- **Should `vegan-news-feed-review` also review this skill?** Deferred entirely — not designed, not decided. The review skill currently only knows about `vegan-news-feed`.
- **Separate Discord webhook.** Currently shares `vegan-news-feed`'s webhook value (in its own `~/.config/vegan-literature/.env`, at the user's explicit request, for testing convenience). Splitting to a distinct channel is a one-line `.env` edit whenever that's wanted — no code change needed.

## Cross-cutting / meta

- **Keep this file current.** Whenever an item here is resolved, remove it and add an entry to `PROCESS.md`'s iteration history instead of just deleting silently — same convention as `vegan-news-feed/TODO.md`.
