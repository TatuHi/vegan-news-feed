#!/usr/bin/env python3
"""
Hakee tuoreet PubMed-artikkelit NCBI:n E-utilities-rajapinnasta (esearch ->
esummary -> efetch), suodattaa julkaisupäivän mukaan ja tulostaa JSON-listan.

PubMed indeksoi vain vertaisarvioituja lehtiartikkeleita (ei preprinttejä),
joten sen kautta löytyvät kohteet ovat jo lähtökohtaisesti "peer-reviewed
only" -kriteerin mukaisia - tätä ei tarvitse tarkistaa erikseen agentin
toimesta (vrt. WebSearch-taydentavan haun tulokset, jotka VAATIVAT tämän
tarkistuksen, ks. SKILL.md vaihe 1-2).

PubMed kattaa hyvin ravitsemus-/terveys- ja eläinkognitiotutkimuksen, mutta
HEIKOSTI maatalous-/ympäristö-/politiikkatutkimuksen (ei biolääketieteellistä
tietokantaa) - tämä on tunnettu, dokumentoitu aukko joka paikataan SKILL.md:n
vaiheessa 1 kohdennetulla WebSearch-haulla, ei tässä skriptissä.

Kayttaa vain Python-standardikirjastoa.

Kaytto:
    python3 fetch_pubmed.py --days 7 --output /tmp/vegan_literature_raw.json
    python3 fetch_pubmed.py --days 14 --retmax 40 --query '"vegan diet"[tiab]'
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL_NAME = "vegan-literature-feed-skill"
USER_AGENT = f"{TOOL_NAME}/1.0 Python-urllib"
TIMEOUT_SECONDS = 20
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2

# Laaja OR-kysely joka kattaa kaikki neljä aihepiiriä (ravitsemus/terveys,
# elainkognitio/-tuntoisuus, elaintuotannon ymparistovaikutus, elainpolitiikka
# ja -oikeus) - [tiab] = otsikko+abstrakti. Tama on tarkoituksella laaja
# aloituspiste, ei viimeistelty hakulauseke - tarkennettava kayttokokemuksen
# perusteella (ks. TODO.md: "references/sources.md kuratoitujen hakusanojen
# ja lehti-RSS:ien listaksi" on viela tekematta).
DEFAULT_QUERY = (
    '("vegan diet"[tiab] OR "plant-based diet"[tiab] OR "plant-based nutrition"[tiab] '
    'OR "vegetarian diet"[tiab] OR "animal welfare"[tiab] OR "animal sentience"[tiab] '
    'OR "animal cognition"[tiab] OR "animal ethics"[tiab] OR "animal rights"[tiab] '
    'OR ("livestock"[tiab] AND "environmental impact"[tiab]) '
    'OR ("meat production"[tiab] AND "climate"[tiab]) '
    'OR ("animal agriculture"[tiab] AND "policy"[tiab]))'
)


def _http_get_json(url: str) -> dict | None:
    return json.loads(_http_get(url) or "null")


def _http_get(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
                return resp.read().decode("utf-8")
        except Exception as exc:  # verkkovirhe, timeout, 5xx, jne.
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


def esearch(query: str, days: int, retmax: int) -> list[str]:
    params = {
        "db": "pubmed",
        "term": query,
        "retmax": str(retmax),
        "retmode": "json",
        "datetype": "pdat",
        "reldate": str(days),
        "tool": TOOL_NAME,
    }
    url = f"{EUTILS_BASE}/esearch.fcgi?{urllib.parse.urlencode(params)}"
    data = _http_get_json(url)
    if not data:
        return []
    return data.get("esearchresult", {}).get("idlist", [])


def esummary(pmids: list[str]) -> dict:
    """Palauttaa pmid -> {title, journal, pubdate, pub_types} -sanakirjan."""
    if not pmids:
        return {}
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "json", "tool": TOOL_NAME}
    url = f"{EUTILS_BASE}/esummary.fcgi?{urllib.parse.urlencode(params)}"
    data = _http_get_json(url)
    if not data:
        return {}

    result = data.get("result", {})
    out = {}
    for uid in result.get("uids", []):
        doc = result.get(uid, {})
        out[uid] = {
            "title": (doc.get("title") or "").strip().rstrip("."),
            "journal": doc.get("fulljournalname") or doc.get("source") or "",
            "pubdate": doc.get("pubdate") or doc.get("sortpubdate") or "",
            "pub_types": doc.get("pubtype") or [],
        }
    return out


def efetch_abstracts(pmids: list[str]) -> dict:
    """Palauttaa pmid -> abstraktiteksti -sanakirjan (tyhja merkkijono jos ei abstraktia)."""
    if not pmids:
        return {}
    params = {"db": "pubmed", "id": ",".join(pmids), "rettype": "abstract", "retmode": "xml", "tool": TOOL_NAME}
    url = f"{EUTILS_BASE}/efetch.fcgi?{urllib.parse.urlencode(params)}"
    xml_text = _http_get(url)
    if not xml_text:
        return {}

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as exc:
        print(f"[varoitus] efetch-vastauksen XML ei jasenny: {exc}", file=sys.stderr)
        return {}

    out = {}
    for article in root.iter("PubmedArticle"):
        pmid_el = article.find(".//PMID")
        if pmid_el is None or not pmid_el.text:
            continue
        pmid = pmid_el.text.strip()
        parts = []
        for abstract_text in article.iter("AbstractText"):
            label = abstract_text.get("Label")
            text = "".join(abstract_text.itertext()).strip()
            if not text:
                continue
            parts.append(f"{label}: {text}" if label else text)
        out[pmid] = " ".join(parts)
    return out


def main():
    parser = argparse.ArgumentParser(description="Hae tuoreet PubMed-artikkelit (esearch+esummary+efetch)")
    parser.add_argument("--query", type=str, default=DEFAULT_QUERY, help="PubMed-hakulauseke (oletus: laaja aihepiirikysely)")
    parser.add_argument("--days", type=int, default=7, help="Kuinka monen paivan sisalla julkaistut (oletus 7)")
    parser.add_argument("--retmax", type=int, default=30, help="Enimmaismaara tuloksia (oletus 30)")
    parser.add_argument("--output", type=Path, default=None, help="Kirjoita JSON tiedostoon (oletus: stdout)")
    args = parser.parse_args()

    pmids = esearch(args.query, args.days, args.retmax)
    if not pmids:
        output_text = json.dumps([], ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(output_text, encoding="utf-8")
            print(f"Ei tuloksia. Kirjoitettu tyhja lista tiedostoon {args.output}", file=sys.stderr)
        else:
            print(output_text)
        return

    summaries = esummary(pmids)
    abstracts = efetch_abstracts(pmids)

    items = []
    for pmid in pmids:
        summ = summaries.get(pmid)
        if not summ or not summ.get("title"):
            continue
        items.append(
            {
                "title": summ["title"],
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                "source": summ["journal"],
                "published": summ["pubdate"],
                "language": "en",
                "summary": abstracts.get(pmid, ""),
                "pub_types": summ["pub_types"],
                "pmid": pmid,
            }
        )

    output_text = json.dumps(items, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(output_text, encoding="utf-8")
        print(f"Kirjoitettu {len(items)} artikkelia tiedostoon {args.output}", file=sys.stderr)
    else:
        print(output_text)


if __name__ == "__main__":
    main()
