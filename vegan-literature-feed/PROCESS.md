# Design history: vegan-literature-feed

## 1. Capture intent

Käyttäjä halusi laajentaa `vegan-news-feed`-mediaseurantaa myös tieteelliseen kirjallisuuteen (veganismi, kasvipohjainen ravitsemus, eläinten kognitio/tuntoisuus, eläintuotannon ympäristövaikutus, eläinoikeuspolitiikka) — tavoitteena antaa viestintätiimille mahdollisuus julkaista kiinnostavasta tutkimuslöydöksestä ennen valtamediaa. Käyttäjä ehdotti itse että tämä kuulostaisi omalta erilliseltä skilliltä, mahdollisesti eri Discord-webhookilla myöhemmin mutta samalla webhookilla aluksi testausmielessä.

## 2. Suunnittelukeskustelu ja päätökset

Ennen rakentamista käytiin läpi kolme keskeistä valintaa (ks. keskustelu, `AskUserQuestion`):

- **Aihepiirin laajuus**: käyttäjä valitsi laajimman vaihtoehdon — ravitsemus/terveys, eläinkognitio/-tuntoisuus, JA eläintuotannon ympäristövaikutus/politiikkatutkimus. Tämä tarkoittaa ettei yksi tietolähde (esim. pelkkä PubMed) riitä kattamaan koko alaa, ks. kohta 3.
- **Preprintit**: käyttäjä valitsi "vain vertaisarvioitu, ei preprinttejä toistaiseksi" — nopeampi kattavuus bioRxiv/medRxiv:n kautta olisi ollut mahdollista, mutta riski että viestintätiimi julkaisisi jotain mikä myöhemmin kaatuu vertaisarvioinnissa painoi enemmän.
- **Ajastustiheys**: käyttäjä ei valinnut kumpaakaan tarjotuista vaihtoehdoista (viikoittain suositeltuna, tai päivittäin kuten `vegan-news-feed`) vaan ehdotti kolmatta: aloita päivittäisellä testauksella, ja jos osoittautuu liian tiheäksi (paljon tyhjiä päiviä), löysennä myöhemmin viikoittaiseksi. **Tämä on kuitenkin tässä vaiheessa hypoteettinen** — ajastusta itsessään (LaunchAgent/cron-wrapperia) ei rakennettu tässä iteraatiossa lainkaan, ks. kohta 4 ja `TODO.md`.

Käyttäjä täsmensi vielä erikseen (ennen rakentamisen aloitusta): katsausartikkelit, meta-analyysit ja systemaattiset katsaukset pitää nimenomaisesti sisällyttää arvokkaana sisältönä, koska ne antavat laajemman kuvan tutkimusrintamasta — ei vain tuoreimpia yksittäisiä löydöksiä. Tämä ohjasi sekä `fetch_pubmed.py`:n suunnittelua (`pub_types`-kentän talteenotto PubMedin esummary-vastauksesta) että `SKILL.md`:n vaiheen 2/3 ohjeistusta (arvioi katsauksia niiden omalla mittapuulla, älä suodata pois "ei ole uusi löydös" -perusteella).

## 3. Sourcing-arkkitehtuuri: miksi PubMed + WebSearch, ei pelkkä RSS

Toisin kuin `vegan-news-feed`, jolla on puhdas RSS-pohjainen lähde jokaiselle relevantille julkaisijalle, tieteellisellä kirjallisuudella ei ole vastaavaa yhtenäistä, konedeutettavaa rajapintaa laajalla aihepiirillä:

- **PubMed E-utilities** (`scripts/fetch_pubmed.py`) kattaa hyvin ravitsemus-/terveys- ja eläinkognitiotutkimuksen — se on NLM:n biolääketieteellinen tietokanta, ilmainen, ei vaadi API-avainta, ja indeksoi VAIN vertaisarvioituja lehtiartikkeleita (ei preprinttejä) — tämä ratkaisee "vain vertaisarvioitu" -vaatimuksen automaattisesti PubMed-lähteisille kohteille.
- PubMed kattaa HEIKOSTI maatalous-/ympäristö-/politiikkatutkimuksen, koska se ei ole tarkoitettu sille alalle. Tätä varten `SKILL.md`:n vaihe 1 ohjeistaa kohdennettuja `WebSearch`-hakuja täydentämään aukkoa — mutta näiden tulokset VAATIVAT erillisen vertaisarviointitarkistuksen per kohde, koska WebSearch ei takaa lähteen laatua samalla tavalla kuin PubMed.
- Harkittiin myös kuratoitua lehti-RSS-listaa (`references/sources.md`, analoginen `feeds.md`:lle) kolmantena tasona — tämä olisi luotettavampi tapa kattaa ympäristö-/politiikka-aukko kuin ad hoc WebSearch, mutta **jätettiin tietoisesti tekemättä tässä minimiversiossa** (ks. `TODO.md`), koska sen kuratointi (oikeiden lehtien tunnistus ja RSS-URL:ien kokoaminen usealta eri tieteenalalta) on itsessään merkittävä työ, eikä käyttäjä tässä vaiheessa priorisoi tätä projektia.

`fetch_pubmed.py` testattiin oikeasti live-rajapintaa vasten ennen kuin sitä pidettiin valmiina (ei vain kirjoitettu ja oletettu toimivaksi): ensimmäinen ajo epäonnistui tutulla `X | None`-syntaksiongelmalla (järjestelmän `python3` liian vanha, sama kuin `vegan-news-feed`:ssä), sitten SSL-varmenneongelmalla (sama `SSL_CERT_FILE`/certifi-ratkaisu kuin `run_daily.sh`:ssa) — kummankin korjauksen jälkeen skripti palautti oikeaa, jäsenneltyä PubMed-dataa, mukaan lukien vahvistus että `pub_types`-kenttä tunnistaa katsausartikkelit oikein (`["Journal Article", "Review"]`). Kysely on tarkoituksella laaja ja tuottaa myös epäolennaisia osumia (esim. yleistä eläinlääketiedettä) — tämä on odotettua ja jätetty agentin vaiheen 2 harkinnan varaan, samalla periaatteella kuin `vegan-news-feed`:n raakadatakin sisältää karsittavia osumia.

## 4. Tietoinen minimiskooppi

Käyttäjä pyysi eksplisiittisesti: "Create the skill for now, but leave it to minimum, as I will prioritize other projects for now." Tämä tarkoitti konkreettisia rajauksia, kaikki dokumentoitu `TODO.md`:ssa eikä vain jätetty hiljaa tekemättä:

- Ei `run_daily.sh`/LaunchAgent-ajastusta — vaikka `vegan-news-feed`:n kolmen bugin (Python-syntaksi, SSL, cron→Keychain) korjaukset ovat jo tiedossa ja kopioitavissa suoraan kun ajastus joskus rakennetaan.
- Ei kuratoitua `references/sources.md`-lehtilistaa — nojataan pelkkään PubMed-kyselyyn + ad hoc WebSearchiin.
- `evals/evals.json` sisältää vain 4 perustason testiä (ei laajaa kattavuutta kuten `vegan-news-feed`:n 10).
- Ei koskaan ajettu päästä päähän oikeasti (ei lähetystä Discordiin asti) — vain `fetch_pubmed.py` on testattu erikseen live-rajapintaa vasten.
- Ei arvioitu kuuluuko tämä skilli `vegan-news-feed-review`:n katselmoinnin piiriin.

Tämä rajaus on tarkoituksellinen, ei laiskuutta: skilli on toiminnallinen (fetch-mekanismi todennettu oikeasti toimivaksi) mutta ei tuotantovalmis, ja seuraava, joku myöhempi istunto voi jatkaa suoraan `TODO.md`:n listalta ilman että täytyy rekonstruoida näitä päätöksiä keskusteluhistoriasta.
