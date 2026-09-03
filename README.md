# AI Media Monitoring for Vegan/Animal-Rights Communications

Three connected AI automations, built with [Claude Code](https://claude.com/claude-code), that act as a media-monitoring desk for a small comms team working in the vegan/plant-based and animal-rights space. The first two run on a schedule, do real work unattended, and post their output to a live Discord channel — this isn't a demo, it's been running daily in production since late August 2026. The third was deliberately built to a smaller, honest scope (see its own section below) rather than padded out to look further along than it is.

**New here and not a developer?** This page is written for you — no need to click into any folder to get the gist. Each project below has its own README with full technical detail, linked at the end of its section, for anyone who wants to go deeper.

## What problem this solves

A comms team can't watch every news outlet, every scientific journal, and its own past output all day. These three tools split that job into pieces an AI agent can do reliably and on a schedule, while keeping a human in charge of anything that actually changes:

## 1. Daily news digest — [`vegan-news-feed`](vegan-news-feed/)

Every day at 13:00, an AI agent wakes up, searches Finnish and English news sources for anything genuinely newsworthy about veganism, plant-based food, or animal rights, decides what's actually worth including (not everything that merely mentions "vegan"), writes short Finnish summaries, suggests 1-2 ready angles the comms team could build their own social post or press release around, and posts one formatted digest to a Discord channel. It also keeps a history to avoid repeating yesterday's story and to catch missed days.

**See it in action:** [`example-output.md`](vegan-news-feed/example-output.md) — a real digest, sent and captured verbatim, not a mockup.

## 2. Self-review — [`vegan-news-feed-review`](vegan-news-feed-review/)

A second, independent agent that runs weekly, reads the first tool's actual track record (which sources contributed, which didn't, where coverage gaps happened), and writes a dated, evidenced improvement proposal. It's built to **never apply its own suggestions** — every change still requires a human to read the reasoning and approve it. That boundary is structural (a separate tool with separate permissions), not just a rule it's asked to follow.

## 3. Scientific literature tracking — [`vegan-literature-feed`](vegan-literature-feed/)

The same idea extended from news to peer-reviewed research: an agent connected to the PubMed API surfaces fresh studies and review articles on plant-based nutrition and animal welfare science, with enough context (study type, key finding, caveats) that a comms team could credibly write about a finding before mainstream coverage catches up. **Deliberately built as a minimum-viable first pass, not yet scheduled** — a real example of knowing when to scope something down and say so plainly, rather than over-claiming how finished it is.

## Tools and techniques used

- **[Claude Code](https://claude.com/claude-code)** as the AI agent runtime — both interactively (building/iterating) and headlessly (`claude -p`, scheduled and unattended)
- **Google News RSS & the PubMed E-utilities API** for sourcing, with real, verified debugging of API quirks (e.g. discovering Google News ranks by relevance rather than recency — see the design history below)
- **Discord webhooks** for publishing
- **macOS LaunchAgents** for reliable scheduling, including recovering from a Mac being asleep at run time
- Plain Python (standard library only) for the deterministic parts — fetching, deduplicating, sending, record-keeping — deliberately kept separate from the parts that need real judgment, which are left to the agent

## How it was actually built

Every script here was written by Claude, iteratively, in conversation — not generated once and left alone. Each project's `PROCESS.md` is a running, honest design log: what was tried, what broke in real use (not just in theory), how it was diagnosed, and why each decision was made. It's worth reading if you want to see how the tool was actually developed, including real production bugs found and fixed after the fact (e.g. a missed news item traced all the way to a specific API behavior, verified, and corrected).

**Note on AI-written code:** none of this has been independently security-reviewed by a human — see each project's own disclaimer before running it yourself. That's stated plainly in each README, not hidden — part of using AI tools responsibly is being clear about what has and hasn't been verified.

## Links for going deeper

| Project | What it's for | Read next |
|---|---|---|
| Daily news digest | The core automation | [`vegan-news-feed/README.md`](vegan-news-feed/README.md) |
| Self-review | How the review/propose loop works | [`vegan-news-feed-review/README.md`](vegan-news-feed-review/README.md) |
| Literature tracking | Extending it to scientific research | [`vegan-literature-feed/README.md`](vegan-literature-feed/README.md) |
