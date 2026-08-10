#!/usr/bin/env python3
"""Sjekk at alle strøm-URL-er i stations.json fortsatt fungerer.

Bruk:
    python3 scripts/check_streams.py                # sjekk alt, skriv rapport til stdout
    python3 scripts/check_streams.py --report       # oppdater også STATUS.md
    python3 scripts/check_streams.py --only NRK     # bare kanaler fra én kringkaster
    python3 scripts/check_streams.py --quiet        # bare vis feil

Avslutningskode 0 = alt OK, 1 = én eller flere døde strømmer.
En strøm regnes som levende når den svarer 200/206 med en lyd-relatert
content-type, eller når serveren sender lyddata uten content-type.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from common import QUALITY_LABELS, iter_streams, load_stations, REPO_ROOT

USER_AGENT = "radio-streamurls/1.0 (+https://github.com/)"
TIMEOUT = 12
AUDIO_HINTS = (
    "audio/",
    # Noen Icecast-verter merker Ogg- og MP3-strømmer med application/*.
    "application/ogg",
    "application/mpeg",
    "application/vnd.apple.mpegurl",
    "application/x-mpegurl",
    "video/mp2t",
)


def check_url(url: str) -> tuple[bool, str]:
    """Åpne strømmen, les litt data, og avgjør om den er levende."""
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Icy-MetaData": "1",
            # Icecast overser vanligvis Range, men noen CDN-er svarer 206 og
            # lukker tilkoblingen pent i stedet for å strømme i det uendelige.
            "Range": "bytes=0-2047",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT) as response:
            status = response.status
            content_type = (response.headers.get("Content-Type") or "").lower()
            payload = response.read(2048)
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return False, f"nettverksfeil: {exc.reason}"
    except TimeoutError:
        return False, "tidsavbrudd"
    except OSError as exc:
        return False, f"feil: {exc}"

    if status not in (200, 206):
        return False, f"HTTP {status}"
    if content_type and not content_type.startswith(AUDIO_HINTS):
        return False, f"uventet content-type: {content_type}"
    if not payload:
        return False, "ingen data"
    return True, f"HTTP {status} {content_type or 'ukjent type'}".strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", metavar="KRINGKASTER", help="sjekk bare kanaler fra denne kringkasteren")
    parser.add_argument("--report", action="store_true", help="skriv STATUS.md")
    parser.add_argument("--quiet", action="store_true", help="vis bare døde strømmer")
    parser.add_argument("--workers", type=int, default=8, help="antall parallelle sjekker (standard 8)")
    args = parser.parse_args()

    data = load_stations()
    jobs = [
        (station, quality, url)
        for station, quality, url in iter_streams(data)
        if not args.only or station["broadcaster"].lower() == args.only.lower()
    ]
    if not jobs:
        print("Ingen strømmer å sjekke.", file=sys.stderr)
        return 1

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        outcomes = list(pool.map(lambda job: check_url(job[2]), jobs))

    results = [(station, quality, url, ok, detail) for (station, quality, url), (ok, detail) in zip(jobs, outcomes)]
    dead = [row for row in results if not row[3]]

    for station, quality, url, ok, detail in results:
        if ok and args.quiet:
            continue
        mark = "OK  " if ok else "DØD "
        print(f"{mark} {station['id']:>3}  {station['name']} [{QUALITY_LABELS[quality]}]  {detail}")
        if not ok:
            print(f"          {url}")

    print(f"\n{len(results) - len(dead)}/{len(results)} strømmer OK.")
    if dead:
        broadcasters = sorted({row[0]["broadcaster"] for row in dead})
        print(f"Døde strømmer hos: {', '.join(broadcasters)}")
        if "NRK" in broadcasters:
            print("Prøv: python3 scripts/refresh_nrk.py   (henter gjeldende URL-er fra lyd.nrk.no)")
        print("Se README.md → «Når en strøm slutter å virke» for framgangsmåte.")

    if args.report:
        write_report(results, dead)
        print(f"Skrev {(REPO_ROOT / 'STATUS.md')}")

    return 1 if dead else 0


def write_report(results, dead) -> None:
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Status for strømmene",
        "",
        f"Sist sjekket: {now}",
        "",
        f"{len(results) - len(dead)} av {len(results)} strømmer svarte.",
        "",
        "| Nr. | Kanal | Kvalitet | Status | Detaljer |",
        "| --: | ----- | -------- | ------ | -------- |",
    ]
    for station, quality, _url, ok, detail in results:
        status = "✅ OK" if ok else "❌ Død"
        lines.append(f"| {station['id']} | {station['name']} | {QUALITY_LABELS[quality]} | {status} | {detail} |")
    lines.append("")
    lines.append("Generert av `scripts/check_streams.py --report`.")
    (REPO_ROOT / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
