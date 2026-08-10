# Norske radiokanaler — strømme-URL-er

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

| Nr. | Distrikt | Nr. | Distrikt |
| --: | -------- | --: | -------- |
| 20 | Buskerud | 28 | Sogn og Fjordane |
| 21 | Finnmark | 29 | Sørlandet |
| 22 | Hordaland | 30 | Telemark |
| 23 | Innlandet | 31 | Troms |
| 24 | Møre og Romsdal | 32 | Trøndelag |
| 25 | Nordland | 33 | Vestfold |
| 26 | Stor-Oslo | 34 | Østfold |
| 27 | Rogaland | | |

Stor-Oslo (26) og riksdekkende NRK P1 (1) deler samme strøm — NRK bruker
Oslo-sendingen som standard P1-kanal.

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

| Nr. | Kanal | Område | Nr. | Kanal | Område |
| --: | ----- | ------ | --: | ----- | ------ |
| 100 | Hjalarhornet | Volda og Ørsta | 140 | Radio 3 Bodø | Bodø |
| 101 | Nordfjord Nærradio | Nordfjord | 141 | Radio Bardufoss | Bardufoss |
| 102 | Ordentlig Radio | Ålesund | 142 | Radio Tromsø | Tromsø |
| 103 | P5 Fosen | Fosen | 143 | Radio Tromsø Hits | Tromsø |
| 104 | Radio 102 | Haugesund | 144 | Radio Nordkapp | Nordkapp |
| 105 | Radio Kos | Sunnmøre | 145 | Radio Meløy | Meløy |
| 106 | Radio Stryn | Stryn | 146 | FM 8000 Bodø | Bodø |
| 107 | Valdres Radio | Valdres | 147 | Radio Værøy | Værøy |
| 108 | RadiOs | Os og Bjørnafjorden | 148 | Guovdageainnu Lagasradio | Kautokeino |
| 109 | Radio Luster | Luster | 160 | Radio Randsfjord | Randsfjord |
| 110 | Radio Sunnmøre | Sunnmøre | 161 | Radio Øst | Østfold |
| 111 | Radio Folgefonn | Hardanger | 162 | Radio Skjeberg | Sarpsborg |
| 112 | Sørlandsradioen | Sørlandet | 163 | radiOrakel | Oslo |
| 120 | ElverumsRadioen | Elverum | 164 | Radio Nova | Oslo |
| 121 | GudbrandsdalsRadioen | Gudbrandsdalen | 165 | Radio Tønsberg | Tønsberg |
| 122 | HamarRadioen | Hamar | 166 | Radio Lyngdal | Lyngdal |
| 123 | RadioKongsvinger | Kongsvinger | 180 | Radio Sotra | Sotra |
| 124 | ØsterdalsRadioen | Østerdalen | 181 | Radio Ålesund | Ålesund |
| 125 | SolørRadioen | Solør | 182 | 1FM Jazz | Molde |
| 126 | SolørRadioen+ | Solør | 183 | Radio Haugaland | Haugesund |
| 127 | TrysilRadioen | Trysil | 184 | Radio Trøndelag | Trøndelag |
| 128 | Totenradioen | Toten | 185 | Nea Radio | Selbu og Tydal |
| 129 | Radio Sentrum | Innlandet | 186 | Radio Bø | Bø i Midt-Telemark |

## Struktur

```
stations.json          Kilden til sannhet — alle kanaler og URL-er
playlists/*.m3u        Generert av scripts/build_playlists.py
STATUS.md              Generert av scripts/check_streams.py --report
schema/                JSON Schema for stations.json
scripts/               Vedlikeholdsverktøy (Python 3.9+, ingen avhengigheter)
```

Hver kanal i `stations.json` ser slik ut:

```json
{
  "id": 4,
  "name": "NRK P3",
  "broadcaster": "NRK",
  "region": "Riksdekkende",
  "homepage": "https://radio.nrk.no/direkte/p3",
  "source": "https://lyd.nrk.no/",
  "streams": {
    "mp3_high": "https://lyd.nrk.no/icecast/mp3/high/s0w7hwn47m/p3",
    "mp3_low": "https://lyd.nrk.no/icecast/mp3/low/s0w7hwn47m/p3",
    "aac_high": "https://lyd.nrk.no/icecast/aac/high/s0w7hwn47m/p3",
    "aac_low": "https://lyd.nrk.no/icecast/aac/low/s0w7hwn47m/p3"
  }
}
```

`source` peker på siden URL-en er hentet fra, slik at den kan hentes på nytt når
kringkasteren endrer noe. Alle fire kvaliteter er valgfrie — mange lokalradioer
tilbyr bare én.

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
```

`check_streams.py` åpner hver strøm, leser de første par kilobytene og godtar den
bare når serveren svarer 200/206 med en lyd-content-type.

[.github/workflows/check-streams.yml](.github/workflows/check-streams.yml) kjører
sjekken hver mandag og oppretter en issue hvis noe har sluttet å virke.

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
