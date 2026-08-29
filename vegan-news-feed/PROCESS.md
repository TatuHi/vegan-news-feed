# Vegan News Feed — suunnitteluprosessi

Tämä dokumentti kuvaa miten tämä skilli syntyi ja miksi se on sellainen kuin on. Tarkoitus on kaksi asiaa: (1) auttaa tulevaa itseä (tai ketä tahansa muuta) ymmärtämään päätösten taustat, ja (2) toimia näyttönä siitä miten agenttien/skillien rakentamista lähestytään systemaattisesti — ei vain lopputulos vaan itse prosessi.

Rakenne noudattaa skill-creatorin peruskaavaa: **capture intent → draft → test → iterate**.

## 1. Capture intent

Ennen ensimmäistäkään riviä koodia tai promptia vastattiin neljään kysymykseen:

1. **Mitä skillin pitäisi mahdollistaa?** Tuoreiden veganismiin liittyvien uutisten haku, arviointi ja koostaminen ilman että käyttäjän tarvitsee itse selata useita lähteitä joka päivä.
2. **Milloin skillin pitäisi laueta?** Kun käyttäjä pyytää uutiskoostetta, mediaseurantaa tai sisältöideoita vegaaniaiheesta — myös lyhyillä, epämuodollisilla komennoilla.
3. **Mikä on odotettu tulostemuoto?** Yksi jäsennelty Discord-viesti, kiinteällä pohjalla, jotta lopputulos on ennustettava eikä vaihtele ajokerrasta toiseen.
4. **Tarvitaanko testitapauksia?** Kyllä osittain: haku/dedupointi/lähetys ovat objektiivisesti tarkistettavia (skripti joko toimii tai ei), mutta relevanssin arviointi ja tiivistelmien laatu ovat subjektiivisia — niitä ei kannata pakottaa numeeriseksi assertioksi, vaan arvioida lukemalla tulos.

## 2. Interview

Kaksi konkreettista kysymystä ratkaisi suurimman osan skillin sisällöstä:

- **Kieli:** sekä suomi että englanti → RSS-lähteet molemmilla kielillä, mutta tiivistelmät kirjoitetaan aina suomeksi yhtenäisyyden vuoksi.
- **Muoto:** yksi päivittäinen koontiviesti (ei yksittäisiä viestejä per uutinen) → tämä ohjasi sekä viestipohjaa että sitä, että relevanssin arviointi tehtiin pakolliseksi vaiheeksi (koonnissa ei voi näyttää kaikkea, joten jonkun on valittava).

## 3. Draft v1

Ensimmäinen versio jakoi työn tarkoituksella kahtia:

- **Deterministinen osa** (RSS-haku, dedupointi, Discord-lähetys) kirjoitettiin tavallisena Python-koodina (`scripts/`), koska nämä eivät hyödy harkinnasta — ne pitää tehdä samalla tavalla joka kerta, ja koodi on nopeampi ja luotettavampi kuin LLM näissä.
- **Harkintaa vaativa osa** (onko uutinen relevantti, mikä on hyvä tiivistelmä) jätettiin tarkoituksella agentin päättelyn varaan SKILL.md:n ohjeistamana, koska tätä ei voi kovakoodata sääntöinä ilman että laatu kärsii.

Riippuvuudet minimoitiin: `fetch_feeds.py` ja `post_discord.py` käyttävät vain Python-standardikirjastoa, jotta skilli toimii missä tahansa Claude Code -ympäristössä ilman `pip install`-vaihetta.

## 4. Iteraatio 2: mediaseuranta + sisältöideat

Projektin aikana kävi ilmi konkreettinen käyttötapaus: [Viral Vegansin viestintäkoordinaattori-ilmoitus](https://rekry.viralvegans.fi/jobs/8235700-viestintakoordinaattori-freelance), joka toivoo nimenomaan tekoälyagenttien ja automaatioiden rakentamista arjen viestintätyöhön kasvipohjaisen ruokajärjestelmän parissa.

Tämä johti kahteen muutokseen:

- **Kehystys vaihdettiin** puhtaasta julkisesta uutiskanavasta pienen viestintätiimin mediaseurantatyökaluksi — sama tekninen ratkaisu, mutta kuvaus ja käyttötarkoitus muuttuivat vastaamaan sitä mitä comms-rooli oikeasti tarvitsee.
- **Uusi vaihe lisättiin** (vaihe 4: sisältöideat): agentti poimii päivän uutisista 1–2 parasta lähtökohtaa omalle sisällölle ja ehdottaa kulman + ajankohtaisuusperustelun. Tämä sitoo skillin suoraan tehtävänkuvan "viestintämateriaalien ja lehdistötiedotteiden valmistelu" -kohtaan sen sijaan että se jäisi pelkäksi tiedoksiannoksi.

## 5. Testaus (ajettu 26.8.2026)

`evals/evals.json` sisältää kolme realistista testipromptia. Skilli ajettiin ensimmäistä kertaa oikeasti 26.8.2026 Claude Codessa: ensin tavallisena päiväkoontina Discordiin, myöhemmin samana päivänä myös muodollisena kolmen evalin läpikäyntinä samaa päivän raakadataa vasten (dry run — ei toista oikeaa lähetystä, koska yksi oli jo lähtenyt).

Havainnot:
- **Relevanssin arviointi (vaihe 2) osui hyvin.** Raakadatasta (21 kohdetta) karsittiin johdonmukaisesti markkinaraporttilistaukset, reseptit, ohimenevät "vegan"-maininnat ja aihepiirin ulkopuoliset osumat (esim. teollisuuskäyttöinen "plant-based" voiteluaine) — mitään oleellista ei jäänyt pois.
- **Tiivistelmät (vaihe 3) paljastivat konkreettisen puutteen.** Google Newsin `summary`-kenttä on lähes aina pelkkä otsikon toisto, ei oikea kuvaus artikkelista. Tämä johti kahteen uuteen pakolliseen sääntöön SKILL.md:hen: (1) rikasta ohut lähde WebFetch/WebSearch-työkalulla ennen tiivistelmän kirjoittamista, (2) käytä lopullisessa viestissä aina alkuperäisen julkaisijan suoraa linkkiä, ei Google Newsin uudelleenohjauslinkkiä.
- **Onnettomuuslöytö validoi molemmat säännöt kerralla.** Samana päivänä raakadatassa oli oikea, ei-lavastettu esimerkki: yksi juttu kolmena kopiona (2x Google News, 1x suora vegconomist-feedi). Tämä toimi käytännön testinä sekä duplikaattisäännölle että suora-linkki-säännölle — molemmat toimivat oikein, ja tapaus johti myöhemmin myös mekaaniseen lähes-duplikaattien tunnistukseen `fetch_feeds.py`:ssä (ks. iteraatio 3).
- **Sisältöideat (vaihe 4) olivat aitoja, ei pakotettuja.** Päivän datasta löytyi kaksi oikeasti käyttökelpoista kulmaa (brändäyskeskustelu "pitäisikö vegaani-sana pudottaa markkinoinnista", EU:n päätös burger/sausage-nimitysten säilyttämisen puolesta) ilman että jouduttiin venyttämään heikompaa materiaalia.

## 6. Iteraatio 3: laajennettu aihepiiri, luotettavuus ja tietoturva

Tämä oli tähänastisista iteraatioista laajin, ja se lähti käyttäjän konkreettisesta rajauspyynnöstä: "kaikki eläinoikeudet ja miten ne liittyvät Suomen poliittiseen tilaan on kiinnostavaa (myös globaalisti)". Tämä laajensi skillin kehystystä puhtaasta vegaaniuutisoinnista laajempaan eläinoikeuspolitiikan seurantaan.

**Aihepiirin laajennus:**
- SKILL.md:n vaiheen 2 "Pidä mukana" -kriteereihin lisättiin oma kohta eläinoikeuksille/eläinsuojelupolitiikalle (lainsäädäntö, EU-päätökset, järjestöjen kannanotot ja kampanjat) — muuten uudet lähteet olisivat vain suodattuneet pois relevanssiarviossa, koska vanha kriteeristö oli rajattu ruokaan.
- Uusia suomenkielisiä lähteitä tutkittiin ja testattiin oikeasti (HTTP-tason tarkistus, ei oletuksena "pitäisi toimia"): `animalia.fi/feed/` ja `vegaaniliitto.fi/feed/` lisättiin — toimivat teknisesti, mutta postaavat harvoin (n. kerran kuukaudessa), joten eivät osu joka päivä 30h-hakuikkunaan. `sey.fi/feed/` lisättiin harkiten: toimii teknisesti hyvin, mutta sisältö on valtaosin yksittäisiä lemmikkitarinoita, joten vaiheen 2 "Jätä pois" -sääntöön lisättiin erillinen kohta joka suodattaa ne pois.
- Neljä lähdettä tutkittiin ja hylättiin — syyt kirjattu tähän, ei enää `feeds.md`:hen (ks. alla, dokumentaatiosiivous):
  - **`oikeuttaelaimille.fi`** — ei RSS-syötettä lainkaan (Next.js-sivusto, ei löydettävissä feed-URL:ia).
  - **`vera.ngo`** — käyttäjän erikseen pyytämä tarkistus ("heidän somensa on hyvä ainakin"). Ei RSS:ää eikä blogikokoelmasivua; Squarespace-sivu joka ei tue `?format=rss`:ää (testattu, palauttaa `400 Unknown response format for page type`). Sisältö on käytännössä Instagram/Facebook-painotteinen, jota ei voi hakea tehokkaasti RSS:llä.
  - **`elainsuojeluasiamies.fi/feed/`** — tekninen RSS toimii, mutta virka lakkautettiin: viimeisin julkaisu joulukuulta 2023, sisällöllisesti kuollut lähde.
  - **`elaintenystava.fi/feed/`** (SEY:n oma julkaisu) — jätetty pois toistaiseksi, koska menee suurelta osin päällekkäin `sey.fi/feed/`:n kanssa.

**Luotettavuuden parannukset (`scripts/`):**
- `fetch_feeds.py`: uudelleenyrityslogiikka tilapäisille verkkovirheille (3 yritystä, 2s väli) — mutta EI ympäristötason verkkoestoille (403/connection refused/tunnel failed), koska niitä uudelleenyrittäminen ei korjaa, vain hidastaisi epäonnistumista.
- `fetch_feeds.py`: mekaaninen lähes-duplikaattien tunnistus (`normalize_title`) tunnistaa Google Newsin lisäämän "- Julkaisija"-suffiksin ja säilyttää duplikaattiparista version jolla on suora linkki ja kunnon kuvaus. Ei yritä tunnistaa eri sanamuotoisia otsikoita samasta tapahtumasta (esim. eri lehden oma otsikointi) — se jää edelleen agentin harkintaan, koska vaatii sisällön ymmärtämistä.
- `scripts/history.py` (uusi): cross-day-dedupointi. Tallentaa lähetettyjen uutisten otsikot/linkit `~/.config/vegan-news/sent_history.json`-tiedostoon, jotta sama tarina ei toistu useana peräkkäisenä päivänä 30h-hakuikkunan takia. SKILL.md:n vaihe 2 lukee tämän ennen relevanssiarviota.
- `scripts/run_daily.sh` (uusi): cron-turvallinen wrapper. Ratkaisee kolme päällekkäistä ympäristöongelmaa jotka paljastuivat vasta oikeassa ajossa: (1) `python3` PATH:ssa osoitti Anaconda 3.7:ään joka ei tue skriptien `list[str]`/`X | None` -syntaksia, (2) python.org:n 3.11-asennukselta puuttuivat SSL-juurivarmenteet, (3) Discordin Cloudflare-suoja pudotti Pythonin oletus-User-Agentin (HTTP 403, koodi 1010). Kaikki kolme olisivat aiheuttaneet hiljaisen epäonnistumisen ajastetussa ajossa ilman että kukaan olisi huomannut.
- `run_daily.sh`:ään lisättiin kaksikanavainen hälytys epäonnistumisesta (`trap ... ERR`): Discord-webhook JA riippumaton macOS-ilmoitus, koska pelkkä Discord-hälytys ei tavoittaisi ketään jos vika on juuri Discord-webhookissa itsessään.
- Huomio joka jätettiin tietoisesti korjaamatta: koneen `/usr/bin/python3` oli rikki (xcrun-arkkitehtuuriristiriita). Käyttäjä korjasi tämän itse asentamalla Command Line Toolsit uudelleen — mutta koska Python 3.9 ei silti tue skriptien `X | None`-syntaksia (vaatii 3.10+), `run_daily.sh` osoittaa edelleen tarkoituksella suoraan python.org:n 3.11-asennukseen.

**Tietoturvatapaus ja korjaus:**
- Discordin webhook-URL liikkui alunperin plaintext-tekstinä käyttäjän ensimmäisessä viestissä (osana ajastuskomentoesimerkkiä) ja sitä käytettiin suoraan komentoriveillä ennen kuin `.env`-erottelu rakennettiin. Tämä jäi pysyvästi talteen Claude Coden oman keskusteluhistorian jsonl-lokiin, mitä ei voi jälkikäteen siivota.
- Ratkaisu: webhook siirrettiin `~/.config/vegan-news/.env`-tiedostoon (`chmod 600`, oma kansio kokonaan skillin ja tulevan git-repon ulkopuolella), ja koko webhook rotatoitiin — vanha poistettiin Discordin DELETE-endpointilla, HTTP 404 vahvisti sen olevan jo mitätön.
- `.gitignore` ja `.env.example` lisättiin skillin juureen etukäteen, koska käyttäjä aikoo pushata tämän GitHubiin. Varmistettiin lisäksi grep-haulla ettei kumpikaan oikea webhook-arvo (vanha tai uusi) esiinny missään skillikansion tiedostossa.

**Dokumentaatiosiivous:** `feeds.md`:n "Huomioita"-osioon oli kertynyt useiden hylättyjen lähteiden yksityiskohtaiset tutkintaselostukset (ks. yllä) — tämä sisältö kuuluu tänne, ei `feeds.md`:hen, jonka tehtävä on pysyä lyhyenä ja skannattavana listana aktiivisista lähteistä. `feeds.md`:ssä on nyt vain lyhyt viittaus tähän dokumenttiin.

## 7. Iteraatio 4: itsearvioiva sisarskilli (vegan-news-feed-review)

Käyttäjä halusi ajastetun putkiston myös *parantavan* itseään ajan myötä, mutta eksplisiittisesti niin että ihminen hyväksyy muutokset — ei täysin autonomista itsemuokkausta. Tämä pyydettiin ennen päivittäisen cron-ajon käyttöönottoa, tietoisesti: kertyvä lähetyshistoria on arvokkaampaa jos katselmointi on suunniteltu alusta asti, ei liimattu päälle jälkikäteen.

**Arkkitehtuuripäätös: oma erillinen skilli, ei osa vegan-news-feediä.** Harkittiin myös samaan `SKILL.md`:hen lisättyä "viikkokatsaus"-vaihetta, mutta hylättiin: katselmointi on eri vastuu (kriittinen arviointi vs. tuotanto), eri kadenssi (viikoittainen/tarpeen mukaan vs. päivittäinen), ja mikä tärkeintä, sillä pitää olla eri oikeudet — luku vegan-news-feedin tiedostoihin, mutta EI KOSKAAN kirjoitusoikeutta niihin. Kahtena erillisenä skillinä tämä rajoitus on rakenteellinen (eri skilli, ei voi vahingossa saada Edit/Write-oikeutta toisen skillin tiedostoihin ilman että joku eksplisiittisesti sallii sen), ei vain kirjoitettu sääntö jota voisi unohtaa noudattaa.

**"Ehdota, älä sovella" -periaate konkreettisesti:**
- `vegan-news-feed-review` lukee `vegan-news-feed/references/feeds.md`:n ja `SKILL.md`:n (konteksti), sekä `~/.config/vegan-news/sent_history.json`:n (data).
- Se kirjoittaa löydöksensä VAIN `vegan-news-feed/proposals/{päivä}.md`-tiedostoon — ei koskaan `SKILL.md`:hen tai `feeds.md`:hen suoraan.
- Ehdotuksen soveltaminen on aina oma, ihmisen pyytämä, interaktiivinen askel — täsmälleen sama malli jota on käytetty jokaiseen tämän skillin muutokseen koko projektin ajan (agentti ehdottaa perusteluineen, ihminen sanoo "tee se").
- Discord-ilmoitus uudesta katselmoinnista käyttää samaa webhookia/kanavaa kuin päivittäinen digest, samalla hälytysmallilla kuin `run_daily.sh`:n virheilmoitukset.

**Muutos `vegan-news-feed`-puolelle jotta tämä ylipäätään toimii:** `scripts/history.py`:n `record`-komento tallensi aiemmin VAIN `title`+`link` — pudotti kaiken muun. Tämä oli riittävää cross-day-dedupointiin, mutta hyödytöntä laadun arvioinnille: katselmoiva skilli ei voi arvioida oliko tiivistelmä hyvä tai oliko sisältöidea aito, jos se näkee vain otsikon. `record` muutettiin säilyttämään item-objektin KAIKKI kentät (aiemmin: poimittiin vain title+link eksplisiittisesti; nyt: `dict(item)` + päivämäärä), ja `SKILL.md`:n vaihe 7 päivitettiin tallentamaan oikeasti lähetetty tiivistelmä/lähde jokaiselle uutiselle sekä jokainen vaiheen 4 sisältöidea omana `"type": "content_idea"` -kohteenaan. Taaksepäinyhteensopiva (vanha title/link-muoto toimii yhä).

`vegan-news-feed-review/scripts/run_weekly_review.sh` on tarkoituksella suunniteltu toimimaan yhtä hyvin ajettuna suoraan terminaalista milloin tahansa kuin cronista — katselmointi ei vaadi ajastusta ollakseen hyödyllinen, ja käyttäjä halusi eksplisiittisesti että sitä "voi myös ajaa merkityksellisesti cron-aikataulun ulkopuolella". Sama env/Python/SSL-turvallisuusmalli kuin `run_daily.sh`:ssa, mutta erillinen loki ja erillinen (valinnainen) cron-rivi.

**Käyttäjän esiin nostama datankatoriski, toteutettu iteraatiossa 5 (ks. alla):** jos Mac on sammuksissa tai unessa klo 8 kun `run_daily.sh` olisi ajastettu, cron ei herätä konetta eikä aja sitä uudelleen myöhemmin — kyseisen päivän uutiset jäävät kokonaan hakematta ja tallentamatta historiaan, mikä jättää aukon jota `vegan-news-feed-review` ei voi arvioida.

## 8. Iteraatio 5: puuttuvien päivien täyttäminen (backfill) ja aukkojen tunnistus

Jatkoa iteraatio 4:n kirjattuun mutta silloin toteuttamattomaan datankatoriski-huomioon. Samassa keskustelussa käyttäjä myös ehdotti että `vegan-news-feed` ja `vegan-news-feed-review` "keskustelisivat keskenään" reaaliaikaisesti relevanssiarvioinnin aikana (esim. "onko tätä aihetta käsitelty äskettäin"). Tämä ehdotus arvioitiin ja hylättiin sellaisenaan: `vegan-news-feed`:n vaihe 2 lukee jo suoraan jaettua `sent_history.json`-tiedostoa cross-day-dedupointiin, joten laajemman aihetason kuvion havaitseminen (ei vain tarkat duplikaatit) on luontevinta toteuttaa samana suorana luentana, ei elävänä kutsuna `vegan-news-feed-review`:hen. Elävä kutsu olisi purkanut juuri sen mitä iteraatio 4:ssä rakennettiin tarkoituksella: katselmointi pysyy asynkronisena, lukuoikeudella varustettuna eikä koskaan päivittäisen putken kriittisellä polulla — jos elävä kysely katselmointiskilliltä jumiutuisi tai epäonnistuisi, se ei saa koskaan estää tämän päivän oikean digestin lähettymistä. Aihetason kuvionhavaitseminen toteutettiin heti perään samassa iteraatiossa vaiheeseen 2: uusi "Aihetason tasapaino" -kappale käyttää TÄSMÄLLEEN samaa `history.py show`-kutsua joka jo ajetaan duplikaattitarkistukseen — ei uutta scriptiä eikä uutta historialuentaa. Se on tietoisesti tiebreaker, ei kova poissulkusääntö: jos kaksi muuten yhtä relevanttia ehdokasta kilpailee viimeisestä paikasta 8–10 kärkiuutisen joukossa, suositaan sitä joka tuo digestiin monipuolisuutta — mutta yksinään merkittävää uutista (esim. iso rahoituskierros) ei koskaan hylätä pelkän aihetoiston takia. Käsittelee myös taaksepäinyhteensopivuuden: ennen iteraatiota 3 tallennetuissa historiamerkinnöissä ei ole `summary`/`source`-kenttiä, jolloin ohje kehottaa käyttämään vain otsikkoa.

**Backfill-toteutus:**

- `scripts/history.py`:n `record`-komentoon lisättiin `--date VVVV-KK-PP` -valinta (oletus: tänään) — mahdollistaa merkintöjen tallentamisen historialliselle päivälle sen sijaan että kaikki tallentuisi aina tämän hetken päivämäärällä.
- Uusi `gaps`-komento (`history.py gaps --days N`) listaa mekaanisesti päivät joilta ei löydy YHTÄÄN merkintää — puhtaasti deterministinen, ei vaadi harkintaa, sopii siis skriptiin (sama periaate kuin muillakin `scripts/`-tiedoston toiminnoilla).
- **Ratkaistava ongelma joka paljastui suunnittelussa:** vanha vaihe 7 tallensi historiaan VAIN silloin kun oikeita uutisia löytyi ("ei uutisia tänään" -päivä ei jättänyt jälkeä). Tämä teki `gaps`-komennosta käyttökelvottoman — se ei olisi voinut erottaa "ajettiin, ei löytynyt mitään relevanttia" -päivää "ajo ei koskaan käynnistynyt" -päivästä, koska molemmat näyttäisivät identtisiltä (ei merkintöjä). Ratkaisu: vaihe 7 tallentaa nyt AINA yhden `"type": "run"` -merkinnän (`result`: `"sent"`/`"no_news"`/`"unrecoverable"`, `item_count`), riippumatta siitä oliko uutisia. Tämä on pieni mutta välttämätön muutos päivittäiseen työnkulkuun, ei vain backfill-ominaisuus sinänsä.
- **Jälkikäteen löytynyt ja korjattu aukko (samana päivänä, README-synkronoinnin yhteydessä):** `vegan-news-feed-review`:n `SKILL.md` kirjoitettiin ENNEN tätä run-merkintä-muutosta, joten sen vaihe 1/3 ei maininnut `"type": "run"` -kohteita lainkaan — katselmoiva skilli olisi siis hiljaisesti jättänyt huomiotta koko run-merkintädatan (mm. `no_news`-päivien määrän, `unrecoverable`-backfill-aukot) sen sijaan että olisi analysoinut sitä. Tämä ei ollut vain dokumentaatiopuute vaan todellinen käyttäytymisaukko: data oli olemassa historiassa mutta skillin ohjeet eivät kertoneet että sitä pitäisi katsoa. Korjattu: vaihe 1 listaa nyt kaikki kolme kohdetyyppiä eksplisiittisesti, vaihe 3 sai uuden analyysikysymyksen ajojen onnistumisesta, ja vaihe 5:n ehdotuspohja sai oman rivin ajotilastoille. Opetus tuleviin muutoksiin: kun `vegan-news-feed`:n historiaskeemaa laajennetaan, tarkista aina samalla ettei `vegan-news-feed-review` jää lukemaan vanhentunutta skeemaa.
- Backfill-työnkulku itse (uusi osio `SKILL.md`:ssä, "Puuttuvien päivien täyttäminen") on tietoisesti **pyydettäessä ajettava kyky, ei osa päivittäistä `run_daily.sh`-cronia**. Peruste: jos aukkojen etsintä/täyttö olisi automaattinen osa joka päivän ajoa, sen oma vika (esim. ylisuuri `--hours`-haku, backfill-logiikan kaatuminen) voisi hidastaa tai estää sen päivän OIKEAN digestin lähettymisen — sama "ei koskaan kriittisellä polulla" -periaate kuin katselmointiskillin arkkitehtuurissa yllä.
- Backfill lähettää oletuksena VAIN historiaan, ei Discordiin (myöhässä oleva "tämän päivän kooste" hämmentäisi kanavaa useita päiviä myöhässä) — käyttäjän oma ehdotus, toteutettu suoraan. Discordiin lähettäminen jälkikäteen on mahdollista vain jos eksplisiittisesti pyydetään yhdelle tietylle päivälle.
- **Tunnettu ja dokumentoitu rajoitus:** RSS-syötteet ovat liukuvia ikkunoita eivätkä säilytä vanhoja julkaisuja rajattomasti. Backfill toimii luotettavasti vain muutaman päivän (n. 1–5 vrk) vanhoille aukoille — tätä vanhemmille se silti yritetään, mutta tulos on todennäköisesti tyhjä/ohut, ja tällöin merkitään rehellisesti `"result": "unrecoverable"` sen sijaan että aukko jäisi hiljaa avoimeksi tai keksittäisiin sisältöä. Testattaessa `gaps --days 14` tuotannon historiaa vasten tämä näkyi konkreettisesti: kaikki 12.–25.8. näkyvät "aukkoina", mutta nämä eivät ole todellisia ohitettuja ajoja — skilli otettiin käyttöön vasta 26.8., joten näiltä päiviltä ei koskaan ollutkaan ajoa. Näitä ei siis täytetty backfillillä; se olisi ollut sekä turhaa (feedit eivät todennäköisesti enää sisällä niin vanhoja julkaisuja) että harhaanjohtavaa (ei ole aito katkos, koska mitään ei ollut rikki).

## 9. Iteraatio 6: cron ei koskaan oikeasti toiminut — löydettiin vasta oikealla laukaisulla

Tämän skillin cron-ajastus oli ollut käytössä useita päiviä (26.–29.8.2026), ja jokainen sitä ajan yksittäinen digest oli tosiasiassa lähtenyt käyttäjän manuaalisesta pyynnöstä ("aja se nyt, kone oli pois päältä") — käyttäjän Mac oli sattumalta ollut sammuksissa cronin ajastettuna kellonaikana joka kerta. Tämä iteraatio alkoi siitä kun päätettiin lopulta *oikeasti testata itse ajastusmekanismia*, ei vain `run_daily.sh`:ta interaktiivisesti — ja tämä testi paljasti, että cron ei olisi koskaan toiminut, riippumatta siitä olisiko kone ollut päällä.

**Löydös 1: `claude`-binaari puuttui cronin PATH:sta.** Ensimmäinen oikea cron-laukaisu (5 min lähiaikatestillä) epäonnistui heti `exit 127`:llä, lokissa `claude: command not found`. Sama luokan ongelma kuin `PYTHON311`:n kanssa aiemmin, mutta ei koskaan huomattu koska interaktiivinen shell löytää `claude`:n aina omasta PATH:staan. Korjaus: `run_daily.sh` (ja ennaltaehkäisevästi myös `run_weekly_review.sh`, vaikka sitä ei ole ajastettu) osoittaa nyt suoraan `~/.local/bin/claude`-polkuun `CLAUDE_BIN`-muuttujalla, samalla periaatteella kuin `PYTHON311`.

**Löydös 2, syvempi: `claude`-kirjautuminen ei ole tavoitettavissa cronista lainkaan.** Korjattuamme PATH-ongelman, seuraava oikea cron-laukaisu epäonnistui uudella tavalla: `exit 1`, viesti "Not logged in · Please run /login". Tämä toistui identtisenä myös simuloitaessa cronin suppeaa ympäristöä (`env -i`) interaktiivisesti — eli tämä EI ollut cron-spesifinen bugi vaan ympäristö-spesifinen. `claude --help` paljasti syyn: normaali `-p`-tila lukee OAuth-kirjautumisen macOS:n Keychainista, ja `--bare`-tila ohittaa sen tarkoituksella ("Anthropic auth is strictly ANTHROPIC_API_KEY or apiKeyHelper via --settings — OAuth and keychain are never read"). Cron on macOS:ssä toteutettu `com.vix.cron`-LaunchDaemonina, joka EI aja käyttäjän GUI-kirjautumisistunnon (Aqua-session) sisällä — ja Keychain-pääsy on sidottu juuri tähän istuntoon. Tästä syystä `claude`:n kirjautuminen ei koskaan olisi toiminut cronista, riippumatta PATH-korjauksesta tai siitä oliko kone päällä.

**Kaksi ratkaisuvaihtoehtoa punnittiin käyttäjän kanssa:**
1. Hanki erillinen Anthropic API-avain (console.anthropic.com) ja käytä `claude --bare` + `ANTHROPIC_API_KEY` — taattu toimiva (dokumentoitu käyttäytyminen), mutta vaatii erillisen, tokeneittain laskutettavan API-avaimen olemassa olevan tilauksen päälle.
2. Vaihda ajastusmekanismi cronista macOS:n LaunchAgentiin (~/Library/LaunchAgents, ladataan `launchctl bootstrap gui/<uid>`) — LaunchAgent ajetaan käyttäjän GUI-istunnon sisällä (`domain = gui/<uid>`, oikea `asid`), joten Keychain-pääsyn pitäisi säilyä normaalina ilman erillistä avainta.

Käyttäjä valitsi vaihtoehdon 2 (ei uutta kustannusta, käyttää olemassa olevaa kirjautumista). **Tämä testattiin oikeasti**, ei vain oletettu toimivaksi: asennettiin LaunchAgent lähiajan `StartCalendarInterval`-arvolla, odotettiin sen laukeamista, ja vahvistettiin `launchctl print`:illä että ajo päättyi `last exit code = 0` ja että oikea kooste lähti Discordiin ja tallentui historiaan. Vasta tämän jälkeen LaunchAgent päivitettiin pysyvään klo 13:00 -aikatauluun ja crontab poistettiin kokonaan (`crontab -r`) — cron ja LaunchAgent eivät jääneet ajamaan samaa työtä rinnakkain.

**Sivuhavainto ajastusmuutoksen aikana:** suorat `crontab <tiedosto>`-kirjoitukset (ei `-l`-luvut) jumiutuivat toistuvasti kun agentti yritti ajaa niitä itse, todennäköisesti odottamattoman lupakyselyn takia jota ei näkynyt agentille asti — `launchctl bootstrap`/`bootout`-kutsut sen sijaan toimivat agentilta suoraan ilman ongelmia. Käyttäjä joutui ajamaan crontab-kirjoitukset itse `!`-etuliitteellä. Tästä ei tehty johtopäätöstä LaunchAgentin puolesta sinänsä (syy on lupakyselyssä, ei crontabissa itsessään), mutta se osaltaan vahvisti päätöstä siirtyä pois cronista kokonaan.

**Yleisempi opetus, kirjattu koska se pätee laajemminkin:** interaktiivinen testaus (agentti ajaa skriptiä suoraan Bash-työkalulla) ei riitä todistamaan että ajastettu, taustalla ajettava versio toimii — vain oikea laukaisu ajastusmekanismin kautta paljastaa ympäristön omat rajoitukset (PATH, Keychain-istunto, jne.). Tätä samaa periaatetta sovellettiin jo `run_daily.sh`:n alkuperäisessä rakentamisessa (Python-polku, SSL-varmenteet, User-Agent) mutta ei osattu soveltaa itse ajastusmekanismiin ennen kuin se oikeasti testattiin.
