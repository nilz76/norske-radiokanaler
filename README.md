# Norske radiokanaler — strømme-URL-er

[![Sjekk strømmer](https://github.com/nilz76/norske-radiokanaler/actions/workflows/check-streams.yml/badge.svg)](https://github.com/nilz76/norske-radiokanaler/actions/workflows/check-streams.yml)

Vedlikeholdt liste over direktestrømmer for norske radiokanaler, klar til bruk i
VLC, Kodi, mpv, Sonos, bilstereo og andre spillere.

**105 kanaler, 271 strøm-URL-er — alle verifisert 2026-08-10.**

## Kom i gang

Åpne en av spillelistene i [playlists/](playlists/) direkte i spilleren din:

| Spilleliste | Innhold |
| ----------- | ------- |
| [alle-kanaler.m3u](playlists/alle-kanaler.m3u) | Alt — 105 kanaler |
| [nrk.m3u](playlists/nrk.m3u) | NRK riksdekkende — 13 kanaler |
| [nrk-distrikt.m3u](playlists/nrk-distrikt.m3u) | NRK P1 distriktssendinger — 15 kanaler |
| [kommersielle.m3u](playlists/kommersielle.m3u) | Riksdekkende kommersielle — 31 kanaler |
| [lokalradio.m3u](playlists/lokalradio.m3u) | Lokalradio — 46 kanaler |

I VLC: **Fil → Åpne nettverksstrøm** og lim inn en URL, eller **Fil → Åpne fil**
og velg en `.m3u`-fil for å laste inn hele lista.

Fra kommandolinja:

```sh
vlc playlists/nrk.m3u
mpv https://lyd.nrk.no/icecast/mp3/high/s0w7hwn47m/p1
```

## I bil — Tesla MCU2 og andre nettleserbaserte skjermer

MCU2 kan ikke åpne `.m3u`-filer: nettleseren laster dem ned istedenfor å spille
dem, og USB-inngangen spiller bare lokale filer, ikke strømmer. Veien inn er
nettleseren, og [docs/index.html](docs/index.html) er en side laget for det —
store trykkflater, søkefelt og ett `<audio>`-element som bytter kilde.

**Spilleren ligger på <https://nilz76.github.io/norske-radiokanaler/>.** Åpne den
i bilens nettleser og legg den inn som bokmerke, så er den ett trykk unna.

(Den serveres av GitHub Pages fra `/docs` på `main`.)

Siden tar hensyn til to begrensninger i den nettleseren:

- **Bare https-strømmer.** Pages går over https, og Chromium blokkerer
  http-strømmer på en https-side som usikkert innhold. 7 kanaler er derfor
  utelatt, og listet nederst på siden med begrunnelse — 98 av 105 er med.
- **MP3 framfor AAC.** AAC i Icecast (`audio/aacp`) spilles ikke pålitelig i
  MCU2, så MP3 velges når kanalen har det. AAC brukes bare der det er eneste
  alternativ.

Siden bygges automatisk av den ukentlige arbeidsflyten, så bilsiden følger
endringer i strøm-URL-ene av seg selv. Etter en manuell endring i
`stations.json` bygger du den slik:

```sh
python3 scripts/build_webplayer.py
```

Vær oppmerksom på at nettleserlyd i MCU2 ikke styres av rattknappene, og at
bilens medieapp ikke viser kanalnavnet. Vil du ha rattstyring og bedre
integrasjon, er Bluetooth fra telefonen fortsatt det som fungerer best; da kan du
bruke `.m3u`-filene i en vanlig spiller på telefonen.

## Kanaloversikt

Hver kanal har et fast nummer som brukes som `tvg-chno` i spillelistene, slik at
kanalrekkefølgen holder seg stabil i spillere som sorterer på kanalnummer.
Nummerblokkene er 1–19 NRK riksdekkende, 20–49 NRK distrikt, 50–99 riksdekkende
kommersielle, 100+ lokalradio.

### NRK — riksdekkende (13)

| Nr. | Kanal | Nr. | Kanal |
| --: | ----- | --: | ----- |
| 1 | NRK P1 | 8 | NRK Radio Super |
| 2 | NRK P1+ | 9 | NRK Klassisk |
| 3 | NRK P2 | 10 | NRK Sápmi |
| 4 | NRK P3 | 11 | NRK Jazz |
| 5 | NRK P3 Musikk | 12 | NRK Folkemusikk |
| 6 | NRK mP3 | 13 | NRK Sport |
| 7 | NRK Alltid Nyheter | | |

### NRK P1 — distrikt (15)

NRK sine distriktsnavn følger ikke fylkesinndelingen. Der de er forskjellige,
står fylket i parentes i spillelistene.

| Nr. | NRK-distrikt | Fylke | Nr. | NRK-distrikt | Fylke |
| --: | ------------ | ----- | --: | ------------ | ----- |
| 20 | Buskerud | Buskerud | 28 | Sogn og Fjordane | Vestland |
| 21 | Finnmark | Finnmark | 29 | Sørlandet | Agder |
| 22 | Hordaland | Vestland | 30 | Telemark | Telemark |
| 23 | Innlandet | Innlandet | 31 | Troms | Troms |
| 24 | Møre og Romsdal | Møre og Romsdal | 32 | Trøndelag | Trøndelag |
| 25 | Nordland | Nordland | 33 | Vestfold | Vestfold |
| 26 | Stor-Oslo | Oslo | 34 | Østfold | Østfold |
| 27 | Rogaland | Rogaland | | | |

Stor-Oslo (26) og riksdekkende NRK P1 (1) deler samme strøm — NRK bruker
Oslo-sendingen som standard P1-kanal. Stor-Oslo dekker også Akershus, som derfor
ikke har en egen distriktskanal.

### Bauer Media (10)

| Nr. | Kanal | Nr. | Kanal |
| --: | ----- | --: | ----- |
| 50 | Radio Norge | 55 | Radio Vinyl |
| 51 | Radio Rock | 56 | Topp 40 |
| 52 | Kiss | 57 | P24-7 Mix |
| 53 | Radio 1 | 58 | P24-7 Kos |
| 54 | Norsk Pop | 59 | P24-7 Juleradioen |

### P4-gruppen (10)

| Nr. | Kanal | Nr. | Kanal |
| --: | ----- | --: | ----- |
| 60 | P4 | 65 | P8 Pop |
| 61 | P5 Hits | 66 | P9 Retro |
| 62 | P5 Nonstop Hits | 67 | P10 Country |
| 63 | P6 Rock | 68 | P11 Dance |
| 64 | P7 Klem | 69 | P12 Hitmix |

### Andre riksdekkende og nisjekanaler (11)

| Nr. | Kanal | Nr. | Kanal |
| --: | ----- | --: | ----- |
| 80 | P7 Kristen Riksradio | 85 | Radio Latin-Amerika |
| 81 | P7 Pop | 86 | historyradio.org |
| 82 | Radio 3.16 | 87 | Radio Northern Star |
| 83 | Norsk Country Radio | 90 | Radio Rox (DinLyd) |
| 84 | Metal Express Radio | 91 | The Beat (DinLyd) |
| | | 92 | Heart Radio (DinLyd) |

### Lokalradio (46)

Sortert på fylke, som er rekkefølgen i [lokalradio.m3u](playlists/lokalradio.m3u).
Området er kanalens eget dekningsområde der det er smalere enn fylket.

| Nr. | Kanal | Fylke | Område |
| --: | ----- | ----- | ------ |
| 166 | Radio Lyngdal | Agder | Lyngdal |
| 112 | Sørlandsradioen | Agder | Sørlandet |
| 148 | Guovdageainnu Lagasradio | Finnmark | Kautokeino |
| 144 | Radio Nordkapp | Finnmark | Nordkapp |
| 120 | ElverumsRadioen | Innlandet | Elverum |
| 121 | GudbrandsdalsRadioen | Innlandet | Gudbrandsdalen |
| 122 | HamarRadioen | Innlandet | Hamar |
| 123 | RadioKongsvinger | Innlandet | Kongsvinger |
| 160 | Radio Randsfjord | Innlandet | Randsfjord |
| 129 | Radio Sentrum | Innlandet | |
| 125 | SolørRadioen | Innlandet | Solør |
| 126 | SolørRadioen+ | Innlandet | Solør |
| 128 | Totenradioen | Innlandet | Toten |
| 127 | TrysilRadioen | Innlandet | Trysil |
| 107 | Valdres Radio | Innlandet | Valdres |
| 124 | ØsterdalsRadioen | Innlandet | Østerdalen |
| 182 | 1FM Jazz | Møre og Romsdal | Molde |
| 100 | Hjalarhornet | Møre og Romsdal | Volda og Ørsta |
| 102 | Ordentlig Radio | Møre og Romsdal | Ålesund |
| 105 | Radio Kos | Møre og Romsdal | Sunnmøre |
| 110 | Radio Sunnmøre | Møre og Romsdal | Sunnmøre |
| 181 | Radio Ålesund | Møre og Romsdal | Ålesund |
| 146 | FM 8000 Bodø | Nordland | Bodø |
| 140 | Radio 3 Bodø | Nordland | Bodø |
| 145 | Radio Meløy | Nordland | Meløy |
| 147 | Radio Værøy | Nordland | Værøy |
| 164 | Radio Nova | Oslo | |
| 163 | radiOrakel | Oslo | |
| 104 | Radio 102 | Rogaland | Haugesund |
| 183 | Radio Haugaland | Rogaland | Haugesund |
| 186 | Radio Bø | Telemark | Bø i Midt-Telemark |
| 141 | Radio Bardufoss | Troms | Bardufoss |
| 142 | Radio Tromsø | Troms | Tromsø |
| 143 | Radio Tromsø Hits | Troms | Tromsø |
| 185 | Nea Radio | Trøndelag | Selbu og Tydal |
| 103 | P5 Fosen | Trøndelag | Fosen |
| 184 | Radio Trøndelag | Trøndelag | |
| 165 | Radio Tønsberg | Vestfold | Tønsberg |
| 101 | Nordfjord Nærradio | Vestland | Nordfjord |
| 111 | Radio Folgefonn | Vestland | Hardanger |
| 109 | Radio Luster | Vestland | Luster |
| 108 | RadiOs | Vestland | Os og Bjørnafjorden |
| 180 | Radio Sotra | Vestland | Sotra |
| 106 | Radio Stryn | Vestland | Stryn |
| 162 | Radio Skjeberg | Østfold | Sarpsborg |
| 161 | Radio Øst | Østfold | |

## Struktur

```
stations.json          Kilden til sannhet — alle kanaler og URL-er
playlists/*.m3u        Generert av scripts/build_playlists.py
docs/index.html        Nettleserspiller, generert av scripts/build_webplayer.py
STATUS.md              Generert av scripts/check_streams.py --report
schema/                JSON Schema for stations.json
scripts/               Vedlikeholdsverktøy (Python 3.9+, ingen avhengigheter)
```

Hver kanal i `stations.json` ser slik ut:

```json
{
  "id": 22,
  "name": "NRK P1 Hordaland",
  "broadcaster": "NRK",
  "region": "Vestland",
  "district": "Hordaland",
  "homepage": "https://www.nrk.no/hordaland/",
  "source": "https://lyd.nrk.no/",
  "streams": {
    "mp3_high": "https://lyd.nrk.no/icecast/mp3/high/s0w7hwn47m/p1_dk8",
    "mp3_low": "https://lyd.nrk.no/icecast/mp3/low/s0w7hwn47m/p1_dk8",
    "aac_high": "https://lyd.nrk.no/icecast/aac/high/s0w7hwn47m/p1_dk8",
    "aac_low": "https://lyd.nrk.no/icecast/aac/low/s0w7hwn47m/p1_dk8"
  }
}
```

| Felt | Betydning |
| ---- | --------- |
| `region` | `Riksdekkende` eller ett av de 15 fylkene — ingen andre verdier |
| `area` | Kanalens eget dekningsområde når det er smalere enn fylket, f.eks. `Volda og Ørsta` |
| `district` | Bare NRK: distriktsnavnet NRK selv bruker. `refresh_nrk.py` slår opp kanal-slugen på dette |
| `source` | Siden URL-en er hentet fra, slik at den kan hentes på nytt når kringkasteren endrer noe |
| `streams` | Alle fire kvaliteter er valgfrie — mange lokalradioer tilbyr bare én |

`region` og `district` er atskilt fordi NRK sine distrikter ikke er fylker:
Hordaland og Sogn og Fjordane ligger begge i Vestland, og Sørlandet er Agder.
Ett fylke kan altså ha flere distriktskanaler, og `refresh_nrk.py` ville ikke
klart å skille dem hvis oppslaget gikk på fylket.

### Navnene i spillelistene

`name` i `stations.json` er det rene kanalnavnet. Spillelistene legger på fylket
for regionale kanaler, slik at de er lette å skille i VLC og andre spillere:

```
103. P5 Fosen (Trøndelag)
22. NRK P1 Hordaland (Vestland)
20. NRK P1 Buskerud
60. P4
```

Fylket utelates når det alt står i navnet — derfor ingen «NRK P1 Buskerud
(Buskerud)» — og riksdekkende kanaler får aldri noe tillegg. Regelen ligger i
`display_name()` i [scripts/common.py](scripts/common.py); rediger den der
framfor å skrive fylket inn i `name`.

## Vedlikehold

Alle skriptene bruker bare Python-standardbiblioteket.

```sh
# Sjekk at alle strømmene svarer (avslutningskode 1 hvis noe er dødt)
python3 scripts/check_streams.py

# Samme, men oppdater også STATUS.md
python3 scripts/check_streams.py --report

# Bare NRK, bare feil
python3 scripts/check_streams.py --only NRK --quiet

# Hent NRK-URL-ene på nytt fra lyd.nrk.no og sammenlikn med stations.json
python3 scripts/refresh_nrk.py            # tørrkjøring
python3 scripts/refresh_nrk.py --write    # lagre endringene

# Spør Icecast-vertene om hvilke kanaler de sender, og vis det som mangler
python3 scripts/discover_icecast.py --new
python3 scripts/discover_icecast.py lyd3.lokalradio.no

# Bygg spillelistene på nytt etter endringer i stations.json
python3 scripts/build_playlists.py
python3 scripts/build_playlists.py --quality aac_high

# Bygg nettleserspilleren i docs/ på nytt
python3 scripts/build_webplayer.py
```

`check_streams.py` åpner hver strøm, leser de første par kilobytene og godtar den
bare når serveren svarer 200/206 med en lyd-content-type.

### Automatikken

[.github/workflows/check-streams.yml](.github/workflows/check-streams.yml) kjører
hver mandag, og gjør dette i rekkefølge:

1. Sjekker alle strøm-URL-ene.
2. Er noe dødt, kjøres `refresh_nrk.py --write` — det reparerer de vanligste
   feilene av seg selv, siden NRK bytter token og flytter distriktskanaler.
3. Bygger `playlists/`, `docs/index.html` og `STATUS.md` på nytt.
4. Committer og pusher hvis noe faktisk endret seg. Bilsiden på GitHub Pages
   oppdaterer seg dermed selv når en URL endres.
5. Sjekker på nytt, og oppretter en issue bare for strømmer som fortsatt er
   døde. Er en issue åpen fra før, kommenteres den i stedet for at det lages en
   ny hver uke.

Push og pull request kjører aldri skrivestegene. Der er jobben å fange at noen
har endret `stations.json` uten å bygge de genererte filene — da feiler den med
beskjed om hvilke skript som må kjøres.

Pushen skjer med `GITHUB_TOKEN`, som med vilje ikke utløser nye arbeidsflyter, så
automatikken kan ikke gå i løkke.

### Når en strøm slutter å virke

1. **Er det NRK?** Kjør `python3 scripts/refresh_nrk.py`. NRK bytter av og til
   `token`-delen av URL-en (`.../icecast/mp3/high/<token>/p1`) og flytter
   distriktskanaler mellom `p1_dkN`-numre. Skriptet leser
   [lyd.nrk.no](https://lyd.nrk.no/) på nytt, viser hva som har endret seg, og
   skriver det inn med `--write`.
2. **Ligger kanalen på Icecast?** Kjør
   `python3 scripts/discover_icecast.py <vert>`. Icecast lister alle mount-punkter
   med navn på `/status-json.xsl`, så et mount som er omdøpt dukker opp der.
3. **Ellers:** åpne `source`-URL-en for kanalen og finn strømmen på nytt.
4. **Er kanalen lagt ned?** Fjern den fra `stations.json`, men behold
   `id`-nummeret ubrukt så nummereringen til andre kanaler ikke forskyver seg.
5. Bygg spillelistene på nytt og oppdater statusrapporten:
   `python3 scripts/build_playlists.py && python3 scripts/check_streams.py --report`

## Hvordan lista er satt sammen

- **NRK** — hentet fra [lyd.nrk.no](https://lyd.nrk.no/), som er NRK sin egen
  oversikt over direktestrømmene. `refresh_nrk.py` leser den siden.
- **P4-gruppen** — Icecast-verter på `p<n>.p4groupaudio.com` med mount-mønsteret
  `P<nn>_<M|A><H|M>`, der M/A er mp3/aac og H/M er høy/middels bitrate.
- **Bauer Media** — én Icecast-vert, `live-bauerno.sharp-stream.com`, med
  mønsteret `<kanal>_no_<mp3|aac>`.
- **Lokalradio** — funnet ved å spørre Icecast-vertene om mount-listene sine
  (`scripts/discover_icecast.py`). De store fellesvertene er
  `lyd1`/`lyd2.lokalradio.no`, `lyd.radioene.no`, `stream.bardufoss.no` og
  `stream.radiorandsfjord.no`.
- Startpunktet for verts-søket var den åpne stasjonsdatabasen
  [radio-browser.info](https://www.radio-browser.info/). Ingen URL er tatt inn
  derfra uten at `check_streams.py` har bekreftet at den svarer med lyd.

Kanaler som mangler, og hvorfor, står i [CONTRIBUTING.md](CONTRIBUTING.md).

## Vilkår for bruk

NRK skriver på [lyd.nrk.no](https://lyd.nrk.no/):

> Livestrømmer og kanaler fra NRK Radio er utviklet for privat bruk, og enhver
> annen bruk av disse for å skape nye tjenester, uten godkjenning av NRK, er
> derfor ikke tillatt.

Denne lista er ment for privat lytting i egen spiller. Skal du bygge en tjeneste
oppå strømmene, ta kontakt med kringkasteren først. Tilsvarende vilkår gjelder
sannsynligvis for de andre kringkasterne.

Repoet inneholder bare offentlig publiserte URL-er og ingen lyd. Lisensen under
gjelder lista og skriptene, ikke innholdet strømmene sender.

## Lisens

[CC0 1.0](LICENSE) — fritt til all bruk.
