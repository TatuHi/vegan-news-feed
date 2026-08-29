---
name: vegan-news-feed
description: Toimii pienen viestintätiimin mediaseurantana veganismiin ja kasvipohjaiseen ruokaan liittyville uutisille suomeksi ja englanniksi — hakee tuoreet uutiset, arvioi niiden uutisarvon ja relevanssin, kirjoittaa lyhyet suomenkieliset tiivistelmät, poimii 1-2 kiinnostavimmasta uutisesta valmiin some-postaus- tai lehdistötiedote-kulmaehdotuksen, ja muotoilee koko koosteen yhdeksi päivittäiseksi viestiksi Discordiin webhookin kautta. Käytä tätä skilliä aina kun käyttäjä pyytää päivittämään, ajamaan tai koostamaan vegaaniuutiskoosteen tai mediaseurannan, "vegan news feedin", sisältöideoita päivän uutisista, tarkistamaan päivän/tämän viikon vegaaniuutiset, tai testaamaan/iteroimaan tätä uutisagenttia — myös lyhyillä komennoilla kuten "aja uutispäivitys", "koosta tämän päivän vegaaniuutiset" tai "lähetä koonti Discordiin". Käytä myös kun käyttäjä pyytää täyttämään puuttuvia päiviä historiaan (backfill) tai tarkistamaan onko ajoja jäänyt välistä, esim. "täytä puuttuvat päivät historiaan" tai "onko ajoja jäänyt välistä".
---

# Vegan News Feed

Tämä skilli toimii kahdessa roolissa yhtä aikaa: se on **mediaseurantatyökalu** pienelle viestintätiimille (nostaa esiin mitä alalla tapahtuu ja ehdottaa valmiita sisältökulmia) ja **päivittäinen uutiskooste** joka päätyy Discordiin. Putki on jaettu tarkoituksella kahteen osaan:

- **Deterministinen osa** (haku, dedupointi, lähetys) hoidetaan `scripts/`-kansion Python-skripteillä, koska ne eivät vaadi harkintaa ja on parempi tehdä samalla tavalla joka kerta.
- **Harkintaa vaativa osa** (onko uutinen oikeasti relevantti, mikä on hyvä tiivistelmä, mitkä tarinat ovat päiväyksen tärkeimmät) tehdään sinun päättelylläsi näiden ohjeiden mukaan. Älä yritä automatisoida tätä osaa skriptillä — se on koko skillin ydin.

## Työnkulku

### 1. Hae raakadata

```bash
python3 scripts/fetch_feeds.py --hours 30 --output /tmp/vegan_news_raw.json
```

Tämä hakee `references/feeds.md`-tiedostossa listatut RSS-syötteet (suomi + englanti), suodattaa viimeisen 30 tunnin sisällä julkaistut, ja tallentaa listan JSON-objekteja: `title`, `link`, `source`, `published`, `language`, `summary` (feedin oma lyhyt kuvaus, ei sinun kirjoittamasi). Jos jokin syöte epäonnistuu, skripti tulostaa varoituksen stderr:iin mutta jatkaa muiden kanssa.

Lue tuloste sisään ennen seuraavaa vaihetta.

**Jos `fetch_feeds.py` ei pääse verkkoon (sandbox-ympäristöt, esim. Cowork):**

Osa ympäristöistä (mm. Cowork-sandbox) sallii ulospäin suuntautuvat yhteydet vain tietyille whitelistatuille domaineille, eikä RSS-lähteisiin (`vegconomist.com`, `plantbasednews.org`, `news.google.com`, ...) tällöin pääse suoraan Python-skriptillä. Tunnusmerkki: kaikki tai lähes kaikki syötteet epäonnistuvat samalla virheellä, jossa lukee esim. "Tunnel connection failed", "403" tai "Connection refused" — tämä on ympäristön verkkoesto, ei feedin oma vika, eikä sitä kannata yrittää korjata skriptiä säätämällä.

Toimi tällöin näin skriptin sijaan:

1. Aja `fetch_feeds.py` kerran nähdäksesi kaatuuko se yllä kuvatulla tavalla kaikkien tai lähes kaikkien lähteiden kohdalla.
2. Jos kaatuu: hae jokainen `references/feeds.md`-tiedoston URL erikseen `WebFetch`-työkalulla. Pyydä promptissa listaamaan kaikki kohteet, jotka on julkaistu haluamasi tuntimäärän (oletus 30h) sisällä nykyhetkestä, kunkin osalta otsikko, tarkka linkki, julkaisuaika ja kuvaus/tiivistelmä — älä anna WebFetchin itse tiivistää tai karsia.
3. Jos `WebFetch` palauttaa `ROBOTS_DISALLOWED` jollekin feed-URL:lle (yleistä juuri `/feed/`-osoitteille ja Google Newsin RSS-hauille), kokeile samaa lähdettä sen tavallisen selattavan listaussivun kautta (esim. `vegconomist.com/` etusivu tai `plantbasednews.org/all/`) `/feed/`-URL:n sijaan — nämä eivät yleensä ole robots-estettyjä.
4. Täytä puuttuvia tai ohuita lähteitä (erityisesti suomenkieliset, joita on listalla vain yksi) `WebSearch`-työkalulla kohdennetuilla hauilla (esim. "vegaani uutinen", "kasvipohjainen uutinen [kuukausi vuosi]"). Tarkista jokaisen osuman julkaisupäivä erikseen (esim. avaamalla artikkeli `WebFetch`illä) ennen kuin luotat siihen tuoreena — hakutulokset nostavat usein esiin myös vanhoja artikkeleita.
5. Jatka putkea normaalisti vaiheesta 2 eteenpäin näin kootulla datalla. Mainitse lopullisessa vastauksessasi käyttäjälle lyhyesti, että haku tehtiin tällä varapolulla suoran skriptiajon sijaan, jotta läpinäkyvyys säilyy.

Tämä varapolku on hitaampi ja vaatii enemmän harkintaa kuin skripti (mm. duplikaattien poisto ja 30h-suodatus on tehtävä itse silmämääräisesti), joten käytä sitä vain kun skripti oikeasti epäonnistuu ympäristösyistä — älä oleta tätä oletuspoluksi ympäristöissä joissa skripti toimii normaalisti.

### 2. Arvioi relevanssi ja valitse parhaat

Käy jokainen kohde läpi ja päätä, kuuluuko se mukaan. Tämä on nimenomaan se osa jota skripti ei osaa tehdä.

**Tarkista ensin lähetyshistoria (vältä saman tarinan lähettäminen monena peräkkäisenä päivänä).** 30h-hakuikkuna tarkoittaa että sama uutinen voi näkyä raakadatassa kahtena tai useampana peräkkäisenä päivänä. Aja:

```bash
python3 scripts/history.py show --days 5
```

Tämä tulostaa JSON-listan viimeisen 5 päivän aikana tallennetuista kohteista (tyhjä historia → `[]`, ei virhe). Lista sisältää sekä `"type": "news"` että `"type": "content_idea"` -kohteita (ks. vaihe 7) — duplikaattitarkistuksessa kiinnostavat vain `"news"`-kohteet, `"content_idea"`-kohteet voit ohittaa tässä. Käytä `"news"`-kohteita vaiheen 2 "Jätä pois" -kohdan duplikaattisäännön kanssa: skripti ei itse päätä mikä on "sama tarina" eri päivien välillä — se on sinun harkintaasi, aivan kuten saman päivän sisäinen dedupointikin.

**Pidä mukana:**
- Uutinen josta veganismi/kasvipohjaisuus on pääaihe, ei sivumaininta (esim. tuotelanseeraus, tutkimus, lainsäädäntö, markkinakehitys, kulttuuri-ilmiö)
- Merkittävät yritys- tai markkinauutiset vegaanialalta (rahoituskierrokset, isot lanseeraukset, sulkemiset)
- Eläinoikeudet ja eläinsuojelupolitiikka laajemmin, ei vain ruoka: lainsäädäntö (esim. eläinsuojelulaki, turkistarhauskielto), EU-tason päätökset, järjestöjen (Animalia, Oikeutta eläimille, Vegaaniliitto) poliittiset kannanotot ja kampanjat, tuotantoeläinten kohtelua koskevat päätökset. Sekä Suomen että kansainvälinen/EU-taso kiinnostavat.

**Jätä pois:**
- Reseptit ja blogitekstit, ellei kyseessä ole oikeasti uutinen niiden ympärillä
- Artikkelit joissa "vegan" mainitaan vain ohimennen (esim. ravintola-arvostelu jossa on "myös vegaanivaihtoehtoja")
- Ilmeinen mainossisältö
- Yksittäiset lemmikki-/pelastuseläintarinat joissa ei ole poliittista tai yhteiskunnallista ulottuvuutta (esim. "löytökissa sai kodin") — nämä eivät ole eläinoikeuspolitiikkaa vaikka lähde on eläinsuojelujärjestö
- Duplikaatit: `fetch_feeds.py` poistaa jo mekaanisesti tarkat linkki- ja otsikkoduplikaatit (mm. Google Newsin lisäämä "- Julkaisija"-loppu tunnistetaan, ja kahdesta samasta jutusta säilytetään versio jolla on suora linkki/kunnon kuvaus). Tämä EI kuitenkaan tunnista eri julkaisijan itse kirjoittamaa, kokonaan eri sanamuotoista otsikkoa samasta tapahtumasta (esim. "EU hylkäsi X" vs. "Lehdistötiedote: MEPs ehdottavat Y" samasta äänestyksestä) — se on edelleen sinun harkintaasi: jos kaksi kohdetta raakadatassa kertovat samasta tapahtumasta eri sanoin, valitse kattavin/luotettavin ja jätä muut pois.
- Tarinat jotka olennaisesti sama kuin jokin `history.py show`:n palauttama viimeaikainen lähetys (sama tapahtuma, sama otsikko/aihe) — **paitsi** jos tarinaan on tullut aidosti uusi käänne sen jälkeen (esim. tuomioistuimen päätös aiemmin uutisoituun kanteeseen, uusi rahoituskierros samalle yritykselle) — silloin päivitys on oma uutisensa eikä duplikaatti

**Aihetason tasapaino (tasapainottava kriteeri, ei kova poissulkusääntö).** Sama `history.py show`-kutsu jonka jo ajoit yllä duplikaattitarkistukseen kertoo myös millaisia AIHEITA on toistunut viime päivinä — ei vain tarkkoja tarinoita. Jos viimeaikaiset `"news"`-kohteet (`summary`/`source`-kentät, kun saatavilla — vanhemmissa, ennen tätä ominaisuutta tallennetuissa merkinnöissä näitä ei vielä ole, ja se on ok, käytä silloin vain otsikkoa) osoittavat että digest on painottunut voimakkaasti yhteen teemaan (esim. kolme peräkkäistä rahoituskierrosuutista, ei yhtään tutkimus- tai politiikkauutista moneen päivään), käytä tätä yhtenä tekijänä kun valitset TASAVERTAISTEN ehdokkaiden väliltä alla olevassa 8–10 kärkiuutisen rajauksessa: suosi uutista joka tuo digestiin jotain viime päivinä näkymätöntä, jos muut relevanssikriteerit ovat muuten tasapainossa.

Tämä ei tarkoita että toistuvaa aihetta pitäisi hylätä — aidosti merkittävä uutinen (esim. iso rahoituskierros) kuuluu mukaan vaikka eilenkin oli rahoitusuutinen. Tämä on tiebreaker kahden muuten samanarvoisen ehdokkaan välillä, ei peruste jättää yksinään merkittävä uutinen pois.

Valitse enintään 8–10 kärkiuutista. Jos relevantteja on vähemmän, älä täytä listaa heikommilla — lyhyempi koonti on parempi kuin laimennettu.

### 3. Kirjoita tiivistelmät

**Rikasta ohuet lähteet ensin.** Google Newsin RSS-syötteiden `summary`-kenttä on lähes aina vain otsikon toisto (esim. "Plant-Based Chelators Market&nbsp;&nbsp;Future Market Insights"), ei oikea kuvaus artikkelin sisällöstä. Ennen kuin kirjoitat tiivistelmän valitulle uutiselle, tarkista `summary`-kentän todellinen sisältö:

- Jos `summary` kertoo jotain todellista tapahtumasta (tyypillistä vegconomist- ja Plant Based News -lähteille, joilla on oma RSS-kuvaus), voit kirjoittaa tiivistelmän suoraan sen pohjalta.
- Jos `summary` on käytännössä pelkkä otsikon toisto tai muuten liian ohut kertomaan mitä tapahtui (tyypillistä Google News -lähteille), hae oikea sisältö ennen tiivistelmän kirjoittamista: kokeile ensin `WebFetch`iä artikkelin linkkiin, ja jos se osuu Googlen consent-seinään tai muuten epäonnistuu (yleistä juuri Google Newsin uudelleenohjauslinkeille), tee `WebSearch` otsikolla/aiheella ja kokoa tiivistelmä hakutulosten pohjalta. Älä koskaan kirjoita tiivistelmää pelkän otsikon perusteella arvaamalla mitä artikkeli voisi sisältää.

Tämä koskee vain vaiheessa 2 valittuja kärkiuutisia — ei kaikkia raakadatan 15–20 osumaa — joten lisätyö pysyy rajattuna.

**Käytä lopullisessa viestissä aina alkuperäisen julkaisijan suoraa linkkiä, ei Google Newsin uudelleenohjauslinkkiä.** `raakadata`:n `link`-kenttä on Google News -lähteille muotoa `https://news.google.com/rss/articles/...` — tämä ei ole artikkelin oikea osoite vaan Googlen välityslinkki, joka usein näyttää lukijalle ensin consent-seinän. Kun teet edellisen kohdan mukaisen rikastuksen (`WebFetch`/`WebSearch`), talteen jää lähes aina myös alkuperäisen julkaisijan suora URL (esim. `WebSearch`-hakutuloksen linkki, tai `WebFetch`in seuraama uudelleenohjauskohde) — käytä sitä vaiheen 5 `🔗`-linkkinä Google Newsin linkin sijaan. Jos suoraa URL:ia ei mistään syystä löydy, käytä Google News -linkkiä varapolkuna mieluummin kuin jätät linkin kokonaan pois.

Kirjoita jokaiselle valitulle uutiselle 1–2 lauseen tiivistelmä **suomeksi**, riippumatta alkuperäisestä kielestä. Tiivistelmän tulee kertoa mitä tapahtui, ei vain aihetta ("Uusi tutkimus Oxfordin yliopistosta" ei riitä — kerro mitä tutkimus löysi). Jos lähde on englanninkielinen, merkitse se selvästi lähteen yhteyteen.

### 4. Poimi 1–2 sisältöideaa

Tämä vaihe tekee koosteesta hyödyllisen viestintätiimille pelkän tiedoksiannon sijaan. Käy läpi vaiheen 2 valinnat ja poimi niistä 1–2, jotka olisivat parhaita lähtökohtia **omalle** sisällölle (ei pelkkää uutisen referointia) — esim. uutinen josta on luonteva ottaa kantaa, kytkeä omaan työhön, tai kommentoida asiantuntijana.

Kirjoita jokaisesta poiminnasta:
- **Kulma**: yhden lauseen ehdotus siitä mistä näkökulmasta aihetta kannattaisi lähestyä some-postauksessa tai lehdistötiedotteessa (ei valmista tekstiä, vaan suuntaviiva jota viestintäihminen voi lähteä työstämään)
- **Miksi juuri nyt**: yksi lause siitä miksi aihe on ajankohtainen tai kiinnostava juuri tänään

Jos mikään päivän uutisista ei oikeasti anna hyvää lähtökohtaa omalle sisällölle, on täysin ok jättää tämä osio pois — pakotettu, laiha sisältöidea on huonompi kuin ei mitään.

### 5. Muotoile viesti

Käytä AINA tätä täsmällistä pohjaa:

```
🌱 **Vegaaniuutiset – {pp.kk.vvvv}**

**1. [Otsikko suomeksi tai käännettynä]**
{Tiivistelmä.} — *{Lähde}*
🔗 {linkki}

**2. ...**

💡 **Sisältöideat**
- **{Aihe}**: {Kulma}. _{Miksi juuri nyt}_
- **{Aihe}**: {Kulma}. _{Miksi juuri nyt}_

_{N} uutista, lähteinä {lähteiden lukumäärä} eri julkaisua._
```

"💡 Sisältöideat" -osio jätetään kokonaan pois viestistä (ei tyhjää otsikkoa) jos vaiheessa 4 ei löytynyt hyviä poimintoja.

Jos yhtään relevanttia uutista ei löytynyt, lähetä silti lyhyt viesti: "🌱 **Vegaaniuutiset – {pvm}** — Ei merkittäviä uutisia tänään." Näin näet putken toimivan myös hiljaisina päivinä.

### 6. Lähetä Discordiin

```bash
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python3 scripts/post_discord.py --message-file /tmp/vegan_digest.md
```

`DISCORD_WEBHOOK_URL` kannattaa asettaa ympäristömuuttujaksi (esim. `.env`-tiedostoon tai shellin profiiliin), ei koskaan kovakoodata skriptiin tai committia repoon. Skripti pilkkoo viestin automaattisesti useampaan Discord-viestiin jos se ylittää 2000 merkin rajan.

### 7. Tallenna ajo historiaan

**Tämä vaihe ajetaan AINA, myös silloin kun uutisia ei löytynyt.** Syy: `history.py gaps` (ks. "Puuttuvien päivien täyttäminen" alla) päättelee ohitetut ajot siitä, että päivältä ei löydy YHTÄÄN merkintää — jos "ei uutisia tänään" -päivät eivät jättäisi mitään jälkeä historiaan, niitä ei voisi erottaa päivistä jolloin ajo ei käynnistynyt lainkaan (esim. kone oli unessa).

```bash
python3 scripts/history.py record --items-file /tmp/vegan_digest_items.json
```

`/tmp/vegan_digest_items.json` on lista objekteja. Sisällytä aina täsmälleen yksi **run-merkintä**, ja sen lisäksi (jos oli uutisia) yksi kohde per lähetetty uutinen ja yksi per vaiheen 4 sisältöidea, erotettuna `type`-kentällä:

```json
[
  {
    "type": "run",
    "title": "run-merkintä",
    "result": "sent",
    "item_count": 9
  },
  {
    "type": "news",
    "title": "Otsikko suomeksi",
    "link": "https://... (sama suora linkki jota käytit viestissä)",
    "summary": "Sama tiivistelmä jonka kirjoitit vaiheessa 3.",
    "source": "Alkuperäinen lähde",
    "language": "en"
  },
  {
    "type": "content_idea",
    "title": "Aihe (vaiheen 4 otsikko)",
    "link": "https://... (sen uutisen linkki johon idea liittyy)",
    "angle": "Vaiheen 4 Kulma-teksti",
    "why_now": "Vaiheen 4 Miksi juuri nyt -teksti"
  }
]
```

`"run"`-kohteen `result` on `"sent"` jos viestissä oli oikeita uutisia, tai `"no_news"` jos lähetettiin "ei uutisia tänään" -viesti. `item_count` on lähetettyjen uutisten lukumäärä (0 no_news-tapauksessa). "Ei uutisia tänään" -päivänä items-file sisältää VAIN tämän yhden run-kohteen, ei muuta.

Tallenna joka valitulle uutiselle yksi `"news"`-kohde (käytä samaa tiivistelmää ja samaa suoraa linkkiä jotka päätyivät oikeaan viestiin) ja joka vaiheen 4 sisältöidealle yksi `"content_idea"`-kohde. Skripti leimaa kaikki kohteet tämänpäiväisellä päivämäärällä ja siivoaa yli 30 päivää vanhat merkinnät pois automaattisesti — et tarvitse erillistä siivousaskelta. Muut kentät kuin `title` säilyvät sellaisenaan historiaan, joten tämä muoto ei ole kiveen hakattu — tärkeintä on että oikea sisältö (ei vain otsikko) tallentuu, ja että run-merkintä kirjataan joka kerta.

## Puuttuvien päivien täyttäminen (backfill)

Cron ei herätä nukkuvaa/sammutettua Macia (ks. "Ajastaminen" alla) — jos ajo jää sen takia välistä, se päivä puuttuu historiasta kokonaan. Tämä haittaa erityisesti `vegan-news-feed-review`-skilliä, joka arvioi historiaa: aukko näyttää samalta kuin "ei uutisia tänään" ilman run-merkintää tarkistamatta erikseen. Tätä varten on olemassa erillinen, **pyydettäessä ajettava** kyky (ei osa päivittäistä automaatiota — ks. peruste lopussa) täyttää puuttuvat päivät jälkikäteen.

**Tärkeä rajoitus ennen kuin aloitat:** RSS-syötteet ovat liukuvia ikkunoita — ne sisältävät vain viimeisimmät julkaisut, eivät koko historiaa. Mitä vanhempi aukko, sitä epätodennäköisempää että lähteet sisältävät enää sen päivän julkaisuja. Käytännössä tämä toimii luotettavasti vain muutaman päivän (esim. 1–5 vrk) vanhoille aukoille. Vanhemmille aukoille yritä silti, mutta kerro käyttäjälle rehellisesti jos dataa ei löytynyt — älä jätä hiljaa yrittämättä, mutta älä myöskään keksi sisältöä.

**Työnkulku:**

1. **Etsi aukot:**
   ```bash
   python3 scripts/history.py gaps --days 14
   ```
   Tulostaa listan päivistä joilta ei löydy yhtään merkintää (ei edes run-merkintää). Jos lista on tyhjä, ei ole mitään täytettävää — kerro se käyttäjälle ja lopeta.

2. **Hae laaja aikaikkuna kerralla** (kattaen vanhimmasta aukkopäivästä nykyhetkeen):
   ```bash
   python3 scripts/fetch_feeds.py --hours <riittävä> --output /tmp/vegan_news_backfill_raw.json
   ```
   Laske `--hours` niin että se ulottuu vanhimman aukkopäivän alkuun asti.

3. **Ryhmittele** haettu data `published`-kentän (ei hakuhetken) perusteella takaisin oikeille kalenteripäiville.

4. **Kullekin puuttuvalle päivälle erikseen**, sen päivän datalla: suorita normaalit vaiheet 2–3 (relevanssiarvio + suomenkieliset tiivistelmät) täsmälleen samalla harkinnalla kuin tavallisessa ajossa. Vaihetta 4 (sisältöideat) ei tarvitse tehdä backfillissa — ideoiden ajankohtaisuus ("miksi juuri nyt") ei ole enää mielekäs jälkikäteen.

5. **ÄLÄ lähetä Discordiin oletuksena.** Myöhässä oleva, päiviä vanha "tämän päivän kooste" hämmentäisi kanavaa. Tallenna vain historiaan. Jos käyttäjä eksplisiittisesti pyytää että jokin tietty puuttuva päivä myös lähetetään jälkikäteen Discordiin, tee se vasta erikseen pyydettäessä (vaihe 6, samalla tavalla kuin normaalisti — muista tässä tapauksessa myös merkitä `"backfilled": true`).

6. **Tallenna historiaan oikealla päivämäärällä:**
   ```bash
   python3 scripts/history.py record --items-file /tmp/backfill_items_PAIVA.json --date VVVV-KK-PP
   ```
   Merkitse JOKAINEN kohde (myös run-merkintä) kentällä `"backfilled": true`, jotta `vegan-news-feed-review` osaa erottaa nämä oikeista päivittäisistä ajoista. Jos päivälle ei löytynyt YHTÄÄN dataa (feedit ovat todennäköisesti jo unohtaneet sen), tallenna silti run-merkintä `"result": "unrecoverable", "backfilled": true` — älä jätä päivää hiljaa avoimeksi loputtomiin, vaan kirjaa selkeästi että sitä yritettiin mutta ei onnistuttu.

**Miksi tämä ei ole osa päivittäistä cron-ajoa:** jos aukon etsintä/täyttö olisi automaattinen osa joka päivän `run_daily.sh`-ajoa, sen oma mahdollinen vika (esim. liian laaja `--hours`-haku hidastaa ajoa, tai backfill-logiikka kaatuu) voisi estää tai hidastaa sen päivän OIKEAN digestin lähettymistä. Pitämällä backfill erillisenä, pyydettäessä ajettavana kykynä, päivittäinen polku pysyy yksinkertaisena ja luotettavana, ja backfill voidaan ajaa turvallisesti milloin tahansa huomataan aukko (esim. "täytä puuttuvat päivät historiaan").

## Ajastaminen

**Käytä macOS:n LaunchAgentia, ei crontabia.** Tämä on opittu kantapään kautta 2026-08-29: cron on toteutettu macOS:ssä `com.vix.cron`-nimisenä LaunchDaemonina, joka EI aja ohjelmia käyttäjän varsinaisen kirjautumisistunnon (Aqua/GUI-session) sisällä. `claude`-komennon kirjautuminen (OAuth) lukee tunnistetiedot macOS:n avainnipusta (Keychain), johon vain oikean kirjautumisistunnon sisällä ajettavilla prosesseilla on pääsy — cronista ajettuna `claude -p` epäonnistuu viestillä "Not logged in · Please run /login", vaikka `run_daily.sh` itsessään toimisi täydellisesti. Tätä ei huomattu ennen kuin ajo laukaistiin oikeasti cronista, ei vain interaktiivisesti terminaalissa (ks. `PROCESS.md`:n iteraatio 6).

LaunchAgent (toisin kuin LaunchDaemon/cron) ajetaan käyttäjän GUI-istunnon sisällä ja säilyttää siten normaalin Keychain-pääsyn — sama `claude`-kirjautuminen toimii ilman erillistä API-avainta. Vaihtoehtoinen ratkaisu olisi `claude --bare` + `ANTHROPIC_API_KEY`-ympäristömuuttuja (ohittaa Keychainin kokonaan), mutta se vaatisi erillisen, laskutettavan API-avaimen olemassa olevan tilauksen sijaan — LaunchAgent on siis oletusvalinta jos haluat käyttää samaa kirjautumista jota käytät muutenkin.

**Asennus:**

1. Luo `~/Library/LaunchAgents/com.<sinä>.vegan-news-feed.daily.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.&lt;sinä&gt;.vegan-news-feed.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/&lt;käyttäjä&gt;/.claude/skills/vegan-news-feed/scripts/run_daily.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>13</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/&lt;käyttäjä&gt;/Library/Logs/vegan-news-feed.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/&lt;käyttäjä&gt;/Library/Logs/vegan-news-feed.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

2. Lataa se: `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.<sinä>.vegan-news-feed.daily.plist`
3. Poista se myöhemmin tarvittaessa: `launchctl bootout gui/$(id -u)/com.<sinä>.vegan-news-feed.daily`

`run_daily.sh` hoitaa loput puolestasi:

- Lukee `DISCORD_WEBHOOK_URL`:n omasta `0600`-oikeuksin suojatusta tiedostosta `~/.config/vegan-news/.env` — ei ajastustiedostosta eikä skriptiin kovakoodattuna.
- Osoittaa suoraan toimivaan Python 3.11 -asennukseen ja sen SSL-varmenteisiin PATH-haun sijaan (moni koneen muu `python3` ei toimi tämän skillin kanssa — ks. `PYTHON311`-muuttuja skriptissä), ja samoin suoraan `claude`-binaariin (`CLAUDE_BIN`-muuttuja) samasta syystä: ajastetun ajon suppea PATH ei sisällä sitä, vaikka interaktiivinen shell aina löytäisi sen.
- Kutsuu `claude -p`:tä oikeilla työkaluoikeuksilla: `--allowedTools "Bash,Read,Write,WebFetch,WebSearch"` (`Write` tarvitaan koosteen tallentamiseen, `WebFetch`/`WebSearch` vaiheen 1 varapolkuun ja vaiheen 3 lähteiden rikastamiseen).
- Jos ajo epäonnistuu millä tahansa vaiheella, lähettää lyhyen ⚠️-varoitusviestin samaan Discord-webhookiin, jotta epäonnistuminen ei jää huomaamatta hiljaisesti — ei vain lokiin jota kukaan ei lue.

Testaa `run_daily.sh` manuaalisesti terminaalissa ennen kuin ajastat sen (huom: se lähettää oikean koosteen Discordiin, koska se kutsuu koko putken) — ja testaa myös itse ajastusmekanismi kerran oikeasti lyhyellä, lähiajan `StartCalendarInterval`-arvolla ennen kuin luotat siihen päivittäin: kuten tämä koko osio osoittaa, interaktiivinen testi ei riitä paljastamaan ajastusympäristön omia ongelmia.

## Resurssit

- `scripts/fetch_feeds.py` — hakee ja suodattaa RSS-syötteet, ei ulkoisia riippuvuuksia (vain Python-standardikirjasto)
- `scripts/post_discord.py` — lähettää viestin webhookiin, pilkkoo pitkät viestit
- `scripts/history.py` — pitää kirjaa lähetetyistä uutisista JA sisältöideoista (`~/.config/vegan-news/sent_history.json`) cross-day-dedupointia varten; `show` lukee historian, `record` tallentaa päivän lähetykset (`--date` mahdollistaa jälkikäteisen tallennuksen/backfillin) ja siivoaa yli 30 vrk vanhat pois, `gaps` listaa päivät joilta puuttuu jokainen merkintä (ohitetut ajot). **Sama tiedosto ja scripti on myös `vegan-news-feed-review`-sisarskillin datalähde** — siksi vaiheessa 7 tallennetaan oikea sisältö (tiivistelmät, kulmat), ei vain otsikkoja.
- `scripts/run_daily.sh` — cron-wrapper: lukee webhookin `~/.config/vegan-news/.env`-tiedostosta, asettaa oikean Python-polun/SSL-varmenteet, ajaa `claude -p`:n ja hälyttää Discordiin jos ajo epäonnistuu
- `proposals/` — ei enää sisällä ehdotustiedostoja itse, vain opastekirjoitus (`README.md`) siitä että ne siirtyivät `~/.config/vegan-news/proposals/`-kansioon (ks. `DATA_LOCATIONS.md`) — ks. myös `../vegan-news-feed-review/SKILL.md`
- `references/feeds.md` — lähdelistaus; muokkaa/laajenna vapaasti
- `evals/evals.json` — testipromptit skillin toiminnan tarkistamiseen (ks. skill-creator-työnkulku)
- `PROCESS.md` — dokumentaatio siitä miten tämä skilli suunniteltiin ja miksi (intent → draft → testaus → iterointi); hyödyllinen jos näytät tämän projektin osana hakemusta tai portfoliota
- `DATA_LOCATIONS.md` — kartta kaikesta datasta joka elää `~/.config/vegan-news/`-kansiossa skillikansion ulkopuolella (webhook-secret, lähetyshistoria, ehdotukset) ja miksi

## Sisarskilli: vegan-news-feed-review

Erillinen skilli `vegan-news-feed-review` (rinnakkaisessa kansiossa `~/.claude/skills/vegan-news-feed-review/`) lukee tämän skillin lähetyshistoriaa viikoittain ja ehdottaa parannuksia (esim. lähteiden lisäys/poisto, relevanssikriteerien hionta) — mutta EI KOSKAAN muokkaa tämän skillin tiedostoja itse. Se kirjoittaa ehdotukset `~/.config/vegan-news/proposals/`-kansioon (ei tämän skillin sisälle — ks. `DATA_LOCATIONS.md` miksi), ja ihminen hyväksyy/soveltaa ne erikseen. Ks. sen oma SKILL.md ja `PROCESS.md`:n iteraatio 4 -osio.
