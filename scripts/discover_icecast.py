#!/usr/bin/env python3
"""Finn kanaler ved å spørre Icecast-serverne om hva de sender.

De fleste norske lokalradioene kjører Icecast, og en Icecast-server lister alle
mount-punktene sine med navn på `/status-json.xsl`. Det er den raskeste veien til
nye kanaler: finn én strøm-URL, spør verten, og få resten på samme server.

Bruk:
    python3 scripts/discover_icecast.py                      # spør vertene i stations.json
    python3 scripts/discover_icecast.py lyd7.lokalradio.no   # spør en bestemt vert
    python3 scripts/discover_icecast.py --new                # vis bare mount-punkter som mangler

Utdata er sortert på vertsnavn og markerer hvilke mount-punkter som allerede
ligger i stations.json. Nye funn må legges inn manuelt — skriptet gjetter ikke
kanalnavn, region eller hjemmeside.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from common import iter_streams, load_stations

USER_AGENT = "radio-streamurls/1.0 (+https://github.com/)"
MAX_STATUS_BYTES = 512_000


def hosts_in_use() -> list[str]:
    """Vertsnavnene stations.json alt bruker — utgangspunktet for et søk."""
    hosts = set()
    for _station, _quality, url in iter_streams(load_stations()):
        hosts.add(urllib.parse.urlparse(url).netloc)
    return sorted(hosts)


def known_mounts() -> set[str]:
    """Alle (vert, sti) som alt ligger i stations.json."""
    mounts = set()
    for _station, _quality, url in iter_streams(load_stations()):
        parsed = urllib.parse.urlparse(url)
        mounts.add((parsed.netloc, parsed.path))
    return mounts


def query(host: str) -> list[dict]:
    """Hent mount-listen fra en Icecast-vert. Tom liste hvis den ikke svarer."""
    for scheme in ("https", "http"):
        request = urllib.request.Request(
            f"{scheme}://{host}/status-json.xsl", headers={"User-Agent": USER_AGENT}
        )
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                # Noen verter svarer med en lydstrøm på denne stien. Da hjelper
                # ikke timeout: den gjelder per socket-operasjon, og en strøm som
                # trikler inn holder tilkoblingen åpen i det uendelige. Sjekk
                # derfor content-type før vi leser, og les alltid begrenset.
                content_type = (response.headers.get("Content-Type") or "").lower()
                if "json" not in content_type and "text" not in content_type:
                    continue
                raw = response.read(MAX_STATUS_BYTES)
            payload = json.loads(raw.decode("utf-8", "replace"))
        except Exception:  # noqa: BLE001 — verten svarer ikke, prøv neste skjema
            continue

        sources = payload.get("icestats", {}).get("source", [])
        sources = sources if isinstance(sources, list) else [sources]
        rows = []
        for source in sources:
            listenurl = source.get("listenurl") or ""
            path = urllib.parse.urlparse(listenurl).path if listenurl else ""
            rows.append({
                "host": host,
                "scheme": scheme,
                "name": (source.get("server_name") or "").strip(),
                "path": path,
                "codec": source.get("server_type", ""),
                "bitrate": source.get("bitrate") or "",
                "listeners": source.get("listeners", 0),
            })
        return rows
    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("hosts", nargs="*", help="vertsnavn å spørre (standard: vertene i stations.json)")
    parser.add_argument("--new", action="store_true", help="vis bare mount-punkter som ikke er i stations.json")
    args = parser.parse_args()

    hosts = args.hosts or hosts_in_use()
    print(f"Spør {len(hosts)} verter …\n", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=12) as pool:
        rows = [row for result in pool.map(query, hosts) for row in result]

    if not rows:
        print("Ingen av vertene svarte på /status-json.xsl.", file=sys.stderr)
        return 1

    known = known_mounts()
    shown = 0
    for row in sorted(rows, key=lambda r: (r["host"], r["path"])):
        is_known = (row["host"], row["path"]) in known
        if args.new and is_known:
            continue
        mark = "  " if is_known else "NY"
        name = row["name"] or "(uten navn)"
        url = f"{row['scheme']}://{row['host']}{row['path']}"
        print(f"{mark} {name[:32]:32} {row['codec']:16} {str(row['bitrate']):>6}  {url}")
        shown += 1

    print(f"\n{shown} mount-punkter vist ({len(rows)} funnet totalt).", file=sys.stderr)
    if args.new:
        print("Legg nye kanaler inn i stations.json — se CONTRIBUTING.md.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
