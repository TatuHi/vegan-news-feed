# Vegan Literature Feed

*Part of a [3-project AI automation portfolio](../README.md) — start there for the plain-language overview.*

A [Claude Code](https://claude.com/claude-code) skill that monitors fresh scientific literature on veganism, plant-based nutrition, animal cognition/sentience, the environmental impact of animal agriculture, and animal-rights policy — surfacing peer-reviewed findings (including review articles and meta-analyses, not just novel primary research) with enough context that a comms team could credibly publish on one before mainstream science journalism does.

**Status: minimum viable, intentionally.** This was built as a first pass and then set aside — see [`TODO.md`](TODO.md) for the honest list of what's deferred (a curated journal source list, scheduling, broader eval coverage) before coming back to it.

## ⚠️ Disclaimer

`scripts/fetch_pubmed.py` was written by Claude (an AI, via Claude Code), as documented in [`PROCESS.md`](PROCESS.md). **It has not been independently reviewed by a human for correctness, security, or safety** — it has been run once against the live PubMed API to confirm it returns sane, parseable results (see `PROCESS.md`), which is not the same thing as a security or code review.

If you clone and run this code — especially if you ever schedule it, where it runs unattended with your credentials — **read it yourself first.** Don't run it blindly. The repository owner takes no responsibility for what happens if you do.

## Why peer-reviewed articles matter here, and why review articles count too

Two deliberate scope decisions, both revisitable:

- **Peer-reviewed only, no preprints (for now).** Faster coverage via bioRxiv/medRxiv was considered and explicitly declined to start — the risk of a comms team publishing on something that later fails review outweighs the speed advantage. PubMed itself only indexes peer-reviewed journal articles, so this is enforced automatically for PubMed-sourced items; anything found via the WebSearch fallback (see below) needs this checked manually per item.
- **Review articles, meta-analyses, and systematic reviews are treated as first-class content, not filtered out.** They often give the comms team more usable context than a single new primary-research finding — `SKILL.md` explicitly instructs judging them on their own terms (does this synthesize something useful?), not on "is this a new result?"

## Why a separate skill instead of a mode of `vegan-news-feed`

Same reasoning as the `vegan-news-feed-review` split: genuinely different job (scientific-weight judgment vs. newsworthiness judgment), different cadence expectation, different sourcing mechanism entirely (no RSS equivalent for most academic literature). See `../vegan-news-feed/PROCESS.md`'s iteration 4 entry for the fuller version of this argument, applied to a different sibling here.

## Sourcing, and its current gap

`scripts/fetch_pubmed.py` queries PubMed's E-utilities API (esearch → esummary → efetch) with a broad keyword query covering all four topic areas. PubMed covers the nutrition/health and animal-cognition angles well — it's a biomedical database, so it covers the agriculture/environment/policy angle poorly. `SKILL.md`'s step 1 asks the agent to run a few targeted `WebSearch` queries to fill that specific gap, with an explicit peer-review check per result (since WebSearch, unlike PubMed, can surface preprints or non-reviewed content).

A properly curated list of journal RSS feeds (the literature equivalent of `vegan-news-feed/references/feeds.md`) would cover this gap more reliably than ad-hoc WebSearch — that's deliberately deferred, see `TODO.md`.

## Setup

**Requirements** — same as `vegan-news-feed`: Claude Code, a Python 3.10+ interpreter at a known absolute path (stdlib only), a Discord webhook URL.

**1. Place the skill**
Put this whole folder at `~/.claude/skills/vegan-literature-feed/`.

**2. Configure the webhook**
```bash
mkdir -p ~/.config/vegan-literature
cp .env.example ~/.config/vegan-literature/.env
chmod 600 ~/.config/vegan-literature/.env
# now edit ~/.config/vegan-literature/.env and set your real DISCORD_WEBHOOK_URL
```
Reusing the same webhook value as `vegan-news-feed` is fine for testing — see "Shared webhook, for now" below.

**3. Run it manually**
Ask Claude Code something matching `SKILL.md`'s trigger phrasing, e.g. "aja vegan-literature-feed-skilli" or "onko alalla tullut mielenkiintoista tutkimusta?".

**4. Scheduling: not yet.** Unlike `vegan-news-feed`, this skill has no `run_daily.sh`/LaunchAgent wrapper yet — deliberately deferred (see `TODO.md`). When it's built, it should copy `vegan-news-feed/scripts/run_daily.sh`'s pattern directly (pinned Python path, pinned `claude` binary path, LaunchAgent not cron, dual-channel failure alerting) rather than rediscovering any of those three already-solved bugs.

## Shared webhook, for now

`vegan-literature-feed` reuses `vegan-news-feed`'s Discord webhook value in its own separate `~/.config/vegan-literature/.env` file, at the user's explicit request, purely for testing convenience while this skill is new. Splitting to a distinct channel later is a one-line edit to that `.env` file — no code change, since the two skills' config were kept structurally separate (own directory, own `.env`, own history file) from the start specifically so this split stays cheap.

## Reused scripts, not duplicated

`post_discord.py` and `history.py` are **not copied into this skill** — `SKILL.md` calls `../vegan-news-feed/scripts/post_discord.py` and `../vegan-news-feed/scripts/history.py` directly (the latter with `--history-file ~/.config/vegan-literature/literature_history.json` to keep its own history separate). Both scripts do an identical, generic job for either skill — duplicating them would just be two copies to keep in sync. Only `fetch_pubmed.py` is genuinely new, since the fetch mechanism (PubMed API, not RSS) is the one part that had to differ.

## Repo layout

```
SKILL.md              Agent instructions Claude Code actually reads to run this skill
PROCESS.md            Design history: why it's built this way, what changed and why
TODO.md                What's deliberately deferred, and why
.env.example           Template showing the required env var — no real secret in it
scripts/
  fetch_pubmed.py       Fetches recent PubMed articles via E-utilities (stdlib only)
evals/evals.json       A first pass at test prompts — thin coverage, see TODO.md
```

## Platform support

Same situation as `vegan-news-feed`: `fetch_pubmed.py` itself is pure Python standard library and portable to Linux/Windows given Python 3.10+. There's no wrapper script yet to make OS-specific in the first place — that question only becomes real once scheduling is built (see `TODO.md`).
