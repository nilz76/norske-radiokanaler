#!/usr/bin/env python3
"""Generer M3U-spillelister fra stations.json.

Bruk:
    python3 scripts/build_playlists.py
    python3 scripts/build_playlists.py --quality aac_high

Spillelistene i playlists/ er generert — rediger stations.json, ikke .m3u-filene.
"""

from __future__ import annotations

import argparse
import sys

from common import QUALITIES, REPO_ROOT, best_url, load_stations

PLAYLIST_DIR = REPO_ROOT / "playlists"


def write_playlist(filename: str, title: str, stations: list[dict], quality: str) -> int:
    lines = [
        "#EXTM3U",
        f"# {title}",
        "# Generert av scripts/build_playlists.py — rediger stations.json i stedet.",
    ]
    written = 0
    for station in stations:
        url = best_url(station, preferred=quality)
        if not url:
            print(f"Hopper over {station['name']}: ingen strøm-URL", file=sys.stderr)
            continue
        attrs = f'tvg-chno="{station["id"]}" tvg-name="{station["name"]}" group-title="{station["broadcaster"]}"'
        lines.append(f"#EXTINF:-1 {attrs},{station['id']}. {station['name']}")
        lines.append(url)
        written += 1

    PLAYLIST_DIR.mkdir(exist_ok=True)
    (PLAYLIST_DIR / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{filename}: {written} kanaler")
    return written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--quality",
        choices=QUALITIES,
        default="mp3_high",
        help="foretrukket kvalitet (faller tilbake til beste tilgjengelige, standard mp3_high)",
    )
    args = parser.parse_args()

    stations = load_stations()["stations"]
    nrk = [s for s in stations if s["broadcaster"] == "NRK"]

    write_playlist("alle-kanaler.m3u", "Alle norske radiokanaler", stations, args.quality)
    write_playlist("nrk.m3u", "NRK — riksdekkende kanaler", [s for s in nrk if s["region"] == "Riksdekkende"], args.quality)
    write_playlist("nrk-distrikt.m3u", "NRK P1 — distriktskanaler", [s for s in nrk if s["region"] != "Riksdekkende"], args.quality)
    write_playlist("kommersielle.m3u", "Kommersielle kanaler", [s for s in stations if s["broadcaster"] != "NRK"], args.quality)
    return 0


if __name__ == "__main__":
    sys.exit(main())
