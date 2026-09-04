#!/bin/bash
# Ajaa vegan-literature-feed-skillin - joko ajastetusti (viikoittain), TAI
# suoraan terminaalista milloin tahansa manuaalisesti tarvittaessa. Sama
# ymparistoturvallisuusmalli kuin vegan-news-feed/scripts/run_daily.sh ja
# vegan-news-feed-review/scripts/run_weekly_review.sh - kaikki kolme
# skriptia ovat oppineet samat kolme bugia (Python-polku, SSL-varmenteet,
# claude-binaarin PATH-puuttuminen) yhden skillin kautta, joten uusia
# skripteja ei enaa tarvitse rakentaa yrityksen ja erehdyksen kautta.
#
# Kaytto ajastamatta (mika tahansa hetki):
#   ~/.claude/skills/vegan-literature-feed/scripts/run_weekly.sh
#
# Kaytto ajastettuna: KAYTA macOS:n LaunchAgentia, EI crontabia - samasta
# syysta kuin vegan-news-feed:ssa (cron ei aja GUI-istunnon sisalla, jolloin
# claude-komennon Keychain-pohjainen OAuth-kirjautuminen ei toimi). Ks.
# vegan-news-feed/SKILL.md:n "Ajastaminen"-osio taydelle selitykselle.
#
# Webhook-URL EI ole tassa tiedostossa: se luetaan omasta
# ~/.config/vegan-literature/.env -tiedostosta (talla hetkella sama arvo
# kuin vegan-news-feed:lla, testausmielessa - ks. README.md).

set -euo pipefail

ENV_FILE="$HOME/.config/vegan-literature/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  echo "[run_weekly.sh] Ymparistotiedostoa ei loydy: $ENV_FILE" >&2
  exit 1
fi

if [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "[run_weekly.sh] DISCORD_WEBHOOK_URL on tyhja ($ENV_FILE)." >&2
  exit 1
fi

# Sama kaksikanavainen halytysperiaate kuin run_daily.sh:ssa.
notify_failure() {
  local exit_code="${1:-$?}"
  echo "[run_weekly.sh] Ajo epaonnistui exit-koodilla $exit_code" >&2

  curl -s -o /dev/null --max-time 10 \
    -H "Content-Type: application/json" \
    -H "User-Agent: Mozilla/5.0 (compatible; vegan-literature-feed-bot/1.0)" \
    -d "{\"content\":\"⚠️ vegan-literature-feed-ajo epäonnistui (exit $exit_code). Tarkista loki koneella.\"}" \
    "$DISCORD_WEBHOOK_URL" || echo "[run_weekly.sh] Virheilmoituksen lahetys Discordiin epaonnistui." >&2

  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"exit $exit_code — tarkista loki: ~/Library/Logs/vegan-literature-feed.log\" with title \"vegan-literature-feed epäonnistui\" sound name \"Basso\"" \
      || echo "[run_weekly.sh] macOS-ilmoituksen nayttaminen epaonnistui." >&2
  fi
}
trap notify_failure ERR

PYTHON311="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
if [ ! -x "$PYTHON311" ]; then
  echo "[run_weekly.sh] Python 3.11 -asennusta ei loydy polusta $PYTHON311" >&2
  notify_failure 1
  exit 1
fi

export SSL_CERT_FILE
SSL_CERT_FILE="$("$PYTHON311" -c 'import certifi; print(certifi.where())')"
export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"

CLAUDE_BIN="$HOME/.local/bin/claude"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[run_weekly.sh] claude-komentoa ei loydy polusta $CLAUDE_BIN" >&2
  notify_failure 1
  exit 1
fi

cd "$HOME/.claude/skills/vegan-literature-feed"

# --add-dir kahdesta syysta, sama kuin vegan-news-feed-review:lla:
# 1. history.py/post_discord.py asuvat sisarskillissa (vegan-news-feed).
# 2. Kirjallisuushistoria (~/.config/vegan-literature/literature_history.json)
#    on skillikansion ulkopuolella - ei "sensitive file" -ongelmaa tassa
#    (kohde ei ole ~/.claude/skills/-hakemiston sisalla), mutta --add-dir
#    tarvitaan silti jotta Write nakee sen cwd:n ulkopuolisena polkuna.
"$CLAUDE_BIN" -p "Aja vegan-literature-feed-skilli ja tee tämän viikon kirjallisuuskooste Discordiin" \
  --allowedTools "Bash,Read,Write,WebFetch,WebSearch" \
  --add-dir "$HOME/.claude/skills/vegan-news-feed" \
  --add-dir "$HOME/.config/vegan-literature"
