#!/usr/bin/env python3
"""
Pitaa kirjaa aiemmin lahetetyista uutisista, jotta samaa tarinaa ei
lahetetä useana perakkaisena paivana uudelleen (esim. sama laki-/kanne-
uutinen pysyy 30h-fetch-ikkunassa monta paivaa peräkkäin).

Tama on tarkoituksella pelkka mekaaninen tallennus/haku - se EI paata
mika on "sama tarina" (esim. eri lahteen kirjoittama juttu samasta
tapahtumasta). Se paatos jaa agentin harkintaan vaiheessa 2, taman
skriptin `show`-komennon palauttamaa historiaa vasten.

Kayttaa vain Python-standardikirjastoa.

Kaytto:
    python3 history.py show --days 5
        Tulostaa JSON-listan viimeisen N paivan aikana tallennetuista
        kohteista (uusin ensin). Tyhja historia -> "[]".

    python3 history.py record --items-file /tmp/vegan_digest_items.json [--date VVVV-KK-PP]
        Lisaa items-file:n sisaltamat kohteet historiaan annetulla
        paivamaaralla (oletus: tanaan, UTC) ja siivoaa samalla yli
        --keep-days paivaa vanhat merkinnat pois. --date on tarkoitettu
        puuttuvien paivien jalkikateiseen tayttoon (backfill) - ks.
        SKILL.md:n "Puuttuvien paivien tayttaminen" -osio.

    python3 history.py gaps --days 14
        Tulostaa JSON-listan (VVVV-KK-PP) paivista viimeisen N paivan
        ajalta joilta EI loydy yhtaan merkintaa historiassa - eli
        todennakoisesti ohitettuja ajoja (esim. kone oli unessa cronin
        ajankohtana). Kaytetaan yhdessa --date-lipun kanssa backfillissa.

Items-file-muoto: JSON-lista objekteja. Ainoa PAKOLLINEN kentta on
"title" - kaikki muut kentat item-objektista sailytetaan sellaisenaan
historiaan (esim. "link", "summary", "source", "language", "type").
Tama on tarkoituksella joustava eika kiinteasti skeemoitu, jotta:

  (a) vegan-news-feed-skilli voi tallentaa paitsi lahetetyt uutiset
      (title/link/summary/source), myos vaiheen 4 sisaltoideat samaan
      historiaan - suositeltu konventio on merkita nama kentalla
      "type": "content_idea" (uutiset voi jattaa merkitsematta, tai
      merkita "type": "news"), jotta vegan-news-feed-review -skilli voi
      lukea molemmat ja erottaa ne toisistaan.

  (b) vegan-news-feed-review -skilli (erillinen, katselee tata dataa
      viikoittain ja ehdottaa muutoksia SKILL.md:hen/feeds.md:hen - EI
      koskaan muokkaa niita itse) tarvitsee oikean sisallon (tiivistelmat,
      lahteet) arvioidakseen laatua, ei pelkkia otsikoita/linkkeja.

  (c) jokainen ajo (myos "ei uutisia tanaan" -tapaus) tallentaa lisaksi
      yhden "type": "run" -merkinnan (kentat esim. "result": "sent"/
      "no_news"/"unrecoverable", "item_count"). Tama on se mika
      erottaa "ajettiin, ei loytynyt mitaan relevanttia" -paivan
      "ajoa ei koskaan tapahtunut" -paivasta `gaps`-komennossa - ilman
      run-merkintaa nailla kahdella tapauksella ei olisi eroa.
      Jalkikateen taytetyt (backfill) merkinnat - mika tahansa tyyppi -
      merkitaan lisaksi kentalla "backfilled": true.

Historiatiedosto elaa oletuksena kayttajan ~/.config/vegan-news/-
kansiossa, saman webhook-.env-tiedoston vieressa - EI skillin oman
kansion sisalla, koska tama on ajoympariston tilaa (per kayttaja/kone),
ei osa itse skillia. Molemmat skillit (vegan-news-feed ja
vegan-news-feed-review) kayttavat samaa tiedostoa ja samaa scriptia.
"""
import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

DEFAULT_HISTORY_FILE = Path.home() / ".config" / "vegan-news" / "sent_history.json"
DEFAULT_KEEP_DAYS = 30


def load_history(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except Exception as exc:
        print(f"[varoitus] historiatiedosto viallinen ({exc}), kaytetaan tyhjaa historiaa.", file=sys.stderr)
        return []


def save_history(path: Path, entries: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


def prune(entries: list[dict], keep_days: int) -> list[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=keep_days)).date().isoformat()
    return [e for e in entries if e.get("date", "") >= cutoff]


def cmd_show(args):
    entries = load_history(args.history_file)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=args.days)).date().isoformat()
    recent = [e for e in entries if e.get("date", "") >= cutoff]
    recent.sort(key=lambda e: e.get("date", ""), reverse=True)
    print(json.dumps(recent, ensure_ascii=False, indent=2))


def cmd_record(args):
    try:
        new_items = json.loads(args.items_file.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"items-file ei kelpaa JSON:ksi: {exc}", file=sys.stderr)
        sys.exit(1)
    if not isinstance(new_items, list):
        print("items-file taytyy olla JSON-lista objekteja.", file=sys.stderr)
        sys.exit(1)

    if args.date:
        try:
            datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print(f"--date ei ole muodossa VVVV-KK-PP: {args.date!r}", file=sys.stderr)
            sys.exit(1)
        target_date = args.date
    else:
        target_date = datetime.now(timezone.utc).date().isoformat()

    entries = load_history(args.history_file)

    for item in new_items:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        if not title:
            continue
        # Sailytetaan KAIKKI item-objektin kentat (summary, source, type, ...),
        # ei vain title/link - ks. moduulin docstring miksi.
        entry = dict(item)
        entry["title"] = title
        entry["date"] = target_date
        entries.append(entry)

    entries = prune(entries, args.keep_days)
    save_history(args.history_file, entries)

    print(
        f"Tallennettu {len(new_items)} kohdetta historiaan paivamaaralla {target_date} "
        f"({args.history_file}), historiassa nyt {len(entries)} merkintaa "
        f"(yli {args.keep_days} vrk vanhat siivottu).",
        file=sys.stderr,
    )


def cmd_gaps(args):
    entries = load_history(args.history_file)
    covered_dates = {e.get("date") for e in entries if e.get("date")}

    today = datetime.now(timezone.utc).date()
    missing = []
    # range(1, ...) - ei tarkisteta tanaista paivaa, koska tama ajetaan
    # yleensa ennen paivan oman ajon suoritusta eika se ole viela
    # "myohassa" tanaan.
    for i in range(1, args.days + 1):
        d = (today - timedelta(days=i)).isoformat()
        if d not in covered_dates:
            missing.append(d)

    missing.sort()
    print(json.dumps(missing, ensure_ascii=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Lahetyshistorian hallinta (cross-day dedup)")
    parser.add_argument(
        "--history-file", type=Path, default=DEFAULT_HISTORY_FILE, help="Polku historia-JSON-tiedostoon"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    show_p = sub.add_parser("show", help="Nayta viimeaikainen lahetyshistoria")
    show_p.add_argument("--days", type=int, default=5, help="Kuinka monelta paivalta historiaa nayteta (oletus 5)")
    show_p.set_defaults(func=cmd_show)

    record_p = sub.add_parser("record", help="Tallenna lahetetyt uutiset historiaan")
    record_p.add_argument(
        "--items-file", type=Path, required=True, help="JSON-lista objekteja, vahintaan {title: ...}"
    )
    record_p.add_argument(
        "--date",
        type=str,
        default=None,
        help="VVVV-KK-PP - kayta jalkikateisessa tayttamisessa (backfill); oletus tanaan (UTC)",
    )
    record_p.add_argument(
        "--keep-days", type=int, default=DEFAULT_KEEP_DAYS, help="Kuinka monta paivaa historiaa sailytetaan (oletus 30)"
    )
    record_p.set_defaults(func=cmd_record)

    gaps_p = sub.add_parser("gaps", help="Listaa paivat joilta puuttuu jokainen merkinta (todennakoisesti ohitettu ajo)")
    gaps_p.add_argument("--days", type=int, default=14, help="Kuinka monelta paivalta taaksepain tarkistetaan (oletus 14)")
    gaps_p.set_defaults(func=cmd_gaps)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
