#!/usr/bin/env python3
"""
Eval 6:n deterministinen, skriptitason testi (ei agenttia tarvita).

Testaa suoraan fetch_feeds.py:n normalize_title()/dedupe()-funktioita
keinotekoisella Google News -republish-parilla (sama tarina kahdesti: yksi
alkuperäisen lähteen omasta feedistä, yksi Google Newsin kautta "- Julkaisija"
-päätteellä ja uudelleenohjauslinkillä) plus yhdellä kontrolliuutisella joka
ei saa poistua.

Vaatii Python 3.10+ (fetch_feeds.py:n `list[str]`-syntaksi):
    /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 test_eval6_dedupe.py

Ajettu ja vahvistettu PASS 2026-10-22, ks. PROCESS.md.
"""
import importlib.util
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"


def load_fetch_feeds():
    spec = importlib.util.spec_from_file_location("fetch_feeds", SCRIPTS_DIR / "fetch_feeds.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    ff = load_fetch_feeds()

    items = [
        {
            "title": "EU hyväksyi uuden eläinten hyvinvointidirektiivin",
            "link": "https://esimerkkiuutiset.fi/eu-elainten-hyvinvointidirektiivi",
            "source": "Esimerkkiuutiset",
            "published": "2026-10-22T08:00:00+00:00",
            "language": "fi",
            "summary": "EU hyväksyi tänään uuden direktiivin, joka tiukentaa tuotantoeläinten hyvinvointivaatimuksia kaikissa jäsenmaissa vuodesta 2028 alkaen.",
        },
        {
            "title": "EU hyväksyi uuden eläinten hyvinvointidirektiivin - Esimerkkiuutiset",
            "link": "https://news.google.com/rss/articles/CBMiFakeGoogleNewsRedirectLinkExample",
            "source": "Esimerkkiuutiset",
            "published": "2026-10-22T08:05:00+00:00",
            "language": "fi",
            "summary": "EU hyväksyi uuden eläinten hyvinvointidirektiivin&nbsp;&nbsp;Esimerkkiuutiset",
        },
        {
            "title": "Toinen, täysin eri uutinen samalta päivältä",
            "link": "https://esimerkkiuutiset.fi/toinen-eri-uutinen",
            "source": "Esimerkkiuutiset",
            "published": "2026-10-22T09:00:00+00:00",
            "language": "fi",
            "summary": "Tämä on eri tapahtuma eikä liity mitenkään ensimmäiseen pariin.",
        },
    ]

    result = ff.dedupe(items)
    print(f"Tulos ({len(result)} kohdetta):")
    for r in result:
        print(" -", r["title"], "|", r["link"])

    assert len(result) == 2, f"ODOTETTIIN 2 kohdetta, saatiin {len(result)}"
    kept = [r for r in result if "hyvinvointidirektiivin" in r["title"].lower()]
    assert len(kept) == 1, f"ODOTETTIIN tasan yksi säilynyt versio, saatiin {len(kept)}"
    assert "news.google.com" not in kept[0]["link"], "VIRHE: säilynyt versio on Google Newsin linkki"
    print("\nPASS: dedupe() tunnisti Google News -republish-parin yhdeksi kohteeksi ja "
          "säilytti suoran linkin version; kontrolliuutinen säilyi erillisenä.")


if __name__ == "__main__":
    sys.exit(main())
