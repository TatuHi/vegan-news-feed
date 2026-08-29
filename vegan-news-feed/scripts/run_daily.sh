#!/bin/bash
# Ajaa vegan-news-feed-skillin cronista/ajastetusti.
#
# Cronin PATH on suppea eika lataa .zshrc/.bash_profile-tiedostoja, joten tama
# skripti asettaa tarvittavat polut ja ymparistomuuttujat itse sen sijaan etta
# luottaisi kayttajan interaktiivisen shellin asetuksiin.
#
# Webhook-URL EI ole tassa tiedostossa eika crontabissa, vaan omassa
# 0600-oikeuksin suojatussa tiedostossa: ~/.config/vegan-news/.env

set -euo pipefail

ENV_FILE="$HOME/.config/vegan-news/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  echo "[run_daily.sh] Ymparistotiedostoa ei loydy: $ENV_FILE" >&2
  exit 1
fi

if [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "[run_daily.sh] DISCORD_WEBHOOK_URL on tyhja ($ENV_FILE)." >&2
  exit 1
fi

# Alkaen tasta kohdasta webhook on tiedossa, joten epaonnistumisesta
# voidaan ilmoittaa Discordiin sen sijaan etta ajo jaa hiljaa roikkumaan
# lokitiedostoon jota kukaan ei lue.
# $1 annetaan eksplisiittisesti kun funktiota kutsutaan suoraan (ei trapin
# kautta), koska $? olisi silloin edellisen onnistuneen komennon (esim. echo)
# koodi eika oikea virhekoodi.
#
# Kaksi RIIPPUMATONTA hälytyskanavaa: jos Discord-webhook on itse syy
# epäonnistumiseen (poistettu/vaihdettu webhook, Discordin oma katko), pelkkä
# Discord-hälytys ei koskaan tavoittaisi ketään. macOS-ilmoitus ei riipu
# verkosta eika webhookista lainkaan, joten se toimii vaikka Discord-osuus
# olisi juuri se rikkoutunut palanen.
notify_failure() {
  local exit_code="${1:-$?}"
  echo "[run_daily.sh] Ajo epaonnistui exit-koodilla $exit_code" >&2

  curl -s -o /dev/null --max-time 10 \
    -H "Content-Type: application/json" \
    -H "User-Agent: Mozilla/5.0 (compatible; vegan-news-feed-bot/1.0)" \
    -d "{\"content\":\"⚠️ vegan-news-feed-ajo epäonnistui (exit $exit_code). Tarkista loki koneella.\"}" \
    "$DISCORD_WEBHOOK_URL" || echo "[run_daily.sh] Virheilmoituksen lahetys Discordiin epaonnistui." >&2

  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"exit $exit_code — tarkista loki: ~/Library/Logs/vegan-news-feed.log\" with title \"vegan-news-feed epäonnistui\" sound name \"Basso\"" \
      || echo "[run_daily.sh] macOS-ilmoituksen nayttaminen epaonnistui." >&2
  fi
}
trap notify_failure ERR

# Tama koneen /usr/bin/python3 ja Anacondan python3 eivat toimi tassa
# skillissa (vanha SSL/xcrun-tila tai puuttuva list[str]-tuki) - kaytetaan
# python.org:n 3.11-asennusta suoraan polulla, ei PATH-hausta.
PYTHON311="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
if [ ! -x "$PYTHON311" ]; then
  echo "[run_daily.sh] Python 3.11 -asennusta ei loydy polusta $PYTHON311" >&2
  notify_failure 1
  exit 1
fi

export SSL_CERT_FILE
SSL_CERT_FILE="$("$PYTHON311" -c 'import certifi; print(certifi.where())')"
export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"

# Sama luokan ongelma kuin PYTHON311:n kanssa, loydettiin vasta oikealla
# cron-laukaisulla 2026-08-28 (exit 127, "claude: command not found") -
# cronin suppea PATH ei sisalla ~/.local/bin:ia, missa claude CLI asuu
# talla koneella. Interaktiiviset ajot eivat koskaan paljastaneet tata,
# koska oma shell loytaa sen aina. Kaytetaan siis suoraa polkua, ei PATH:ia.
CLAUDE_BIN="$HOME/.local/bin/claude"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[run_daily.sh] claude-komentoa ei loydy polusta $CLAUDE_BIN" >&2
  notify_failure 1
  exit 1
fi

cd "$HOME/.claude/skills/vegan-news-feed"

# Ei "exec" tassa: trap ERR ei laukeaisi enaa taman prosessin jalkeen, jos
# claude korvaisi koko shell-prosessin.
"$CLAUDE_BIN" -p "Aja vegan-news-feed-skilli ja lähetä tämän päivän koonti Discordiin" \
  --allowedTools "Bash,Read,Write,WebFetch,WebSearch"
