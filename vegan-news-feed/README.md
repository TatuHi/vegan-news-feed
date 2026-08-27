# Vegan News Feed

A [Claude Code](https://claude.com/claude-code) skill that acts as daily media monitoring for a small comms team: it finds fresh vegan/plant-based and animal-rights news (Finnish + English), decides what's actually worth including, writes short Finnish summaries, suggests 1-2 ready angles for the team's own social/press content, and posts one formatted digest to Discord.

It's built with a sibling skill, [`vegan-news-feed-review`](../vegan-news-feed-review/), that periodically reviews this skill's own track record and proposes improvements — without ever applying them itself. See below.

Design rationale and iteration history: see [`PROCESS.md`](PROCESS.md). Full agent instructions the skill actually runs on: see [`SKILL.md`](SKILL.md). Open items: see [`TODO.md`](TODO.md). Want to see what it actually produces before reading further? See [`example-output.md`](example-output.md) — a real sent digest, captured verbatim.

## ⚠️ Disclaimer

Every script in this repository (`fetch_feeds.py`, `post_discord.py`, `history.py`, `run_daily.sh`) was written by Claude (an AI, via Claude Code), iteratively, as documented in `PROCESS.md`. **None of it has been independently reviewed by a human for correctness, security, or safety** — it has been tested for behavior (see `PROCESS.md`'s testing notes and `evals/`), which is not the same thing as a security or code review.

If you clone and run this code — especially if you schedule it via cron, where it runs unattended with your credentials — **read it yourself first.** Don't run it blindly. The repository owner takes no responsibility for what happens if you do.

## What it looks for

**Included:**
- News where veganism/plant-based food is the actual subject, not a passing mention — product launches, research, legislation, market moves, cultural stories
- Significant business/market news in the plant-based sector — funding rounds, major launches, closures
- Animal rights and animal-welfare politics more broadly, not just food — legislation (e.g. fur farming bans, animal welfare law), EU-level decisions, advocacy org campaigns and statements, farmed-animal treatment rulings. Both Finnish and international/EU level.

**Excluded:**
- Recipes and blog posts (unless there's a real news story around one)
- Articles where "vegan" is just a side mention (e.g. a restaurant review that happens to note vegan options)
- Obvious ad content
- Single pet-rescue/animal-welfare human-interest stories with no political or societal angle (a common false-positive from animal-welfare org feeds)
- Duplicates — the same event covered by multiple outlets, or a story already sent recently without a genuine new development (see "Reliability" below)

**What it weights higher, given a choice:**
- A real development over a passive announcement — the summary has to say *what happened*, not just name the topic
- A shorter, high-quality list over padding to the cap (max 8-10 stories/day; fewer good ones beats diluting with weak ones)
- For the content-idea step specifically: a story that gives the comms team a genuine angle to build *their own* content from (a stance to take, a connection to their work) over one that's merely informative
- Topic variety over topic repetition, as a tiebreaker only — if today's news happens to be three funding rounds and nothing else, all three still make it in; the balance rule only kicks in when choosing between otherwise-equal candidates for the last slot

## Setup

**Requirements**
- Claude Code
- A Python 3.10+ interpreter available at a known absolute path (standard library only, no `pip install` needed) — see "Reliability" below for why an absolute path matters and what to do if your system `python3` is older
- A Discord webhook URL for the channel you want the digest posted to

**1. Place the skill**
Put this whole folder at `~/.claude/skills/vegan-news-feed/` (or under a project's `.claude/skills/` for a project-scoped install).

**2. Configure the webhook**
The webhook is deliberately kept *outside* this folder so it never ends up in git:
```bash
mkdir -p ~/.config/vegan-news
cp .env.example ~/.config/vegan-news/.env
chmod 600 ~/.config/vegan-news/.env
# now edit ~/.config/vegan-news/.env and set your real DISCORD_WEBHOOK_URL
```

**3. Run it manually**
In Claude Code, ask something that matches `SKILL.md`'s trigger phrasing, e.g.:
- "Aja vegan-news-feed-skilli ja lähetä tämän päivän koonti Discordiin"
- "Koosta tämän päivän vegaaniuutiset"
- "Onko tänään mitään sellaista vegaaniuutista josta olisi hyvä tehdä oma some-postaus?"
- "Täytä puuttuvat päivät historiaan" (backfill, see "Reliability" below)

Claude Code should pick the skill up automatically from its description; no explicit slash command needed.

**4. (Optional) Schedule it**
`scripts/run_daily.sh` is a cron-safe wrapper — see "Reliability" below for exactly what it handles. Example crontab line (daily at 8 AM):
```
0 8 * * * /Users/<you>/.claude/skills/vegan-news-feed/scripts/run_daily.sh >> ~/Library/Logs/vegan-news-feed.log 2>&1
```
Test it manually once before adding it to cron — it sends a real digest, since it runs the whole pipeline.

## Reliability & data integrity

This pipeline is meant to run unattended, so a fair amount of it is about failure modes rather than the core "find and summarize news" logic:

- **Transient-failure retries**: `fetch_feeds.py` retries a feed fetch up to 3 times on things that look like a momentary blip (timeout, connection reset) — but *not* on signatures of a systemic block (403, connection refused, tunnel failures), since retrying those just wastes time.
- **Mechanical near-duplicate detection**: within a single fetch, `fetch_feeds.py` recognizes when the same story shows up twice (e.g. once via a source's own feed, once via a Google News republish with a "- Publisher Name" suffix appended to the title) and keeps whichever copy has the real direct link and a proper description, not just whichever came first.
- **Cross-day duplicate suppression**: `scripts/history.py` tracks what's been sent (and what content-idea angles were suggested) so the same story doesn't repeat across consecutive days just because it's still inside the 30-hour fetch window. It also gives the skill topic-level awareness — not just exact-duplicate detection — used as a tiebreaker (never a hard exclusion) between otherwise-equal candidates.
- **Direct-link resolution**: Google News links are redirect URLs, not the real article — the skill resolves and uses the actual publisher URL in every sent message instead.
- **Missed-run backfill**: cron doesn't wake a sleeping Mac, so a missed day leaves a real gap in the history. `history.py gaps` detects days with zero recorded activity, and a documented (on-demand, not automatic) backfill workflow can retroactively fill history for recent gaps — without necessarily posting a stale digest to Discord. Bounded by a real constraint: RSS feeds are rolling windows, so this only works reliably for gaps of roughly 1-5 days.
- **Dual-channel failure alerting**: if a scheduled run fails for any reason, `run_daily.sh` posts a warning to the same Discord channel *and* fires an independent macOS notification — so a failure still surfaces even if the failure is Discord itself being unreachable.
- **Environment fragility, solved once**: `run_daily.sh` points at a specific, known-working Python install and its SSL certs rather than trusting `PATH` (which, depending on the machine, may resolve to a Python too old for this codebase's syntax), and sends requests with a browser-like User-Agent (some hosts, including Discord's own webhook endpoint, block default script user-agents).

Full detail on all of the above: `SKILL.md`'s "Puuttuvien päivien täyttäminen" and "Ajastaminen" sections, and `PROCESS.md`'s iteration history.

## Sibling skill: vegan-news-feed-review

[`vegan-news-feed-review`](../vegan-news-feed-review/) reads this skill's send history periodically (weekly by default, but runnable any time) and writes dated, specific improvement proposals to `proposals/` — sources that never contribute, thin summaries, forced-feeling content ideas, coverage gaps. **It never edits this skill's files.** Applying a proposal is always a separate, human-approved, interactive step, documented afterward in `PROCESS.md` — see that sibling skill's own README for why it's a separate skill rather than a mode of this one.

## Repo layout

```
SKILL.md              Agent instructions Claude Code actually reads to run this skill
PROCESS.md            Design history: why it's built this way, what changed and why
TODO.md                Open items, detailed enough for a fresh Claude Code session to act on
example-output.md     A real sent digest, captured verbatim
references/feeds.md   RSS source list (edit freely to add/remove sources)
scripts/
  fetch_feeds.py       Fetches, retries, and dedupes RSS feeds (stdlib only)
  post_discord.py      Posts the finished digest to the webhook, splitting long messages
  history.py           Send history: cross-day dedup, topic awareness, gap detection, backfill
  run_daily.sh          Cron-safe wrapper: env setup + dual-channel failure alerting
proposals/             Improvement proposals written by vegan-news-feed-review (never by this skill)
evals/evals.json       Realistic test prompts for checking the skill still behaves
.env.example           Template showing the required env var — no real secret in it
.gitignore              Keeps secrets/caches out of the repo
```

## Language

Sources are pulled in both Finnish and English, but every summary is always written in Finnish for consistency, regardless of the source article's language (marked with a flag when the source is non-Finnish).
