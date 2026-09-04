# Example output

This is a real digest the skill produced and sent to Discord — captured verbatim, not written as a mockup. Sent 2026-09-04, the skill's first full end-to-end run: 7 articles from 7 journals, sourced entirely via PubMed (the WebSearch fallback for the agriculture/environment/policy gap was checked but turned up nothing meeting the peer-reviewed bar that day — see the note at the end). At ~4,800 characters it went out as 3 separate Discord messages, same automatic splitting `post_discord.py` also gives `vegan-news-feed`.

Note the deliberate honesty in items 1 and 5: a randomized controlled trial showing a vegan diet *reduced* muscle mass in older adults without resistance training, and an observational study showing vegan children were shorter with lower growth markers than their peers — both included with real caveats about what the data does and doesn't show, rather than filtered out for being inconvenient. That's the "review articles and honest limitations, not just favorable findings" principle from `SKILL.md` working as designed, not cherry-picked for this example.

---

```
📚 **Kirjallisuuskooste – 04.09.2026**

**1. Itse valittu vegaaninen ruokavalio vähensi lihasmassaa terveillä ikääntyneillä**
_Alkuperäistutkimus, satunnaistettu koeasetelma (n=72, 65+ v.)_ — 12 viikon RCT vertasi itse valittua vegaanista ruokavaliota kaikkiruokaiseen ja vegaaniseen ruokavalioon yhdistettynä voimaharjoitteluun. Pelkkä vegaaninen ruokavalio ilman voimaharjoittelua heikensi lihasmassaa kaikkiruokaiseen ryhmään verrattuna. Varaus: korostaa proteiininsaannin suunnittelun ja voimaharjoittelun merkitystä ikääntyneillä vegaaneilla, ei osoita vegaanista ruokavaliota yleisesti haitalliseksi.
📖 *The American Journal of Clinical Nutrition*, syyskuu 2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42680254/

**2. Katsaus: kasvipohjaiset ruokavaliot ja aineenvaihduntaoireyhtymän riski lapsilla ja nuorilla**
_Katsausartikkeli_ — Kokoaa tuoreen tutkimusnäytön kasvipohjaisten ja kestävyyspainotteisten ruokavaliomallien yhteydestä aineenvaihduntaoireyhtymän riskiin lapsuudessa ja nuoruudessa, ja tarkastelee kestävyysindeksejä terveys- ja ympäristövaikutusten yhteismittarina.
📖 *Current Nutrition Reports*, 3.9.2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42690566/

**3. Kipu kalojen kokemana: mitä tiedämme ja mitä pitäisi vielä selvittää**
_Katsaus_ — Kokoaa yli 20 vuoden tutkimusnäytön siitä, että kaloilla on kipua välittäviä hermosto- ja käyttäytymisvasteita, jotka muistuttavat nisäkkäiden vastaavia — ensimmäiset nosiseptorit tunnistettiin kirjolohella jo 2002.
📖 *Laboratory Animals*, 31.8.2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42670273/

**4. Katsaus: naudanlihantuotannon metaanipäästöt ja niiden vähentämiskeinot**
_Katsaus_ — Kokoaa nykytiedon naudanlihakarjan suoliston metaanipäästöistä sekä arvioi mittausmenetelmiä ja hallintakeinoja (ruokinnan muutokset, rehun lisäaineet, rokotukset, laiduntamisstrategiat, mikrobimanipulaatio) päästöjen vähentämiseksi.
📖 *Veterinary and Animal Science*, syyskuu 2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42668471/

**5. Kasvuparametrit ja IGF-1-merkkiaineet eroavat sekasyöjä-, kasvissyöjä- ja vegaanilapsilla**
_Alkuperäistutkimus (n=2508 osallistujaa, 7344 näytettä)_ — Laaja saksalaistutkimus vertaili pituutta, painoindeksiä ja kasvuun liittyviä IGF-1/IGFBP-3-veriarvoja 3kk–19-vuotiailla. Vegaanilapset olivat lyhyempiä ja BMI matalampi kuin kasvissyöjä- tai sekasyöjälapsilla, ja IGF-1/IGFBP-3-arvot matalampia. Varaus: poikkileikkaustutkimus (ei RCT) — ei osoita syy-seuraussuhdetta eikä sitä että erot tarkoittaisivat huonompaa terveyttä, vaan nostaa esiin ruokavalion koostumuksen mahdollisen merkityksen kasvulle.
📖 *European Journal of Nutrition*, 29.8.2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42667434/

**6. Kananmunantuotannon emolinnut kuljetuksen aikana: fysiologiset ja käyttäytymisvasteet**
_Alkuperäistutkimus_ — Ensimmäinen tutkimus joka selvitti käytöstä poistettavien kananmunantuotannon emolintujen (kolme kantaa: Sakura, Lohmann Julia, Hy-Line Brown) fysiologisia ja käyttäytymisvasteita kaupallisen kuljetusprosessin aikana.
📖 *Journal of Veterinary Medical Science*, 1.9.2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42402411/

**7. Katsaus: yleisimmät kasvipohjaiset ravintolisät – annostelu, muodot ja turvallisuus**
_Katsaus (käytännön opas)_ — Antaa käytännön ohjeita ravintolisien laadun, pakkausmerkintöjen ja ainesosien arviointiin erityisesti kasvipohjaisten tuotteiden osalta; nostaa esiin kreatiinin, kofeiinin ja beeta-alaniinin esimerkkeinä muotoilu-, annostelu- ja turvallisuuseroista sekä mahdollisista ei-vegaanisista ainesosista.
📖 *American Journal of Lifestyle Medicine*, 31.8.2026
🔗 https://pubmed.ncbi.nlm.nih.gov/42682728/

💡 **Julkaisukulmat**
- **Rehellinen viestintä vegaanisesta ravitsemuksesta**: Kaksi tämän viikon tutkimusta (lihasmassa-RCT ja lasten kasvututkimus) osoittaa että vegaaninen ruokavalio vaatii tietoista suunnittelua sekä ikääntyneillä että lapsilla. Näiden esiin nostaminen rehellisesti, ratkaisukeskeisesti (riittävä proteiini, voimaharjoittelu, energiansaanti) rakentaa enemmän uskottavuutta kuin pelkkien hyötyjen korostaminen. _Molemmat tutkimukset julkaistiin juuri tällä viikolla, tarjoten ajankohtaisen ja konkreettisen pohjan asiantuntijakommentille._
- **Kalojen kipuherkkyys**: "Tiesitkö, että kalat tuntevat kipua samalla tavalla kuin nisäkkäät?" -tyyppinen valistuskulma, joka laajentaisi eläinoikeuskeskustelua myös kalatalouteen — aihe joka jää usein keskustelun ulkopuolelle. _Tuore katsaus kokoaa yli 20 vuoden tutkimusnäytön yksiin kansiin, hyvä ajankohta nostaa aihe esiin._

_7 artikkelia tästä koosteesta, lähteinä 7 eri julkaisua._
```

---

**On the WebSearch fallback finding nothing this run:** `SKILL.md` step 1 asks for a few targeted `WebSearch` queries to cover the agriculture/environment/policy gap PubMed doesn't serve well. Two were run for this digest (animal-agriculture environmental impact, farm-welfare policy research) — both returned mostly older background material (2021-2024 studies, general advocacy reports) rather than anything freshly published and clearly peer-reviewed. Per the skill's own rule, nothing from that search was forced into the digest just to have something from that category — the PubMed haul alone was strong enough to fill it honestly.

**A real bug found while producing this run:** `history.py`'s `--history-file` flag is a global option, not specific to the `record`/`show` subcommands — it has to come *before* `record`/`show` on the command line, not after. `SKILL.md` had it in the wrong order in two places (copied from a mental model of the flag rather than tested against the actual `argparse` structure). Found by running the real command and hitting `unrecognized arguments`, fixed, and verified — see `PROCESS.md`.
