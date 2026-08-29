---
name: vegan-news-feed-review
description: Viikoittainen (tai pyydettäessä muulloinkin ajettava) itsearviointi vegan-news-feed-skillille. Lukee sisarskilliin `vegan-news-feed` kertyneen lähetyshistorian (mitä uutisia ja sisältöideoita on oikeasti lähetetty, mistä lähteistä, kuinka usein), analysoi toistuvia laatuongelmia tai puutteita, ja kirjoittaa konkreettisia, perusteltuja muutosehdotuksia (esim. lähteen lisäys/poisto feeds.md:hen, relevanssikriteerin hionta SKILL.md:hen) tiedostoon `~/.config/vegan-news/proposals/`. Ei KOSKAAN muokkaa vegan-news-feedin omia tiedostoja itse — ehdotukset vaativat aina ihmisen hyväksynnän ja soveltamisen erikseen. Käytä tätä skilliä kun käyttäjä pyytää arvioimaan/katselmoimaan/parantamaan vegan-news-feed-skilliä, tekemään viikkokatsauksen, tarkistamaan onko lähteissä tai relevanssissa parannettavaa, tai lyhyillä komennoilla kuten "aja viikkokatsaus", "arvioi vegan-news-feedin toimintaa" tai "onko vegan-news-feediin parannusehdotuksia".
---

# Vegan News Feed — Review

Tämä skilli on `vegan-news-feed`-skillin **katselmoija**, ei sen tuottaja. Sillä on täysin eri vastuu ja eri kadenssi (viikoittainen tai tarpeen mukaan, ei päivittäinen), ja siksi se on tarkoituksella oma erillinen skillinsä eikä osa `vegan-news-feed`:iä — ks. `vegan-news-feed/PROCESS.md`:n iteraatio 4 -osio miksi tämä arkkitehtuurivalinta tehtiin.

**Ydinsääntö, josta ei jousteta:** tämä skilli lukee `vegan-news-feed`-hakemiston tiedostoja, mutta **ei koskaan kirjoita tai muokkaa niitä**. Se kirjoittaa vain `~/.config/vegan-news/proposals/`-kansioon — tarkoituksella skillikansion ulkopuolelle, koska `~/.claude/skills/`-hakemiston sisällä olevat tiedostot lasketaan Claude Codessa "sensitive file" -kategoriaan, mikä estäisi Write-työkalua kirjoittamasta sinne ilman ihmisen läsnäoloa hyväksymässä sitä (ks. `../vegan-news-feed/DATA_LOCATIONS.md`). Muutosten soveltaminen `SKILL.md`:hen tai `feeds.md`:hen on aina erillinen, ihmisen pyytämä, interaktiivinen toimenpide — ei jotain minkä tämä skilli tekee osana ajoaan, ei edes jos ehdotus vaikuttaa ilmiselvältä.

## Riippuvuus

Tämä skilli olettaa että `vegan-news-feed` on asennettu polkuun `~/.claude/skills/vegan-news-feed/` (rinnakkainen kansio, ei tämän skillin sisällä). Se käyttää suoraan sen `scripts/history.py`- ja `scripts/post_discord.py`-skriptejä sekä lukee sen `references/feeds.md`- ja `SKILL.md`-tiedostoja — ei omaa kopioita niistä.

## Työnkulku

### 1. Lue lähetyshistoria

```bash
python3 ~/.claude/skills/vegan-news-feed/scripts/history.py show --days 7
```

Oletus on 7 päivää (viikkokatsaus), mutta jos käyttäjä pyysi eri aikaväliä (esim. "katso viimeiset kaksi viikkoa"), käytä `--days`-arvoa sen mukaan. Historia sisältää kolmea kohdetyyppiä, kaikki kiinnostavat tässä (ks. vaihe 3):

- `"type": "news"` — lähetetyt uutiset (otsikko, linkki, tiivistelmä, lähde)
- `"type": "content_idea"` — vaiheen 4 sisältöideat (kulma, miksi juuri nyt)
- `"type": "run"` — joka ajon ajomerkintä (`result`: `"sent"`/`"no_news"`/`"unrecoverable"`, `item_count`, mahdollisesti `"backfilled": true`) — tallennetaan AINA, myös päivinä jolloin uutisia ei löytynyt tai joita on täytetty jälkikäteen backfillillä. Tämä on ainoa tapa erottaa "ajettiin, ei löytynyt mitään relevanttia" -päivä "ajo ei koskaan käynnistynyt" -päivästä.

**Jos historia on tyhjä tai hyvin ohut** (esim. skilli asennettu juuri, tai `vegan-news-feed`-vaiheen 7 tallennus ei ole vielä ehtinyt kertyä useammalta päivältä): älä keksi löydöksiä tyhjästä. Kirjoita ehdotustiedostoon rehellisesti että dataa on liian vähän mielekkääseen arvioon, tai jätä koko ajo tekemättä ja kerro käyttäjälle miksi (jos ajettu interaktiivisesti) / älä lähetä Discord-ilmoitusta (jos ajettu cronista).

### 2. Lue nykyinen konfiguraatio (vain luku)

Lue `~/.claude/skills/vegan-news-feed/references/feeds.md` (mitä lähteitä on tällä hetkellä käytössä) ja `~/.claude/skills/vegan-news-feed/SKILL.md`:n vaihe 2 (nykyiset "Pidä mukana"/"Jätä pois" -kriteerit). Tarvitset näitä kontekstiksi — et voi ehdottaa "lisää X-lähde" jos se on jo listalla, etkä "tiukenna Y-kriteeriä" tietämättä mikä nykyinen kriteeri on.

### 3. Analysoi

Käy läpi vaiheen 1 data ja etsi konkreettisia, dataan pohjautuvia havaintoja — ei yleisiä mielipiteitä. Esimerkkejä kysymyksistä joita kannattaa kysyä:

- **Lähteiden kontribuutio**: mitkä `source`-kentän arvot esiintyvät `"news"`-kohteissa toistuvasti, mitkä eivät koskaan? Jos jokin `feeds.md`:n lähde ei ole tuottanut yhtään mukaan valittua uutista koko tarkastelujaksolla, se on validi havainto (mutta muista: syy voi olla että lähde julkaisee harvoin, ei että se on hyödytön — tarkista `feeds.md`:n omat huomiot ennen kuin ehdotat poistoa).
- **Duplikaattikuorma**: näkyykö historiassa merkkejä siitä että sama tarina on lähetetty useana peräkkäisenä päivänä (mahdollinen cross-day-dedupin ohitus, tai aidosti uusia käänteitä samaan tarinaan — erota nämä)?
- **Tiivistelmien laatu**: ovatko `summary`-kentät informatiivisia (kertovat mitä tapahtui) vai laimeita/geneerisiä? Tämä on suoraan luettavissa historian datasta, koska se sisältää oikean lähetetyn tekstin, ei vain otsikkoa.
- **Sisältöideoiden aitous**: `"content_idea"`-kohteiden `angle`/`why_now`-tekstit — vaikuttavatko ne aidoilta, konkreettisilta kulmilta, vai geneerisiltä/pakotetuilta toistoilta samasta muotista päivästä toiseen?
- **Aihepiirin tasapaino**: onko esim. eläinoikeuspolitiikka (Suomi/EU) näkynyt lainkaan tarkastelujaksolla, vai onko digest ollut yksipuolisesti yritys-/tuoteuutisia? (Ks. `SKILL.md`:n laajennettu "Pidä mukana" -kriteeri — jos tämä ei näy datassa, syy voi olla lähteiden harva päivitystahti, ei relevanssiarvion vika.)
- **Ajojen onnistuminen**: käy läpi `"run"`-kohteet tarkastelujaksolta. Montako päivää oli `"sent"` vs. `"no_news"` — onko `"no_news"`-päiviä epätavallisen monta (voisi viitata relevanssikriteerin olevan liian tiukka, ei siihen ettei uutisia oikeasti ollut)? Löytyykö `"backfilled": true` -merkintöjä, ja jos niin onko niiden joukossa `"result": "unrecoverable"` (aukko jota ei saatu koskaan täytettyä — kertoo että ajoja jää välistä useammin kuin toivottaisiin, mikä voi olla oma havainto/ehdotus sinänsä, esim. cron-ajan siirto tai koneen valvontaan liittyvä huomio). Puuttuuko joltain päivältä tarkastelujaksolla kokonaan `"run"`-merkintä (ks. `history.py gaps`) — se on eri asia kuin `"no_news"`, ja validi oma havaintonsa.

Älä pakota löydöksiä jos dataa ei riitä johtopäätökseen — "ei riittävästi dataa arvioidakseen X:ää vielä" on validi ja rehellinen havainto.

### 4. Kirjoita ehdotukset

Jokainen ehdotus on **konkreettinen ja toteuttamiskelpoinen sellaisenaan** — ei "harkitse parantamista", vaan täsmällinen muutos + peruste:

- Mikä tiedosto muuttuisi (`references/feeds.md` tai `SKILL.md`, ja mikä kohta niistä)
- Mikä täsmällinen muutos (esim. "lisää URL X feeds.md:n Suomi-osioon", "muuta vaiheen 2 'Jätä pois' -sääntöä lisäämällä poikkeus Y:lle")
- Peruste, viitaten oikeisiin havaintoihin vaiheesta 3 (ei yleisluontoiseen "voisi olla parempi")

Jos tarkastelujakson data ei anna aihetta mihinkään muutokseen, se on täysin ok tulos — kirjoita ehdotustiedostoon lyhyesti että kaikki toimi odotetusti eikä muutoksia ehdoteta, äläkä keksi tekosyytä ehdottaa jotain.

### 5. Tallenna ehdotus

Kirjoita `~/.config/vegan-news/proposals/{VVVV-KK-PP}.md` (tämänpäiväinen päivämäärä), tätä pohjaa käyttäen:

```
# Viikkokatsaus – {pp.kk.vvvv}

**Tarkastelujakso:** {N} päivää ({alkupvm}–{loppupvm})
**Historian koko:** {X} uutista, {Y} sisältöideaa
**Ajot:** {A} sent, {B} no_news, {C} backfilled, {D} unrecoverable (jos ei mainittavaa, esim. kaikki ajot onnistuivat normaalisti, tämän rivin voi jättää lyhyeksi: "kaikki {N} ajoa onnistuivat normaalisti")

## Havainnot

- {Havainto 1, dataan pohjautuen}
- {Havainto 2}

## Ehdotukset

### 1. {Lyhyt otsikko}
**Tiedosto:** `{polku}`
**Muutos:** {täsmällinen muutos}
**Peruste:** {miksi, viitaten havaintoihin yllä}

### 2. ...

(Jos ei ehdotuksia: "Ei muutosehdotuksia tällä kertaa — data ei antanut aihetta.")
```

### 6. Ilmoita Discordiin

Lähetä lyhyt ilmoitus samaan webhookiin jota `vegan-news-feed` käyttää (sama `.env`), jotta ehdotus ei jää huomaamatta:

```bash
DISCORD_WEBHOOK_URL="..." python3 ~/.claude/skills/vegan-news-feed/scripts/post_discord.py --message-file /tmp/review_notification.md
```

Viesti on lyhyt, ei koko ehdotus:

```
📋 **Viikkokatsaus valmis – {pp.kk.vvvv}**
{N} ehdotusta tarkastettavaksi: `~/.config/vegan-news/proposals/{VVVV-KK-PP}.md`
```

Jos ehdotuksia ei ollut, lähetä silti lyhyt vahvistus ("📋 Viikkokatsaus tehty, ei muutosehdotuksia") — sama periaate kuin `vegan-news-feed`:n "ei uutisia tänään" -viestissä: näet putken toimivan myös silloin kun mitään ei tapahdu.

**Jos historia oli vaiheessa 1 liian ohut arvioitavaksi**: älä lähetä Discord-ilmoitusta lainkaan (ei ole mitään ilmoitettavaa), paitsi jos skilli ajettiin interaktiivisesti käyttäjän pyynnöstä — silloin kerro suoraan chatissa, ei Discordin kautta.

## Mitä TÄMÄ skilli ei koskaan tee

- Ei muokkaa `vegan-news-feed/SKILL.md`, `references/feeds.md`, tai `scripts/*.py` -tiedostoja.
- Ei lähetä uutiskoostetta Discordiin (se on `vegan-news-feed`:n vaihe 6, ei tämän skillin vastuulla).
- Ei sovella omia ehdotuksiaan, ei edes jos ne vaikuttavat pieniltä/ilmeisiltä.

## Ajastaminen (valinnainen)

Tätä skilliä EI tarvitse ajaa cronilla toimiakseen — se on täysin käyttökelpoinen ajettuna manuaalisesti milloin tahansa (esim. "aja vegan-news-feedin viikkokatsaus"). Jos haluat automaattisen viikoittaisen muistutuksen, ks. `scripts/run_weekly_review.sh` ja sen oma dokumentaatio ajastamisesta — sama malli kuin `vegan-news-feed/scripts/run_daily.sh`, mutta eri (harvempi) aikataulu ja eri prompti.

## Resurssit

- `scripts/run_weekly_review.sh` — cron-turvallinen wrapper (env/Python/SSL-asetus + `claude -p`), mutta ajettavissa myös suoraan terminaalista milloin tahansa ilman cronia
