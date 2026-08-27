# Vegan News Feed — Review

A companion [Claude Code](https://claude.com/claude-code) skill that reviews its sibling, [`vegan-news-feed`](../vegan-news-feed/), and proposes improvements — without ever applying them itself.

## ⚠️ Disclaimer

`scripts/run_weekly_review.sh` was written by Claude (an AI, via Claude Code), iteratively, as documented in [`../vegan-news-feed/PROCESS.md`](../vegan-news-feed/PROCESS.md). **It has not been independently reviewed by a human for correctness, security, or safety.**

If you clone and run this code — especially if you schedule it via cron, where it runs unattended with your credentials — **read it yourself first.** Don't run it blindly. The repository owner takes no responsibility for what happens if you do.

## What it does

Reads the send history `vegan-news-feed` accumulates (`~/.config/vegan-news/sent_history.json` — what was actually sent, from where, and the real summary/content-idea text, not just headlines), looks for concrete patterns over the review window (default: last 7 days) — sources that never contribute, thin or repetitive summaries, content ideas that feel forced, coverage gaps, and run-outcome patterns (how many days had no relevant news at all, any backfilled or unrecoverable gaps) — and writes a dated, specific proposal file to `vegan-news-feed/proposals/`. It then posts a short Discord notification pointing to it.

**It never edits `vegan-news-feed`'s own files.** Applying a proposal is always a separate, human-initiated step — you read the proposal, decide, and either apply it yourself or ask Claude Code to apply a specific one interactively. This mirrors how every change to `vegan-news-feed` has actually been made: propose, explain the reasoning, human approves, then it's applied and documented in `PROCESS.md`.

## Why a separate skill instead of a mode of `vegan-news-feed`

Producing the daily digest and critiquing its own track record are genuinely different jobs, on different cadences, with different (and deliberately asymmetric) permissions — the reviewer needs read access to `vegan-news-feed`'s files but must never get write access to them. Keeping them as two skills makes that boundary structural rather than just a written rule. See `vegan-news-feed/PROCESS.md`'s iteration 4 entry for the fuller reasoning.

## Setup

No separate configuration needed — it reuses `vegan-news-feed`'s existing `~/.config/vegan-news/.env` (same Discord webhook, same channel) and calls its scripts directly by path. The only requirement is that `vegan-news-feed` is installed at `~/.claude/skills/vegan-news-feed/`.

**Run it manually, any time:**
```bash
~/.claude/skills/vegan-news-feed-review/scripts/run_weekly_review.sh
```
or just ask Claude Code directly: "aja vegan-news-feedin viikkokatsaus" / "arvioi vegan-news-feedin toimintaa".

**Or schedule it** (optional — it's fully useful without ever being scheduled):
```
0 20 * * 0 /Users/<you>/.claude/skills/vegan-news-feed-review/scripts/run_weekly_review.sh >> ~/Library/Logs/vegan-news-feed-review.log 2>&1
```
(Sundays at 20:00, as an example — adjust to taste.)

## Repo layout

```
SKILL.md                    Agent instructions
scripts/run_weekly_review.sh  Cron-safe wrapper, also runnable manually anytime
```

Proposals it produces live in `../vegan-news-feed/proposals/`, not here — they're about that skill, so they sit next to what they propose to change.

## Example output

The first real run (2026-08-26) is preserved as-is at [`../vegan-news-feed/proposals/2026-08-26.md`](../vegan-news-feed/proposals/2026-08-26.md) — it correctly found only one day of thin, pre-schema-change history and reported honestly that there wasn't enough data to review yet, rather than inventing findings. A more typical proposal, once real week-over-week data exists, will look like the template in `SKILL.md`'s step 5: dated observations plus concrete, file-and-line-specific suggestions.

## Open items

Tracked centrally, not duplicated here — see [`../vegan-news-feed/TODO.md`](../vegan-news-feed/TODO.md) (has a section for this skill too).
