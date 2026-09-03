# Example output

This is a real proposal the skill produced — captured verbatim, not written as a mockup. Produced 2026-08-30, by the skill's first real scheduled run (a macOS LaunchAgent firing on time, unattended). It lives outside this repo on the machine that ran it (`~/.config/vegan-news/proposals/` — see [`../vegan-news-feed/DATA_LOCATIONS.md`](../vegan-news-feed/DATA_LOCATIONS.md) for why), so it's reproduced here for anyone reading the code who can't see that machine's filesystem.

What's worth noticing: the skill finishes an investigation the *previous* week's review had only flagged as needing one (source-by-source diagnosis, not guesswork), reaches an honest **"no change needed"** conclusion on the actual sources rather than manufacturing a fix to look useful, and every proposal carries a `Tila` (status) field a human updates later — this one shipped as `odottaa` (pending), waiting on a person to actually read it and decide.

---

```
# Viikkokatsaus – 30.08.2026

**Tarkastelujakso:** 7 päivää (24.08.2026–30.08.2026)
**Historian koko:** 31 uutista, 9 sisältöideaa
**Ajot:** 5 sent, 0 no_news, 0 backfilled, 0 unrecoverable — 24.–25.8. puuttuu run-merkintä, mutta ei aidosta aukosta (skilli otettiin käyttöön vasta 26.8., ks. edellisen katselmoinnin (29.8.) korjattu havainto ja PROCESS.md)

## Havainnot

- Kaikki 5 tarkastelujakson ajoa (26.–30.8.) onnistuivat normaalisti ("sent"), tuottaen yhteensä 31 uutista ja 9 sisältöidean.
- **Edellisen katselmoinnin (29.8.) ehdotus #1 diagnosoitu loppuun.** Tuo ehdotus pyysi selvittämään syyn siihen, ettei yksikään feeds.md:n suomenkielinen lähde ollut tuottanut yhtään uutista 7 päivän aikana, ennen kuin lähteitä muutetaan. Tällä viikolla tilanne on täsmälleen sama (0/31 uutisesta on kielimerkinnältään suomi), joten tein diagnoosin nyt hakemalla lähteet suoraan:
  - animalia.fi/feed/: uusin julkaisu 10.7.2026 — n. 7 viikkoa vanha, siis reilusti fetch_feeds.py:n 30h-ikkunan ulkopuolella koko tarkastelujakson ajan. Lähde ei ole rikki, mutta on tällä hetkellä käytännössä pysähdyksissä.
  - vegaaniliitto.fi/feed/: uusin julkaisu 3.7.2026 — sama tilanne, n. 8 viikkoa vanha.
  - sey.fi/feed/: päivittyy edelleen aktiivisesti (uusimmat 17.–19.8.2026), mutta sisältö on feeds.md:n oman huomion mukaisesti valtaosin yksittäisiä lemmikki-/pelastuseläintarinoita ("Ursula-kissa ja sen viisi pentua hylättiin ulos"), jotka SKILL.md:n vaiheen 2 "Jätä pois" -sääntö perustellusti suodattaa pois — tämä toimii siis suunnitellusti, ei ole ongelma.
  - Suomenkieliset Google News -haut (veganismi/kasviperäinen, vegaaninen/kasvipohjainen ruoka, elainoikeudet/turkistarhaus) EIVÄT ole rikki tai tyhjiä — ne löytävät ajoittain aidosti relevantteja tuoreita suomalaisia uutisia (esim. 17.8. Iltalehti-juttu, 27.7. STT Info -uutinen turkistarhauskyselystä), mutta harvakseltaan, karkeasti kerran 1–4 viikossa. Kahden 0-tuloksen viikon peräkkäisyys 30h-hakuikkunalla on siis tilastollisesti odotettavissa tällä julkaisutahdilla, ei merkki rikkinäisestä hausta tai liian tiukasta relevanssikriteeristä.
  - **Johtopäätös:** 0/31 suomenkielistä uutista selittyy kahden lähteen (animalia.fi, vegaaniliitto.fi) tilapäisellä pysähtyneisyydellä yhdistettynä suomenkielisen vegaani-/eläinoikeusuutisoinnin luontaisesti matalaan volyymiin — ei relevanssiarvioinnin viasta eikä rikkinäisestä lähteestä. Näiden kahden lähteen poistaminen tai korvaaminen ei ole perusteltua pelkän tämän datan pohjalta, koska ne saattavat aktivoitua uudelleen; asiaa kannattaa vain seurata.
- Duplikaattikuormaa ei näy: sama tarina ei toistu peräkkäisinä päivinä ilman aitoa uutta käännettä (esim. EU:n "burger"-nimikielto 27.8. on oma, aidosti ajankohtainen uutinen kolmannesta parlamenttikäsittelystä, ei duplikaatti aiemmasta).
- Aihetasapaino on hyvä tällä viikolla: mukana sekä EU-/kansallista politiikkaa (burger-nimikielto, MEP-äänestystutkimus, Britannian eläinkoerahoitus), tiedettä (mykotoksiinitutkimus, NASA-rahoitteinen proteiinitutkimus), että yritys-/markkinauutisia — ei yksipuolista painotusta.
- Tiivistelmät ovat läpi jakson konkreettisia ja kertovat mitä tapahtui (esim. tarkat lukemat: "67 % brittivanhemmista", "56 % kasvua", "3 kertaa todennäköisemmin") — ei geneeristä laimeutta.
- Sisältöideoiden (9 kpl) kulmat ja "miksi juuri nyt" -perustelut vaikuttavat edelleen aidoilta ja tapauskohtaisilta, eivät toisteisilta samasta muotista.
- Pieni, ei-toimenpiteitä vaativa huomio: 30.8. ajossa oli vain 1 uutinen (muina päivinä 7–9). Tämä on todennäköisesti vain aidosti hiljainen päivä (SKILL.md:n oman ohjeen mukaan lyhyempi koonti on tarkoituksella parempi kuin laimennettu), eikä yksi päivä riitä päättelemään mitään lähde- tai kriteeriongelmasta — ei vaadi toimenpidettä, mutta kannattaa pitää mielessä jos toistuu.

## Ehdotukset

### 1. Kirjaa suomenkielisten lähteiden diagnoosi feeds.md:n Huomioita-osioon
**Tila:** odottaa
**Tiedosto:** references/feeds.md
**Muutos:** Lisää "Huomioita"-listaan (rivin 29 sey.fi-huomion tapaan) uusi kohta: "30.8.2026 tarkistettu: animalia.fi ja vegaaniliitto.fi eivät ole julkaisseet mitään heinäkuun 2026 alun jälkeen (viimeisimmät 10.7. ja 3.7.) — eivät siis tällä hetkellä tuota mitään 30h-hakuikkunaan, mutta eivät ole teknisesti rikki. Jos tämä jatkuu useita kuukausia, harkitse poistoa; tarkista ensin onko julkaisu käynnistynyt uudelleen."
**Peruste:** Tämä diagnoosi vastaa suoraan edelliseen (29.8.) katselmointiin kirjattuun ehdotukseen #1 ("diagnosoi ennen kuin muutat"), ja tallentamalla tuloksen feeds.md:ään vältetään sama selvitystyö toistamasta jokaisessa tulevassa katselmoinnissa niin kauan kuin 0-suomi-viikkoja jatkuu.

### 2. Ei muuta muutosehdotusta suomenkielisiin lähteisiin tai relevanssikriteereihin tällä kertaa
**Tila:** odottaa
**Tiedosto:** (ei sovellu)
**Muutos:** Ei toimenpidettä — älä poista tai korvaa animalia.fi/vegaaniliitto.fi-lähteitä, älä muuta suomenkielisiä Google News -hakusanoja, älä löysää SKILL.md:n vaiheen 2 relevanssikriteerejä.
**Peruste:** Havainnon mukaan ongelma on kahden lähteen tilapäinen hiljaisuus ja suomenkielisen uutisoinnin luontainen harvuus, ei relevanssiarvioinnin tai hakusanojen vika — muutos näihin ratkaisisi väärän ongelman. Kirjattu tähän eksplisiittisesti, jottei tulevaisuudessa ehdoteta samaa korjausta uudelleen ilman uutta, tätä diagnoosia kumoavaa dataa.
```

---

For the fuller story of how that "diagnosed to completion" thread actually resolved — including a real user-reported missed article that turned out to reveal a second, independent bug the source-dormancy diagnosis above hadn't caught — see [`../vegan-news-feed/PROCESS.md`](../vegan-news-feed/PROCESS.md), iterations 9 onward.
