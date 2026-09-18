# RSS-lähteet

Yksi URL per rivi. Rivit jotka alkavat `#` ohitetaan. `fetch_feeds.py` lukee tämän tiedoston oletuksena.

Kieli päätellään lähteen perusteella alla olevissa kommenteissa — jos lisäät uuden lähteen, merkitse kieli riville `# lang:fi` tai `# lang:en` edeltävälle kommenttiriville jos se ei ole ilmeinen URL:sta.

## Englanti

https://news.google.com/rss/search?q=veganism+OR+%22plant-based%22&hl=en-US&gl=US&ceid=US:en
https://vegconomist.com/feed/
https://plantbasednews.org/feed/

## Suomi

https://news.google.com/rss/search?q=vegaani+when:2d&hl=fi&gl=FI&ceid=FI:fi
https://news.google.com/rss/search?q=vegaaninen+OR+kasvipohjainen+ruoka+OR+kasviproteiini+when:2d&hl=fi&gl=FI&ceid=FI:fi
https://news.google.com/rss/search?q=eläinoikeudet+OR+turkistarhaus+OR+tehotuotanto+when:2d&hl=fi&gl=FI&ceid=FI:fi
https://animalia.fi/feed/
https://vegaaniliitto.fi/feed/
https://sey.fi/feed/

---

Huomioita:
- Google News -haut ovat luotettavin peruslähde, koska ne kattavat käytännössä kaikki isot mediat automaattisesti — säädä hakusanoja tarpeen mukaan.
- **Suomenkielisissä hauissa on `when:2d`-määrite jota englanninkielisessä ei ole.** Löydettiin 2026-09-02: Google Newsin RSS-haku palauttaa tuloksia RELEVANSSIJÄRJESTYKSESSÄ, ei päivämääräjärjestyksessä — vahvistettu oikeasti (ks. `PROCESS.md`:n vastaava iteraatio): `eläinoikeudet OR eläinsuojelulaki OR turkistarhaus` -haku palautti 100 osumaa joiden julkaisupäivät ulottuivat marraskuulle 2025 - heinäkuulle 2026, eli lähes kaikki `fetch_feeds.py`:n 30h-tuoreussuodattimen hylkäämiä. Suomenkielisen aihepiirin volyymi on niin pieni ettei tuoreita osumia riitä täyttämään 100 tulosta, jolloin vanhat tulokset dominoivat. `when:2d` (Googlen oma päivämääräsuodatin, lisätään kyselyyn hakusanana) korjaa tämän palauttamalla vain oikeasti tuoreet tulokset. Englanninkielinen `veganism OR "plant-based"` -haku EI kärsi samasta ongelmasta (aihepiirin volyymi riittää täyttämään 100 tulosta tuoreilla osumilla ilman `when:`-määrettä), joten sitä ei muutettu.
- **`tehotuotanto` lisättiin kolmanteen hakuun 2026-09-02** samassa yhteydessä: käyttäjän raportoima puuttunut uutinen (HS.fi: "Aktivistit paljastivat sikatilan ongelmat, Atria poisti tilan esittelyistään") ei täsmännyt mihinkään olemassa olevaan hakusanaan (`eläinoikeudet`/`eläinsuojelulaki`/`turkistarhaus`) vaikka aihe on selvästi eläinoikeusaktivismia tuotantoeläintiloilla — testattu oikeasti, `tehotuotanto` yksinään löysi tarinan eikä tuottanut kohinaa 14 päivän ikkunassa.
- **`kasviproteiini` lisättiin toiseen hakuun 2026-09-03**, samasta syystä: käyttäjän raportoima toinen puuttunut uutinen (Yle: sokkotesti liha-/vege-/hybridibolognesesta) ei täsmännyt mihinkään haussa, mutta samalla diagnoosilla löytyi ERI, myös puuttunut, aidosti relevantti tarina (Warkauden Lehti: "Pojat eivät uskalla syödä kasvisruokaa") joka löytyi `kasviproteiini`-termillä — testattu oikeasti, otettiin mukaan sen perusteella. **Alkuperäistä Yle-uutista itseään `kasviproteiini` ei löytänyt eikä mikään muukaan kokeiltu hakusana** (ks. `PROCESS.md`:n vastaava iteraatio täydelle listalle kokeilluista termeistä) — se ei siis ole hakusanaongelma vaan todennäköisesti Google Newsin oma indeksointi-/relevanssirajoitus, jota hakusanoja lisäämällä ei voi korjata.
- **`veganismi`/`kasviperäinen` korvattu `vegaani`:lla, ja `eläinsuojelulaki` poistettu kokonaan, 2026-09-18** — `vegan-news-feed-review`:n 13.9. viikkokatsaus ajoi `query_term_overlap.py`:n ensimmäistä kertaa oikeasti tätä hakua vasten ja vahvisti riippumattomasti saman löydöksen minkä työkalun rakennusvaiheen manuaalinen testi (ks. iteraatio 11) jo osoitti: `veganismi` ja `eläinsuojelulaki` olivat täysin kuolleita (0 osumaa) sekä 7 vrk:n että 30 vrk:n ikkunoissa, `kasviperäinen`/`vegaaninen` lähes yhtä kuolleita. `vegaani` (perusmuoto) testattiin ennen käyttöönottoa suoraan Googlea vasten — tuotti 2 osumaa 30 päivän ikkunassa (silti ohut, mutta enemmän kuin nolla) ilman kohinaa. Ks. `PROCESS.md`:n vastaava iteraatio ja katselmointien proposal-tiedostot (`~/.config/vegan-news/proposals/2026-09-13.md`) täydelle perustelulle.
- Blogien/pienempien julkaisujen feed-osoitteet muuttuvat välillä. Jos `fetch_feeds.py` valittaa jostain lähteestä stderr:iin, tarkista onko `/feed/`-polku yhä voimassa selaimessa.
- Voit lisätä lisää kohdennettuja hakuja, esim. `q=vegaani+ruoka` tai tietyn maan mediaa varten oman `gl=`/`ceid=`-parametrin.
- URL:t saa kirjoittaa tähän tiedostoon ihmisluettavassa muodossa (esim. `kasviperäinen` ä-kirjaimineen) — `fetch_feeds.py` prosentti-enkoodaa ei-ASCII-merkit automaattisesti ennen verkkopyyntöä, joten tätä ei tarvitse tehdä itse.
- `sey.fi/feed/` päivittyy usein mutta sisältö on valtaosin yksittäisiä eläinten pelastustarinoita — SKILL.md:n vaiheen 2 "Jätä pois" -sääntö suodattaa nämä pois; jos digest alkaa silti täyttyä lemmikkiuutisista, poista tämä feed tai tiukenna sääntöä.
- Muita lähteitä on tutkittu ja hylätty (mm. `oikeuttaelaimille.fi`, `vera.ngo`, `elainsuojeluasiamies.fi`, `elaintenystava.fi`) — syyt ja löydökset on kirjattu `PROCESS.md`:n iteraatio 3 -osioon, ei tänne, jotta tämä lista pysyy lyhyenä ja skannattavana.
