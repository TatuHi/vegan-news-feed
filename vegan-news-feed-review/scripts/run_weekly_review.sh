#!/bin/bash
# Ajaa vegan-news-feed-review-skillin - joko ajastetusti, TAI suoraan
# terminaalista milloin tahansa manuaalisesti tarvittaessa. Tama skripti
# ei ITSESSAAN ole sidottu viikkoaikatauluun - se vain hoitaa saman
# ymparistoturvallisuuden (Python-polku, claude-polku, SSL, hälytykset)
# kuin vegan-news-feed/scripts/run_daily.sh, jotta katselmointi voi olla
# yhta luotettava ajaa kuin itse paapipeline.
#
# Kaytto ajastamatta (mika tahansa hetki):
#   ~/.claude/skills/vegan-news-feed-review/scripts/run_weekly_review.sh
#
# Kaytto ajastettuna: KAYTA macOS:n LaunchAgentia, EI crontabia. Cron on
# toteutettu LaunchDaemonina joka ei aja GUI-kirjautumisistunnon sisalla,
# jolloin "claude"-komennon Keychain-pohjainen OAuth-kirjautuminen ei
# toimi ("Not logged in") - taman huomasi vegan-news-feed puolella
# 2026-08-29 vasta oikealla cron-laukaisulla, ks. sen SKILL.md:n
# "Ajastaminen"-osio taydelle selitykselle ja LaunchAgent-plist-mallille.
# Sama korjaus (CLAUDE_BIN-muuttuja alla) ja sama LaunchAgent-malli
# patevat tahankin skriptiin, vaikka sita ei viela ole ajastettu.
#
# Webhook-URL EI ole tassa tiedostossa: se luetaan samasta
# ~/.config/vegan-news/.env -tiedostosta jota vegan-news-feed kayttaa (sama
# Discord-kanava, sama webhook - katselmointi-ilmoitus menee samaan paikkaan).

set -euo pipefail

ENV_FILE="$HOME/.config/vegan-news/.env"
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
else
  echo "[run_weekly_review.sh] Ymparistotiedostoa ei loydy: $ENV_FILE" >&2
  exit 1
fi

if [ -z "${DISCORD_WEBHOOK_URL:-}" ]; then
  echo "[run_weekly_review.sh] DISCORD_WEBHOOK_URL on tyhja ($ENV_FILE)." >&2
  exit 1
fi

# Sama kaksikanavainen hälytysperiaate kuin run_daily.sh:ssa - ks. sen
# kommentit tarkemmasta perustelusta miksi seka Discord etta macOS-ilmoitus.
notify_failure() {
  local exit_code="${1:-$?}"
  echo "[run_weekly_review.sh] Ajo epaonnistui exit-koodilla $exit_code" >&2

  curl -s -o /dev/null --max-time 10 \
    -H "Content-Type: application/json" \
    -H "User-Agent: Mozilla/5.0 (compatible; vegan-news-feed-review-bot/1.0)" \
    -d "{\"content\":\"⚠️ vegan-news-feed-review-ajo epäonnistui (exit $exit_code). Tarkista loki koneella.\"}" \
    "$DISCORD_WEBHOOK_URL" || echo "[run_weekly_review.sh] Virheilmoituksen lahetys Discordiin epaonnistui." >&2

  if command -v osascript >/dev/null 2>&1; then
    osascript -e "display notification \"exit $exit_code — tarkista loki: ~/Library/Logs/vegan-news-feed-review.log\" with title \"vegan-news-feed-review epäonnistui\" sound name \"Basso\"" \
      || echo "[run_weekly_review.sh] macOS-ilmoituksen nayttaminen epaonnistui." >&2
  fi
}
trap notify_failure ERR

# Sama syy kuin vegan-news-feedissa: monet koneen python3-asennukset eivat
# tue skriptien (history.py) X | None -syntaksia (vaatii 3.10+).
PYTHON311="/Library/Frameworks/Python.framework/Versions/3.11/bin/python3"
if [ ! -x "$PYTHON311" ]; then
  echo "[run_weekly_review.sh] Python 3.11 -asennusta ei loydy polusta $PYTHON311" >&2
  notify_failure 1
  exit 1
fi

export SSL_CERT_FILE
SSL_CERT_FILE="$("$PYTHON311" -c 'import certifi; print(certifi.where())')"
export PATH="/Library/Frameworks/Python.framework/Versions/3.11/bin:$PATH"

# Sama luokan ongelma kuin PYTHON311:n kanssa - cronin suppea PATH ei
# sisalla ~/.local/bin:ia, missa claude CLI asuu talla koneella. Loydettiin
# run_daily.sh:sta oikealla cron-laukaisulla 2026-08-28 (exit 127); korjattu
# ennalta ehkaisevasti myos tanne samalla logiikalla, vaikka tata skillia
# ei ole viela ajastettu.
CLAUDE_BIN="$HOME/.local/bin/claude"
if [ ! -x "$CLAUDE_BIN" ]; then
  echo "[run_weekly_review.sh] claude-komentoa ei loydy polusta $CLAUDE_BIN" >&2
  notify_failure 1
  exit 1
fi

cd "$HOME/.claude/skills/vegan-news-feed-review"

# Ei "exec" tassa: trap ERR ei laukeaisi enaa taman prosessin jalkeen.
# Ei tarvita WebFetch/WebSearch-oikeuksia - taama skilli ei hae ulkoista
# dataa, vain lukee vegan-news-feedin paikallista historiaa ja tiedostoja.
#
# --add-dir tarvitaan kahdesta erillisesta syysta:
# 1. cwd on tama skilli (vegan-news-feed-review), mutta history.py/feeds.md
#    luetaan sisarskillin (vegan-news-feed) kansiosta. Loytyi ensimmaisella
#    oikealla ajolla 2026-08-29.
# 2. Ehdotustiedosto kirjoitetaan ~/.config/vegan-news/proposals/-kansioon,
#    EI enaa vegan-news-feedin sisalle - koska ~/.claude/skills/-hakemiston
#    sisalla olevat tiedostot lasketaan Claude Codessa "sensitive file"
#    -kategoriaan, mika estaa Write-tyokalua kirjoittamasta sinne ilman
#    ihmisen lasnaoloa hyvaksymassa sita. Taman huomasi vasta samalla
#    2026-08-29 ajolla, kun ensimmainen --add-dir-korjaus ei riittanytkaan:
#    headless-istunto ei voinut kysya lupaa keneltakaan skillikansion
#    sisalle kirjoittamiseen, joten se olisi jaanyt aina kesken ajastettuna.
#    Ks. ../../vegan-news-feed/DATA_LOCATIONS.md taydelle selitykselle.
"$CLAUDE_BIN" -p "Aja vegan-news-feed-review-skilli ja tee viikkokatsaus vegan-news-feedin viimeisen viikon toiminnasta" \
  --allowedTools "Bash,Read,Write" \
  --add-dir "$HOME/.claude/skills/vegan-news-feed" \
  --add-dir "$HOME/.config/vegan-news"
