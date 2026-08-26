#!/usr/bin/env python3
"""
Lahettaa viestin Discord-webhookiin. Pilkkoo automaattisesti pitkat
viestit useampaan osaan Discordin 2000 merkin rajan takia.

Kayttaa vain Python-standardikirjastoa.

Kaytto:
    DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
        python3 post_discord.py --message-file /tmp/vegan_digest.md

    echo "testiviesti" | DISCORD_WEBHOOK_URL="..." python3 post_discord.py
"""
import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error

DISCORD_LIMIT = 2000


def chunk_message(text: str, limit: int = DISCORD_LIMIT) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = ""
    for block in text.split("\n\n"):
        candidate = (current + "\n\n" + block) if current else block
        if len(candidate) <= limit:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(block) <= limit:
                current = block
            else:
                # Yksittainen kappale on itsessaan liian pitka: pakotettu katkaisu.
                for i in range(0, len(block), limit):
                    chunks.append(block[i : i + limit])
                current = ""
    if current:
        chunks.append(current)
    return chunks


def send_chunk(webhook_url: str, content: str) -> None:
    payload = json.dumps({"content": content}).encode("utf-8")
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            # Discordin Cloudflare-suoja tiputtaa oletus-urllib-user-agentin (403/1010).
            "User-Agent": "Mozilla/5.0 (compatible; vegan-news-feed-bot/1.0)",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"Discord vastasi virheella {exc.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Webhook-kutsu epaonnistui: {exc}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Laheta viesti Discord-webhookiin")
    parser.add_argument("--message-file", type=str, default=None, help="Tiedosto jonka sisalto lahetetaan")
    parser.add_argument("--webhook-url", type=str, default=None, help="Voi antaa myos env-muuttujana DISCORD_WEBHOOK_URL")
    args = parser.parse_args()

    webhook_url = args.webhook_url or os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL puuttuu (aseta ymparistomuuttujana tai --webhook-url).", file=sys.stderr)
        sys.exit(1)

    if args.message_file:
        with open(args.message_file, "r", encoding="utf-8") as f:
            message = f.read()
    else:
        message = sys.stdin.read()

    message = message.strip()
    if not message:
        print("Tyhja viesti, ei laheteta mitaan.", file=sys.stderr)
        sys.exit(1)

    chunks = chunk_message(message)
    for i, chunk in enumerate(chunks):
        send_chunk(webhook_url, chunk)
        if i < len(chunks) - 1:
            time.sleep(1)  # kevyt rate-limit-suoja Discordin API:lle

    print(f"Lahetetty {len(chunks)} viesti(a) Discordiin.", file=sys.stderr)


if __name__ == "__main__":
    main()
