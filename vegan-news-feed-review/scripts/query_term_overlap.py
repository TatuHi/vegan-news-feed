#!/usr/bin/env python3
"""
Analysoi Google News RSS -hakujen (news.google.com/rss/search) OR-listan
yksittaisten termien kontribuution ja paallekkaisyyden: kuinka moni kunkin
termin loytamista otsikoista loytyy myos jonkin toisen (SAMAN kieli-/
alue-asetuksen, ks. alla) termin kautta, ja kuinka moni termi ei tuota
tuloksia lainkaan.

Motivaatio: vegan-news-feed/PROCESS.md:n iteraatio 9 (2026-09-02) loysi
ja korjasi kaksi bugia yhdessa Google News -haussa (relevanssijarjestys
tuoreussuodatuksen sijaan, puuttuva hakusana) manuaalisesti kysely
kerrallaan - tama skripti pakkaa saman tekniikan uudelleenkaytettavaksi.
YLEISKAYTTOINEN, EI sidottu mihinkaan tiettyyn skilliin: kayttaa vain
Python-standardikirjastoa, ja lukee syotteensa joko feeds.md-tyylisesta
tiedostosta tai suoraan komentoriviltä - ks. alla "Kaytto".

Ei tunnista eri julkaisijan ERI SANOIN kirjoittamaa samaa tapahtumaa
(esim. "EU hylkasi X" vs "Lehdistotiedote: MEPs ehdottavat Y" samasta
aanestyksesta) samaksi kohteeksi - vain mekaanisesti lahes identtiset
otsikot (sama tarina, mahdollisesti eri termin kautta loydettyna)
tunnistetaan paallekkaisiksi. Tama tarkoittaa etta paallekkaisyysluvut
ovat ALARAJA todellisesta paallekkaisyydesta, ei tarkka luku - sama
periaatteellinen rajoitus kuin fetch_feeds.py:n normalize_title():lla.

Termien vertailu tehdaan VAIN saman (hl, gl, ceid) - eli saman kieli-/
alue-asetuksen - sisalla, koska esim. suomenkielisen ja englanninkielisen
haun tuloksia ei ole mielekasta verrata paallekkaisyyden suhteen.

Kaytto:
    # Poimii kaikki news.google.com/rss/search -rivit tiedostosta ja
    # analysoi jokaisen (hl,gl,ceid)-ryhman termit erikseen:
    python3 query_term_overlap.py \\
        --feeds-file ~/.claude/skills/vegan-news-feed/references/feeds.md \\
        --when 30d --output /tmp/overlap_report.json

    # Tai suoraan annetut termit (vaatii --hl/--gl/--ceid):
    python3 query_term_overlap.py \\
        --terms veganismi kasviperainen turkistarhaus \\
        --hl fi --gl FI --ceid FI:fi --when 14d
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

USER_AGENT = "vegan-news-feed-review-skill/1.0 Python-urllib"
TIMEOUT_SECONDS = 20
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2
BETWEEN_QUERIES_DELAY_SECONDS = 1


def fetch_xml(url: str) -> ET.Element | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                return ET.fromstring(resp.read())
        except Exception as exc:  # verkkovirhe, timeout, huono XML, jne.
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


def normalize_title(title: str) -> str:
    """Karkea otsikon normalisointi mekaanista paallekkaisyystunnistusta varten.

    Ei yrita tunnistaa eri julkaisijan eri sanoin kirjoittamaa samaa
    tapahtumaa - vain lahes identtiset otsikot (esim. sama Google News
    -osuma loytynyt kahden eri termin kautta) tunnistetaan.
    """
    t = title.strip().lower()
    t = re.sub(r"\s*-\s*[^-]{2,60}$", "", t)  # karkea " - Julkaisija" -paatteen riisunta
    t = re.sub(r"[^\w\s]", "", t, flags=re.UNICODE)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def extract_search_queries(feeds_file: Path) -> list[tuple[str, str, str, str]]:
    """Poimii kaikki news.google.com/rss/search -rivit: palauttaa listan (raw_q, hl, gl, ceid)."""
    out = []
    for line in feeds_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("http") or "news.google.com/rss/search" not in line:
            continue
        parsed = urllib.parse.urlsplit(line)
        qs = urllib.parse.parse_qs(parsed.query)
        q = qs.get("q", [""])[0]
        if not q:
            continue
        out.append((q, qs.get("hl", ["en"])[0], qs.get("gl", ["US"])[0], qs.get("ceid", ["US:en"])[0]))
    return out


def split_terms(raw_q: str) -> list[str]:
    """Riisuu tunnetun when:Nd-maareen ja pilkkoo OR-listan yksittaisiksi termeiksi."""
    q = re.sub(r"\s+when:\S+\s*$", "", raw_q.strip(), flags=re.IGNORECASE)
    q = q.strip().strip("()").strip()
    parts = re.split(r"\s+OR\s+", q)
    return [p.strip() for p in parts if p.strip()]


def query_term(term: str, hl: str, gl: str, ceid: str, when: str) -> list[dict]:
    params = {"q": f"{term} when:{when}", "hl": hl, "gl": gl, "ceid": ceid}
    url = f"https://news.google.com/rss/search?{urllib.parse.urlencode(params)}"
    root = fetch_xml(url)
    if root is None:
        return []
    items = []
    for item in root.iter("item"):
        title_el = item.find("title")
        if title_el is None or not title_el.text:
            continue
        link_el = item.find("link")
        date_el = item.find("pubDate")
        source_el = item.find("source")
        items.append(
            {
                "title": title_el.text.strip(),
                "link": link_el.text.strip() if link_el is not None and link_el.text else "",
                "published": date_el.text.strip() if date_el is not None and date_el.text else "",
                "source": source_el.text.strip() if source_el is not None and source_el.text else "",
            }
        )
    return items


def analyze_locale_group(terms: list[str], hl: str, gl: str, ceid: str, when: str) -> list[dict]:
    per_term = {}
    for term in terms:
        if term in per_term:
            continue  # sama termi esiintyy useammalla rivilla - ei kysytä kahdesti
        items = query_term(term, hl, gl, ceid, when)
        keyed = {}
        for it in items:
            key = normalize_title(it["title"])
            if key and key not in keyed:
                keyed[key] = it
        per_term[term] = keyed
        time.sleep(BETWEEN_QUERIES_DELAY_SECONDS)

    report = []
    for term, keyed in per_term.items():
        other_keys = set()
        for other_term, other_keyed in per_term.items():
            if other_term != term:
                other_keys |= set(other_keyed.keys())
        own_keys = set(keyed.keys())
        overlap = own_keys & other_keys
        unique = own_keys - other_keys
        total = len(own_keys)
        report.append(
            {
                "term": term,
                "hl": hl,
                "gl": gl,
                "ceid": ceid,
                "total_items": total,
                "unique_items": len(unique),
                "overlapping_items": len(overlap),
                "redundancy_ratio": round(len(overlap) / total, 2) if total else None,
                "dead_term": total == 0,
                "unique_examples": [keyed[k]["title"] for k in list(unique)[:3]],
            }
        )
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Analysoi Google News RSS -haun OR-termien kontribuution ja paallekkaisyyden"
    )
    parser.add_argument(
        "--feeds-file", type=Path, help="feeds.md-tyylinen tiedosto, jonka news.google.com/rss/search -rivit analysoidaan"
    )
    parser.add_argument("--terms", nargs="+", help="Suoraan annetut termit (vaatii --hl/--gl/--ceid)")
    parser.add_argument("--hl", type=str, default=None)
    parser.add_argument("--gl", type=str, default=None)
    parser.add_argument("--ceid", type=str, default=None)
    parser.add_argument("--when", type=str, default="30d", help="Googlen oma tuoreussuodatin, esim. 7d/30d (oletus 30d)")
    parser.add_argument("--output", type=Path, default=None, help="Kirjoita JSON tiedostoon (oletus: stdout)")
    args = parser.parse_args()

    # locale_key (hl,gl,ceid) -> termilista, jotta vertailu pysyy saman
    # kieli-/alue-asetuksen sisalla vaikka termit tulisivat useammalta feeds.md-rivilta.
    groups: dict[tuple[str, str, str], list[str]] = {}

    if args.feeds_file:
        if not args.feeds_file.exists():
            print(f"Feeds-tiedostoa ei loydy: {args.feeds_file}", file=sys.stderr)
            sys.exit(1)
        for raw_q, hl, gl, ceid in extract_search_queries(args.feeds_file):
            groups.setdefault((hl, gl, ceid), [])
            for term in split_terms(raw_q):
                if term not in groups[(hl, gl, ceid)]:
                    groups[(hl, gl, ceid)].append(term)

    if args.terms:
        if not (args.hl and args.gl and args.ceid):
            print("--terms vaatii myos --hl, --gl ja --ceid.", file=sys.stderr)
            sys.exit(1)
        key = (args.hl, args.gl, args.ceid)
        groups.setdefault(key, [])
        for term in args.terms:
            if term not in groups[key]:
                groups[key].append(term)

    if not groups:
        print("Ei termeja analysoitavaksi - anna --feeds-file ja/tai --terms.", file=sys.stderr)
        sys.exit(1)

    full_report = []
    for (hl, gl, ceid), terms in groups.items():
        full_report.extend(analyze_locale_group(terms, hl, gl, ceid, args.when))

    output_text = json.dumps(full_report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Kirjoitettu raportti {len(full_report)} termille tiedostoon {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
