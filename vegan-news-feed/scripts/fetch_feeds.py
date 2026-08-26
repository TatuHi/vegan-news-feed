#!/usr/bin/env python3
"""
Hakee RSS-syotteet references/feeds.md -tiedostosta, suodattaa tuoreet
kohteet, poistaa duplikaatit (linkin ja normalisoidun otsikon perusteella -
katso normalize_title) ja tulostaa JSON-listan.

Kayttaa vain Python-standardikirjastoa, jotta skilli toimii ilman
lisaasennuksia missa tahansa Claude Code -ymparistossa.

Kaytto:
    python3 fetch_feeds.py --hours 30 --output /tmp/vegan_news_raw.json
    python3 fetch_feeds.py --feeds-file /polku/omat_feedit.md
"""
import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib.parse import urlparse, urlsplit, urlunsplit, quote

DEFAULT_FEEDS_FILE = Path(__file__).resolve().parent.parent / "references" / "feeds.md"
USER_AGENT = "vegan-news-feed-skill/1.0 (+https://github.com/) Python-urllib"
TIMEOUT_SECONDS = 15
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2
# Tunnistetaan sandboxatun/whitelistatun ymparistoproxyn tyypilliset virheet,
# jotta kayttajalle voidaan antaa oikea vihje eika vain "epaonnistui" -viesti.
# Nama eivat ole "tilapaisia" virheita (koko ymparisto on estetty), joten
# niita ei kannata yrittaa uudelleen - vain oikeasti hetkellisia virheita
# (timeout, connection reset, 5xx) yritetaan uudelleen alla.
NETWORK_BLOCK_HINTS = ("tunnel connection failed", "403", "connection refused")


def normalize_url(url: str) -> str:
    """Prosentti-enkoodaa URL:n ei-ASCII-merkit (esim. 'ä', 'ö') ennen pyyntoa.

    urllib.request ei suostu lahettamaan pyyntoa jos URL sisaltaa raakoja
    Unicode-merkkeja (ValueError/UnicodeEncodeError). feeds.md:ssa URL:t on
    tarkoitettu pidettavan ihmisluettavassa (ei-enkoodatussa) muodossa, joten
    enkoodaus tehdaan tassa aina ennen verkkokutsua sen sijaan etta feeds.md:n
    muokkaajan pitaisi muistaa tehda se itse.
    """
    parts = urlsplit(url)
    # Path ja query voivat sisaltaa ei-ASCII-merkkeja (esim. suomenkieliset
    # hakusanat) - quote() jattaa jo-enkoodatut %XX-sekvenssit koskematta.
    path = quote(parts.path, safe="/%")
    query = quote(parts.query, safe="=&%+:,")
    return urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def extract_feed_urls(feeds_file: Path) -> list[str]:
    text = feeds_file.read_text(encoding="utf-8")
    urls = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("http://") or line.startswith("https://"):
            urls.append(line)
    return urls


def guess_language(url: str) -> str:
    if "hl=fi" in url or "gl=FI" in url or "ceid=FI" in url:
        return "fi"
    if ".fi/" in url or urlparse(url).netloc.endswith(".fi"):
        return "fi"
    return "en"


def fetch_xml(url: str) -> ET.Element | None:
    safe_url = normalize_url(url)
    req = urllib.request.Request(safe_url, headers={"User-Agent": USER_AGENT})

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                data = resp.read()
            return ET.fromstring(data)
        except Exception as exc:  # verkkovirhe, timeout, huono XML, jne.
            msg = str(exc).lower()
            if any(hint in msg for hint in NETWORK_BLOCK_HINTS):
                # Ei tilapainen: koko ymparisto on estetty, uudelleenyritys ei auta.
                print(
                    f"[varoitus] {url}: {exc} "
                    "— vaikuttaa ymparistotason verkkoestolta (esim. sandboxin "
                    "whitelistattu proxy), ei feedin omalta vialta. Jos tama toistuu "
                    "kaikilla feedeilla, aja hakuvaihe sen sijaan Claude-agentin "
                    "WebFetch-tyokalulla per feed (ks. SKILL.md vaihe 1, 'Jos "
                    "fetch_feeds.py ei paase verkkoon') sen sijaan etta yritat "
                    "korjata taman skriptin verkkoasetuksia.",
                    file=sys.stderr,
                )
                return None

            if attempt < MAX_ATTEMPTS:
                print(
                    f"[uudelleenyritys {attempt}/{MAX_ATTEMPTS - 1}] {url}: {exc} "
                    f"— yritetaan uudelleen {RETRY_DELAY_SECONDS}s kuluttua.",
                    file=sys.stderr,
                )
                time.sleep(RETRY_DELAY_SECONDS)
            else:
                print(f"[varoitus] {url}: {exc} (yritetty {MAX_ATTEMPTS} kertaa)", file=sys.stderr)
                return None


def parse_pubdate(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        return None


def strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text or "").strip()


def parse_rss_items(root: ET.Element, source_lang: str) -> list[dict]:
    items = []
    channel = root.find("channel")
    channel_title = None
    if channel is not None:
        title_el = channel.find("title")
        channel_title = title_el.text.strip() if title_el is not None and title_el.text else None

    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        date_el = item.find("pubDate")
        desc_el = item.find("description")
        source_el = item.find("source")

        title = title_el.text.strip() if title_el is not None and title_el.text else None
        link = link_el.text.strip() if link_el is not None and link_el.text else None
        if not title or not link:
            continue

        published = parse_pubdate(date_el.text if date_el is not None else None)
        source_name = (
            source_el.text.strip()
            if source_el is not None and source_el.text
            else channel_title or urlparse(link).netloc
        )

        items.append(
            {
                "title": title,
                "link": link,
                "source": source_name,
                "published": published.isoformat() if published else None,
                "language": source_lang,
                "summary": strip_html(desc_el.text) if desc_el is not None and desc_el.text else "",
            }
        )
    return items


def normalize_title(title: str, source: str) -> str:
    """Normalisoi otsikon lahes-duplikaattien tunnistusta varten.

    Google News liittaa lahes aina otsikon perään " - Julkaisijan nimi",
    jolloin sama juttu nakyy raakadatassa kahdesti (kerran suoraan lahteen
    omasta feedista, kerran Google Newsin kautta hieman eri muotoisella
    otsikolla). Poistetaan tama tunnettu lahde-suffiksi, yhtenaistetaan
    lainausmerkit/valimerkit/valilyonnit ja pienennetaan kirjaimet.

    HUOM: tama ei yrita tunnistaa eri julkaisijoiden itse kirjoittamia,
    kokonaan eri sanamuotoisia otsikoita samasta tapahtumasta (esim.
    "EU hylkasi X" vs "Lehdistotiedote: MEPs ehdottavat Y") - sellainen
    vaatii sisallon ymmartamista eika ole mekaanisesti luotettavasti
    ratkaistavissa. Se jaa agentin harkintaan (ks. SKILL.md vaihe 2).
    """
    t = title.strip()

    # 1) Poista tunnettu " - <source>" -suffiksi jos se tasmaa taman
    #    kohteen source-kenttaan (turvallisin tapa: emme arvaa, tarkistamme).
    suffix = f" - {source.strip()}"
    if t.lower().endswith(suffix.lower()):
        t = t[: -len(suffix)].strip()
    else:
        # 2) Varapolku: geneerinen "... - Julkaisijan Nimi" -loppu, kun
        #    source-kentta ei tasmaa tarkalleen (esim. Google News kayttaa
        #    hieman eri valimerkkia kuin alkuperainen feed). Vaaditaan ettei
        #    jaljelle jaava otsikko lyhene liikaa, jotta ei vahingossa
        #    katkaista otsikkoa jonka oma sisalto paattyy " - johonkin".
        m = re.match(r"^(.{15,}?)\s+-\s+[^-]{2,60}$", t)
        if m:
            t = m.group(1).strip()

    t = unicodedata.normalize("NFKC", t)
    t = t.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    t = re.sub(r"[^\w\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t


def _item_quality(it: dict) -> tuple:
    """Vertailuarvo kahden duplikaatin valilla: isompi voittaa.

    Google Newsin uudelleenohjauslinkki (news.google.com/rss/articles/...)
    ei ole artikkelin oikea osoite (ks. SKILL.md vaihe 3) - jos sama juttu
    loytyy sekä suoraan lahteesta etta Google Newsin kautta, halutaan
    sailyttaa se versio jolla on jo valmiiksi oikea suora linkki ja
    (yleensa) oikea kuvaus pelkan otsikon toiston sijaan.
    """
    has_direct_link = "news.google.com" not in it["link"]
    summary_len = len((it.get("summary") or "").strip())
    return (has_direct_link, summary_len)


def dedupe(items: list[dict]) -> list[dict]:
    kept_by_title = {}
    kept_by_link = {}
    result = []

    for it in items:
        key_link = it["link"].split("?")[0].rstrip("/")
        key_title = normalize_title(it["title"], it["source"])
        existing = kept_by_title.get(key_title) or kept_by_link.get(key_link)

        if existing is None:
            result.append(it)
            kept_by_title[key_title] = it
            kept_by_link[key_link] = it
            continue

        # Duplikaatti loytyi: sailytetaan parempi versio (suora linkki ja/tai
        # pidempi oikea kuvaus) sen sijaan etta aina ensimmaisena nahty voittaisi.
        if _item_quality(it) > _item_quality(existing):
            result[result.index(existing)] = it
            kept_by_title[key_title] = it
            kept_by_link[key_link] = it

    return result


def main():
    parser = argparse.ArgumentParser(description="Hae ja suodata vegaaniuutis-RSS-syotteet")
    parser.add_argument("--feeds-file", type=Path, default=DEFAULT_FEEDS_FILE, help="Polku feeds.md-tiedostoon")
    parser.add_argument("--hours", type=int, default=30, help="Kuinka monen tunnin sisalla julkaistut otetaan mukaan")
    parser.add_argument("--output", type=Path, default=None, help="Kirjoita JSON tiedostoon (oletus: stdout)")
    args = parser.parse_args()

    if not args.feeds_file.exists():
        print(f"Feeds-tiedostoa ei loydy: {args.feeds_file}", file=sys.stderr)
        sys.exit(1)

    urls = extract_feed_urls(args.feeds_file)
    if not urls:
        print("Feeds-tiedostosta ei loytynyt yhtaan URL:ia.", file=sys.stderr)
        sys.exit(1)

    cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
    all_items = []

    for url in urls:
        root = fetch_xml(url)
        if root is None:
            continue
        lang = guess_language(url)
        items = parse_rss_items(root, lang)
        all_items.extend(items)

    deduped = dedupe(all_items)

    # Suodata tuoreet. Jos julkaisuaikaa ei saatu parsittua, pidetaan mukana
    # varmuuden vuoksi (mieluummin nayttaa liikaa kuin hukkaa relevantin uutisen).
    fresh = []
    for it in deduped:
        if it["published"] is None:
            fresh.append(it)
            continue
        pub_dt = datetime.fromisoformat(it["published"])
        if pub_dt >= cutoff:
            fresh.append(it)

    fresh.sort(key=lambda x: x["published"] or "", reverse=True)

    output_text = json.dumps(fresh, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Kirjoitettu {len(fresh)} uutista tiedostoon {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
