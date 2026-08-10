# Bidra

## Legge til en kanal

1. Legg inn en ny oppføring i `stations.json`. Bruk et ledig `id`-nummer i riktig
   blokk — 1–19 NRK riksdekkende, 20–49 NRK distrikt, 50+ kommersielle.
2. Fyll ut `name`, `broadcaster`, `region`, `homepage` og `source`. `source` skal
   peke på siden URL-en er hentet fra, slik at den kan hentes på nytt senere.
3. Legg inn URL-ene under `streams`. Gyldige nøkler er `mp3_high`, `mp3_low`,
   `aac_high` og `aac_low`. Ta med bare de som faktisk finnes.
4. Verifiser og bygg:

   ```sh
   python3 scripts/check_streams.py
   python3 scripts/build_playlists.py
   ```

5. Send pull request med både `stations.json` og de genererte spillelistene.

Ikke rediger `.m3u`-filene eller `STATUS.md` for hånd — de er generert.

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

P4-gruppen: P4, P5 Hits, P6 Rock, P7 Klem, P8 Pop, P9 Retro, P10 Country,
P11 Bandit. Spilleren på [radio.no](https://radio.no/) laster strømmene via
Radioplayer-API i nettleseren, så URL-ene står ikke i HTML-en. Finner du dem —
for eksempel i nettverksfanen i utviklerverktøyene mens en kanal spiller — er de
velkomne her.

Ellers ønskes lokalradio (Radio Metro, Jærradioen, nærradioer) og eventuelle
NRK-kanaler som ikke er med.
