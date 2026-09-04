---
name: vegan-literature-feed
description: Seuraa tuoretta tieteellistä kirjallisuutta veganismiin, kasvipohjaiseen ravitsemukseen, eläinten kognitioon/tuntoisuuteen, eläintuotannon ympäristövaikutukseen ja eläinoikeuspolitiikkaan liittyen — hakee PubMedista (ja tarvittaessa WebSearchilla laajemmin) tuoreet vertaisarvioidut artikkelit ja katsausartikkelit, arvioi niiden tieteellisen painoarvon ja uutisarvon, kirjoittaa suomenkielisen yhteenvedon lähdeviitteineen ja varauksineen, poimii viestintätiimille julkaisukulman, ja lähettää koosteen Discordiin. Käytä tätä skilliä kun käyttäjä pyytää tarkistamaan tuoretta vegaani-/eläinoikeustutkimusta, "kirjallisuuskatsausta", tieteellisiä löydöksiä alalta, tai lyhyillä komennoilla kuten "aja kirjallisuuskooste" tai "onko alalla tullut mielenkiintoista tutkimusta". Huom: tämä skilli on tarkoituksella minimiversio (ks. TODO.md) — ei vielä ajastettu, ei vielä laajaa lähdekatalogia.
---

# Vegan Literature Feed

Tämä skilli on `vegan-news-feed`:n sisarskilli, mutta seuraa uutisten sijaan **tieteellistä kirjallisuutta**: vertaisarvioituja tutkimusartikkeleita ja katsauksia (review/meta-analyysi/systemaattinen katsaus) veganismiin, kasvipohjaiseen ravitsemukseen, eläinten kognitioon/tuntoisuuteen, eläintuotannon ympäristövaikutukseen ja eläinoikeuspolitiikkaan liittyen. Tavoite: antaa viestintätiimille mahdollisuus julkaista kiinnostavasta löydöksestä ennen kuin valtamedia ehtii sen edelle.

**Tämä on tarkoituksella minimiversio.** Ks. `TODO.md` täydelle listalle mitä on jätetty myöhemmäksi (mm. kuratoitu lehti-RSS-lähdekatalogi, ajastus, laajempi eval-kattavuus).

## Miksi review-/katsausartikkelit ovat yhtä tärkeitä kuin uudet löydökset

**Tämä ei ole vain "uusin tutkimus" -seuranta.** Katsausartikkelit (review), meta-analyysit ja systemaattiset katsaukset ovat usein KIINNOSTAVAMPIA kuin yksittäinen uusi alkuperäistutkimus, koska ne kokoavat laajemman kuvan tutkimusrintamasta yhteen — juuri se konteksti jota viestintätiimi tarvitsee ottaakseen kantaa perustellusti. Älä siis suodata näitä pois vain koska ne "eivät ole uusi löydös" — arvioi niitä omalla mittapuullaan (ks. vaihe 2 ja 3 alla).

## Vertaisarvioitu vain — ei preprinttejä

PubMedin kautta löytyvät kohteet ovat jo lähtökohtaisesti vertaisarvioituja (PubMed ei indeksoi preprinttejä) — tätä ei tarvitse tarkistaa erikseen niiden kohdalla. **WebSearch-hakujen tulokset sen sijaan VAATIVAT tämän tarkistuksen erikseen jokaiselle kohteelle**: jos osuma on bioRxiv/medRxiv/SSRN/arXiv tai muu preprint-palvelin, tai muuten selvästi vertaisarvioimaton (esim. julkaisematon working paper), jätä se pois tästä koosteesta kokonaan. Tämä on tietoinen, konservatiivinen valinta tälle skillille juuri nyt (nopeus preprinttien kautta olisi mahdollista, mutta riski että viestintätiimi julkaisisi jotain mikä ei kestä vertaisarviointia painaa enemmän) — ks. `PROCESS.md`.

## Työnkulku

### 1. Hae raakadata

```bash
python3 scripts/fetch_pubmed.py --days 7 --output /tmp/vegan_literature_raw.json
```

Tämä hakee PubMedista viimeisen 7 päivän (oletus, säädettävissä `--days`) sisällä julkaistut artikkelit `fetch_pubmed.py`:n oletuskyselyllä (kattaa laajasti kaikki neljä aihepiiriä — ks. skriptin `DEFAULT_QUERY`). Tuloste on JSON-lista, kenttinä `title`, `link` (suora pubmed.ncbi.nlm.nih.gov-linkki), `source` (lehden nimi), `published`, `language` (aina `"en"`, PubMed on englanninkielinen), `summary` (artikkelin oma abstrakti, ei sinun kirjoittamasi), `pub_types` (lista, esim. `["Journal Article", "Review"]` — **tarkista tämä kenttä aina**, se kertoo onko kyseessä alkuperäistutkimus, katsaus, meta-analyysi tms.), ja `pmid`.

**Kysely on tarkoituksella laaja ja tuottaa myös epäolennaisia osumia** (esim. yleistä eläinlääketiedettä joka ei liity veganismiin/eläinoikeuksiin) — tämä on odotettua, aivan kuten `vegan-news-feed`:n raakadatakin sisältää karsittavia osumia. Vaihe 2 hoitaa varsinaisen relevanssiarvion.

**PubMed kattaa heikosti maatalous-/ympäristö-/politiikkatutkimuksen** (ei biolääketieteellinen tietokanta). Tämän täydentämiseksi, tee lisäksi 1-3 kohdennettua `WebSearch`-hakua nimenomaan tälle aihepiirille (esim. "animal agriculture environmental impact study [kuukausi vuosi]", "farm animal welfare policy research [kuukausi vuosi]") ja tarkista jokainen osuma erikseen `WebFetch`illä: (a) onko se oikeasti vertaisarvioitu julkaisu (ei preprint, ei pelkkä uutisartikkeli tutkimuksesta), (b) mikä on julkaisupäivä (hakutulokset nostavat usein esiin myös vanhoja tutkimuksia). Älä luota hakutuloksen otsikkoon/kuvaukseen sellaisenaan.

### 2. Arvioi relevanssi ja tieteellinen painoarvo

Käy läpi vaiheen 1 kaikki kohteet (PubMed + WebSearch-täydennys). Tarkista ensin lähetyshistoria duplikaattien varalta:

```bash
python3 ~/.claude/skills/vegan-news-feed/scripts/history.py --history-file ~/.config/vegan-literature/literature_history.json show --days 14
```

(Käytetään samaa `history.py`-skriptiä kuin `vegan-news-feed`, mutta omalla `--history-file`-polulla — ei omaa kopiota skriptistä, ks. `README.md`.)

**Pidä mukana:**
- Alkuperäistutkimus (`"pub_types"` sisältää `"Journal Article"` muttei `"Review"`/`"Meta-Analysis"`/`"Systematic Review"`) jonka löydös on aidosti kiinnostava, uusi tai yllättävä — ei vain "vahvistaa jo tiedettyä"
- Katsausartikkeli/meta-analyysi/systemaattinen katsaus (`"pub_types"` sisältää jonkin näistä) joka kokoaa hyödyllisen laajemman kuvan aihepiiristä — arvioi näitä NIMENOMAAN kontekstin/synteesin arvon perusteella, ei "onko tämä uusi löydös"
- Tutkimus jonka tulos on tarpeeksi selkeä että viestintätiimi voi ottaa siitä kantaa ilman että joutuu itse arvioimaan monimutkaista metodologiaa

**Jätä pois:**
- Selvästi epäolennainen (yleinen eläinlääketiede/maataloustiede jolla ei ole veganismi-/eläinoikeusnäkökulmaa, esim. tuotantoeläinten lääkitysprotokollat ilman eettistä/poliittista ulottuvuutta)
- Eläinkoetutkimus jonka tulosta ei voi suoraan yleistää (esim. jyrsijämalli ihmisravitsemuksesta) ilman että tämä mainitaan selvästi varauksena vaiheessa 3 — ei suodateta pois, mutta ei myöskään esitetä ihmissovelluksena ilman varausta
- Preprintit ja muut vertaisarvioimattomat lähteet (ks. yllä) — TÄRKEÄÄ tarkistaa erikseen jokaiselle WebSearch-kohteelle
- Duplikaatit: sama tutkimus/tulos joka on jo lähetetty äskettäin (ks. `history.py show` yllä)

Valitse enintään 5-8 kärkikohdetta. Jos relevantteja on vähemmän, älä täytä listaa heikommilla.

### 3. Kirjoita yhteenvedot

Kirjoita jokaiselle valitulle kohteelle suomeksi:
- **Yhteenveto** (2-3 lausetta): mitä tutkittiin ja mitä löydettiin (alkuperäistutkimus) TAI mitä laajempaa kuvaa katsaus kokoaa (review/meta-analyysi) — kerro aina konkreettinen tulos, ei vain aihe
- **Tutkimustyyppi**: merkitse selvästi (esim. "Alkuperäistutkimus, satunnaistettu koeasetelma", "Systemaattinen katsaus", "Meta-analyysi, N tutkimusta") — tämä auttaa viestintätiimiä arvioimaan kuinka vahvasti tulokseen kannattaa nojata
- **Varaus/rajoitus** (1 lause, jos relevantti): esim. "eläinkoe, ei suoraan yleistettävissä ihmisiin", "pieni otoskoko (N=32)", "poikkileikkaustutkimus, ei osoita syy-seurausta" — älä jätä tätä pois vain koska se tekisi tuloksesta vähemmän vaikuttavan kuulostavan

### 4. Poimi julkaisukulma

Poimi 1-2 vaiheen 2 valinnasta parhaat lähtökohdat **omalle** sisällölle — ei pelkkää tutkimuksen referointia:

- **Kulma**: yhden lauseen ehdotus näkökulmasta some-postaukseen tai lehdistötiedotteeseen
- **Miksi julkaista tämä ensimmäisenä**: yksi lause siitä miksi tämä löydös on juuri nyt kiinnostava JA miksi viestintätiimi voisi ehtiä valtamedian edelle (esim. tuore julkaisu, ei vielä laajaa mediahuomiota saanut)

**Tärkeä varoitus liioittelusta:** "ensimmäisenä julkaiseminen" ei tarkoita tuloksen liioittelua tai varausten unohtamista nopeuden vuoksi. Jos tutkimus on alustava, eläinkoe, tai pienen otoksen tutkimus, sano se suoraan kulmaehdotuksessakin — nopea mutta epärehellinen kulma on huonompi kuin ei kulmaa lainkaan.

Jos mikään ei anna hyvää lähtökohtaa, jätä tämä osio pois.

### 5. Muotoile viesti

```
📚 **Kirjallisuuskooste – {pp.kk.vvvv}**

**1. [Otsikko suomeksi tai käännettynä]**
_{Tutkimustyyppi}_ — {Yhteenveto.} {Varaus, jos relevantti.}
📖 *{Lehti}*, {julkaisupäivä}
🔗 {linkki}

**2. ...**

💡 **Julkaisukulmat**
- **{Aihe}**: {Kulma}. _{Miksi julkaista ensimmäisenä}_

_{N} artikkelia tästä koosteesta, lähteinä {lähteiden lukumäärä} eri julkaisua._
```

"💡 Julkaisukulmat" jätetään kokonaan pois jos vaiheessa 4 ei löytynyt hyviä poimintoja.

Jos yhtään relevanttia kohdetta ei löytynyt: "📚 **Kirjallisuuskooste – {pvm}** — Ei merkittävää uutta tutkimusta tällä kertaa." Tämä on odotettavaa ja yleistä — kirjallisuutta ei julkaista päivittäin samalla tahdilla kuin uutisia.

### 6. Lähetä Discordiin

```bash
DISCORD_WEBHOOK_URL="..." python3 ~/.claude/skills/vegan-news-feed/scripts/post_discord.py --message-file /tmp/literature_digest.md
```

Käytetään suoraan `vegan-news-feed`:n `post_discord.py`-skriptiä (identtinen tehtävä, ei omaa kopiota) — `DISCORD_WEBHOOK_URL` luetaan omasta `~/.config/vegan-literature/.env`-tiedostosta. **Tällä hetkellä sama webhook-arvo kuin `vegan-news-feed`:llä, testausmielessä** — eri kanavalle siirtyminen on myöhemmin pelkkä `.env`-arvon vaihto, ei koodimuutos (ks. `README.md`).

### 7. Tallenna ajo historiaan

**Aina, myös kun tuloksia ei löytynyt** — sama periaate kuin `vegan-news-feed`:ssä (ks. sen `SKILL.md`:n vaihe 7 täydelle perustelulle).

```bash
python3 ~/.claude/skills/vegan-news-feed/scripts/history.py --history-file ~/.config/vegan-literature/literature_history.json record --items-file /tmp/literature_items.json
```

Sama muoto kuin `vegan-news-feed`:ssä: yksi `{"type": "run", "result": "sent"/"no_news", "item_count": N}` -kohde aina, ja lisäksi yksi `{"type": "literature", "title": ..., "link": ..., "summary": ..., "source": ..., "pub_types": [...]}` -kohde per lähetetty artikkeli (käytä `"type": "literature"` erottamaan nämä `vegan-news-feed`:n `"news"`-kohteista, jos historiatiedostot joskus yhdistetään).

## Resurssit

- `scripts/fetch_pubmed.py` — hakee PubMedista E-utilities-rajapinnan kautta (esearch → esummary → efetch), ei ulkoisia riippuvuuksia (vain Python-standardikirjasto). **Vaatii Python 3.10+** (ks. `PROCESS.md` — sama `X | None`-syntaksiongelma kuin `vegan-news-feed`:ssä, käytä `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3` jos järjestelmän oma `python3` on vanhempi) ja toimivat SSL-varmenteet (`SSL_CERT_FILE`, ks. `.env.example`:n vieressä oleva huomio tai `vegan-news-feed/scripts/run_daily.sh`:n vastaava ratkaisu).
- `vegan-news-feed/scripts/post_discord.py` ja `vegan-news-feed/scripts/history.py` — käytetään suoraan sisarskillistä, ei omia kopioita (DRY, sama periaate kuin `vegan-news-feed-review`:lla).
- `evals/evals.json` — muutama perustason testipromptio (ks. `TODO.md`, kattavuus on vielä ohut)
- `PROCESS.md` — suunnitteludokumentaatio
- `TODO.md` — mitä on tarkoituksella jätetty tekemättä tässä minimiversiossa
