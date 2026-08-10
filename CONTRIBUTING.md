# Bidra

## Legge til en kanal

1. Legg inn en ny oppføring i `stations.json`. Bruk et ledig `id`-nummer i riktig
   blokk — 1–19 NRK riksdekkende, 20–49 NRK distrikt, 50–99 riksdekkende
   kommersielle, 100+ lokalradio.
2. Fyll ut `name`, `broadcaster`, `region`, `homepage` og `source`. `source` skal
   peke på siden URL-en er hentet fra, slik at den kan hentes på nytt senere.
   - `region` skal være `Riksdekkende` eller ett av de 15 fylkene. Ikke bruk
     landsdeler eller gamle fylkesnavn — schema-en avviser dem.
   - Er dekningsområdet smalere enn fylket, sett det i `area` (`Volda og Ørsta`,
     `Sunnmøre`). Området er dokumentasjon; fylket er det som vises i spillerne.
   - `name` skal være det rene kanalnavnet. Ikke skriv fylket inn i navnet —
     spillelistene legger det på selv, se `display_name()` i `scripts/common.py`.
3. Legg inn URL-ene under `streams`. Gyldige nøkler er `mp3_high`, `mp3_low`,
   `aac_high` og `aac_low`. Ta med bare de som faktisk finnes.
4. Verifiser og bygg:

   ```sh
   python3 scripts/check_streams.py
   python3 scripts/build_playlists.py
   ```

5. Send pull request med både `stations.json` og de genererte spillelistene.

Ikke rediger `.m3u`-filene eller `STATUS.md` for hånd — de er generert.

## Finne nye kanaler

De fleste norske lokalradioene kjører Icecast, og Icecast lister alle
mount-punktene sine med navn på `/status-json.xsl`. Det gjør det raskt å gå fra én
kjent strøm til alle kanalene på samme vert:

```sh
python3 scripts/discover_icecast.py lyd3.lokalradio.no
python3 scripts/discover_icecast.py --new        # spør vertene lista alt bruker
```

Kvalitetsnavnene går igjen på fellesvertene: `_hq` er mp3, `_mq` er AAC rundt
128 kbit/s og `_lq` er AAC rundt 48 kbit/s. Men ikke alle kanaler har alle tre —
verifiser før du legger dem inn.

## Krav til URL-er

- Bare offentlig publiserte strøm-URL-er. Ikke URL-er som krever innlogging,
  abonnement eller omgåelse av geoblokkering.
- `https` når kringkasteren tilbyr det.
- Foretrekk kringkasterens egen dokumenterte URL framfor en CDN-URL den peker
  videre til. NRK sine `lyd.nrk.no`-URL-er redirigerer til
  `*.dna.contentdelivery.net`; det er `lyd.nrk.no`-varianten som skal ligge i
  lista, siden CDN-verten kan byttes ut.
- `check_streams.py` må gi OK for URL-en.

## Kanaler som mangler

**DinLyd (tidligere Radio Metro)** har rundt femten kanaler på
`live-nors.sharp-stream.com`, men mount-punktene heter `nors10` til `nors24` og
serveren oppgir verken `icy-name` eller beskrivelse. Tre er identifisert
(Radio Rox, The Beat, Heart Radio — id 90–92); resten er med i lista bare hvis
noen kan knytte mount-nummer til kanalnavn. Nettsidene på
[dinlyd.no](https://dinlyd.no/) laster spilleren via JavaScript, så URL-ene står
ikke i HTML-en. Enkleste vei: åpne en kanal på dinlyd.no, se i nettverksfanen i
utviklerverktøyene hvilket `nors`-mount som spilles, og meld inn paret.

Kanalene DinLyd omtaler på sine sider er Radio Metro, Radio Rox, The Beat,
Hitradio, Heart Radio, Metro Classic, Power Rock Radio og Dansbandradioen.

**Jærradiogruppen** har flere kanaler på `audio.jaerradiogruppen.no`, men verten
svarer ikke på `/status-json.xsl`, så bare Radio Tønsberg (165) er funnet så
langt.

Ellers ønskes lokalradioer som ikke er med, og eventuelle NRK-kanaler som mangler
— `refresh_nrk.py` varsler om nye kanal-sluger som dukker opp på lyd.nrk.no.
