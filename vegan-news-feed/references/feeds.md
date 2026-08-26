# RSS-lähteet

Yksi URL per rivi. Rivit jotka alkavat `#` ohitetaan. `fetch_feeds.py` lukee tämän tiedoston oletuksena.

Kieli päätellään lähteen perusteella alla olevissa kommenteissa — jos lisäät uuden lähteen, merkitse kieli riville `# lang:fi` tai `# lang:en` edeltävälle kommenttiriville jos se ei ole ilmeinen URL:sta.

## Englanti

https://news.google.com/rss/search?q=veganism+OR+%22plant-based%22&hl=en-US&gl=US&ceid=US:en
https://vegconomist.com/feed/
https://plantbasednews.org/feed/

## Suomi

https://news.google.com/rss/search?q=veganismi+OR+kasviperäinen&hl=fi&gl=FI&ceid=FI:fi
https://news.google.com/rss/search?q=vegaaninen+OR+kasvipohjainen+ruoka&hl=fi&gl=FI&ceid=FI:fi
https://news.google.com/rss/search?q=eläinoikeudet+OR+eläinsuojelulaki+OR+turkistarhaus&hl=fi&gl=FI&ceid=FI:fi
https://animalia.fi/feed/
https://vegaaniliitto.fi/feed/
https://sey.fi/feed/

---

Huomioita:
- Google News -haut ovat luotettavin peruslähde, koska ne kattavat käytännössä kaikki isot mediat automaattisesti — säädä hakusanoja tarpeen mukaan.
- Blogien/pienempien julkaisujen feed-osoitteet muuttuvat välillä. Jos `fetch_feeds.py` valittaa jostain lähteestä stderr:iin, tarkista onko `/feed/`-polku yhä voimassa selaimessa.
- Voit lisätä lisää kohdennettuja hakuja, esim. `q=vegaani+ruoka` tai tietyn maan mediaa varten oman `gl=`/`ceid=`-parametrin.
- URL:t saa kirjoittaa tähän tiedostoon ihmisluettavassa muodossa (esim. `kasviperäinen` ä-kirjaimineen) — `fetch_feeds.py` prosentti-enkoodaa ei-ASCII-merkit automaattisesti ennen verkkopyyntöä, joten tätä ei tarvitse tehdä itse.
- `sey.fi/feed/` päivittyy usein mutta sisältö on valtaosin yksittäisiä eläinten pelastustarinoita — SKILL.md:n vaiheen 2 "Jätä pois" -sääntö suodattaa nämä pois; jos digest alkaa silti täyttyä lemmikkiuutisista, poista tämä feed tai tiukenna sääntöä.
- Muita lähteitä on tutkittu ja hylätty (mm. `oikeuttaelaimille.fi`, `vera.ngo`, `elainsuojeluasiamies.fi`, `elaintenystava.fi`) — syyt ja löydökset on kirjattu `PROCESS.md`:n iteraatio 3 -osioon, ei tänne, jotta tämä lista pysyy lyhyenä ja skannattavana.
