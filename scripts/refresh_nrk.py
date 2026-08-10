#!/usr/bin/env python3
"""Hent gjeldende NRK-strømmer fra lyd.nrk.no og oppdater stations.json.

NRK publiserer alle direktestrømmene sine på https://lyd.nrk.no/. URL-ene har
formen

    https://lyd.nrk.no/icecast/<mp3|aac>/<high|low>/<token>/<kanal>

der <token> av og til byttes ut. Dette skriptet leser siden på nytt, sammenlikner
med stations.json og oppdaterer URL-ene som har endret seg.

Bruk:
    python3 scripts/refresh_nrk.py            # vis hva som ville blitt endret
    python3 scripts/refresh_nrk.py --write    # skriv endringene til stations.json
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from html import unescape

from common import load_stations, save_stations

SOURCE_URL = "https://lyd.nrk.no/"
USER_AGENT = "radio-streamurls/1.0 (+https://github.com/)"

# Distriktsnavnene NRK bruker på lyd.nrk.no. Kanal-slugene (p1_dk2, p1_dk3, ...)
# står ikke i noen fast rekkefølge, så vi parer hvert navn med den nærmeste
# etterfølgende slugen i dokumentet.
DISTRICTS = [
    "Buskerud",
    "Finnmark",
    "Hordaland",
    "Innlandet",
    "Møre og Romsdal",
    "Nordland",
    "Stor-Oslo",
    "Rogaland",
    "Sogn og Fjordane",
    "Sørlandet",
    "Telemark",
    "Troms",
    "Trøndelag",
    "Vestfold",
    "Østfold",
]

STREAM_PATH = re.compile(r"/icecast/(mp3|aac)/(high|low)/([A-Za-z0-9]+)/([a-z0-9_]+)")


def fetch(url: str = SOURCE_URL) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8", errors="replace")


def parse_streams(html: str) -> tuple[str, dict[str, dict[str, str]]]:
    """Returner (token, {slug: {kvalitet: url}}) slik siden ser ut nå."""
    tokens: set[str] = set()
    streams: dict[str, dict[str, str]] = {}
    for codec, level, token, slug in STREAM_PATH.findall(html):
        tokens.add(token)
        quality = f"{codec}_{level}"
        url = f"https://lyd.nrk.no/icecast/{codec}/{level}/{token}/{slug}"
        streams.setdefault(slug, {})[quality] = url
    if not streams:
        raise SystemExit(f"Fant ingen strøm-URL-er på {SOURCE_URL} — har siden endret struktur?")
    if len(tokens) > 1:
        print(f"Merk: siden bruker flere tokens: {', '.join(sorted(tokens))}", file=sys.stderr)
    return sorted(tokens)[0], streams


def parse_districts(html: str) -> dict[str, str]:
    """Par distriktsnavn med kanal-slug ut fra rekkefølgen i dokumentet."""
    known = set(DISTRICTS)
    tokens: list[tuple[str, str]] = []
    pattern = re.compile(r">([^<>]{3,30})<|/icecast/mp3/high/[A-Za-z0-9]+/([a-z0-9_]+)")
    for match in pattern.finditer(html):
        if match.group(1) is not None:
            text = unescape(match.group(1)).strip()
            if text in known:
                tokens.append(("name", text))
        else:
            tokens.append(("slug", match.group(2)))

    mapping: dict[str, str] = {}
    for index, (kind, value) in enumerate(tokens):
        if kind != "name":
            continue
        slug = next((v for k, v in tokens[index + 1 :] if k == "slug"), None)
        if slug:
            mapping[value] = slug

    missing = known - mapping.keys()
    if missing:
        print(f"Merk: fant ikke slug for distrikt: {', '.join(sorted(missing))}", file=sys.stderr)
    return mapping


def slug_of(station: dict) -> str | None:
    """Hent kanal-slugen stations.json bruker for en NRK-kanal."""
    for url in station.get("streams", {}).values():
        match = STREAM_PATH.search(url)
        if match:
            return match.group(4)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--write", action="store_true", help="skriv endringene til stations.json")
    args = parser.parse_args()

    html = fetch()
    token, live = parse_streams(html)
    districts = parse_districts(html)
    print(f"lyd.nrk.no: token {token}, {len(live)} kanaler, {len(districts)} distrikter.\n")

    data = load_stations()
    nrk = [s for s in data["stations"] if s["broadcaster"] == "NRK"]

    changes: list[str] = []
    for station in nrk:
        # For distriktskanaler er slugen på NRK sin side sannheten — den kan
        # flytte seg mellom p1_dkN-numre når NRK slår sammen distriktskontorer.
        slug = districts.get(station["region"]) if station["region"] in districts else slug_of(station)
        if not slug:
            changes.append(f"! {station['id']} {station['name']}: klarte ikke å bestemme kanal-slug")
            continue
        if slug not in live:
            changes.append(f"! {station['id']} {station['name']}: slug '{slug}' finnes ikke lenger på lyd.nrk.no")
            continue
        for quality, url in sorted(live[slug].items()):
            current = station["streams"].get(quality)
            if current != url:
                changes.append(f"~ {station['id']} {station['name']} [{quality}]\n    før:  {current}\n    nå:   {url}")
                station["streams"][quality] = url

    known_slugs = {districts.get(s["region"], slug_of(s)) for s in nrk}
    for slug in sorted(set(live) - known_slugs):
        changes.append(f"+ ny kanal på lyd.nrk.no: '{slug}' — legg den til i stations.json manuelt")

    if not changes:
        print("Ingen endringer — NRK-URL-ene i stations.json er oppdatert.")
        return 0

    print("\n".join(changes))
    if args.write:
        save_stations(data)
        print("\nSkrev stations.json. Kjør deretter:")
        print("  python3 scripts/build_playlists.py")
        print("  python3 scripts/check_streams.py --report")
    else:
        print("\nTørrkjøring — kjør med --write for å lagre.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
