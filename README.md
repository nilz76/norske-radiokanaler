# Norske radiokanaler — strømme-URL-er

Vedlikeholdt liste over direktestrømmer for norske radiokanaler, klar til bruk i
VLC, Kodi, mpv, Sonos, bilstereo og andre spillere.

**34 kanaler, 122 strøm-URL-er — alle verifisert 2026-08-10.**

## Kom i gang

Åpne en av spillelistene i [playlists/](playlists/) direkte i spilleren din:

| Spilleliste | Innhold |
| ----------- | ------- |
| [alle-kanaler.m3u](playlists/alle-kanaler.m3u) | Alt — 34 kanaler |
| [nrk.m3u](playlists/nrk.m3u) | NRK riksdekkende — 13 kanaler |
| [nrk-distrikt.m3u](playlists/nrk-distrikt.m3u) | NRK P1 distriktssendinger — 15 kanaler |
| [kommersielle.m3u](playlists/kommersielle.m3u) | Kommersielle kanaler — 6 kanaler |

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

### NRK — riksdekkende

| Nr. | Kanal | Nr. | Kanal |
| --: | ----- | --: | ----- |
| 1 | NRK P1 | 8 | NRK Radio Super |
| 2 | NRK P1+ | 9 | NRK Klassisk |
| 3 | NRK P2 | 10 | NRK Sápmi |
| 4 | NRK P3 | 11 | NRK Jazz |
| 5 | NRK P3 Musikk | 12 | NRK Folkemusikk |
| 6 | NRK mP3 | 13 | NRK Sport |
| 7 | NRK Alltid Nyheter | | |

### NRK P1 — distrikt

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

### Kommersielle

| Nr. | Kanal | Kringkaster |
| --: | ----- | ----------- |
| 50 | Radio Norge | Bauer Media |
| 51 | Radio Rock | Bauer Media |
| 52 | Kiss | Bauer Media |
| 53 | Radio 1 | Bauer Media |
| 54 | Norsk Pop | Bauer Media |
| 55 | Radio Vinyl | Bauer Media |

P4-gruppen (P4, P5 Hits, P6 Rock, P7 Klem, P8 Pop, P9 Retro, P10 Country,
P11 Bandit) mangler foreløpig — spilleren deres på [radio.no](https://radio.no/)
henter strømmene via Radioplayer-API i nettleseren, så URL-ene lot seg ikke
utlede pålitelig. Bidrag ønskes, se [CONTRIBUTING.md](CONTRIBUTING.md).

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
kringkasteren endrer noe.

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
2. **Er det en kommersiell kanal?** Åpne `source`-URL-en for kanalen og finn
   strømmen på nytt. De ligger typisk på et Icecast-endepunkt (`_mp3`, `_aac`)
   som er lett å gjette når mønsteret for søsterkanalene er kjent.
3. **Er kanalen lagt ned?** Fjern den fra `stations.json`, men behold
   `id`-nummeret ubrukt så nummereringen til andre kanaler ikke forskyver seg.
4. Bygg spillelistene på nytt og oppdater statusrapporten:
   `python3 scripts/build_playlists.py && python3 scripts/check_streams.py --report`

## Vilkår for bruk

NRK skriver på [lyd.nrk.no](https://lyd.nrk.no/):

> Livestrømmer og kanaler fra NRK Radio er utviklet for privat bruk, og enhver
> annen bruk av disse for å skape nye tjenester, uten godkjenning av NRK, er
> derfor ikke tillatt.

Denne lista er ment for privat lytting i egen spiller. Skal du bygge en tjeneste
oppå strømmene, ta kontakt med kringkasteren først. Tilsvarende vilkår gjelder
sannsynligvis for de kommersielle kanalene.

Repoet inneholder bare offentlig publiserte URL-er og ingen lyd. Lisensen under
gjelder lista og skriptene, ikke innholdet strømmene sender.

## Lisens

[CC0 1.0](LICENSE) — fritt til all bruk.
