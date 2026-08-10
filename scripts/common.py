"""Delte hjelpefunksjoner for skriptene i dette repoet."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIONS_FILE = REPO_ROOT / "stations.json"

# Rekkefølgen kvaliteter foretrekkes i, best først.
QUALITIES = ["mp3_high", "aac_high", "mp3_low", "aac_low"]

QUALITY_LABELS = {
    "mp3_high": "MP3 høy",
    "mp3_low": "MP3 lav",
    "aac_high": "AAC høy",
    "aac_low": "AAC lav",
}


def load_stations(path: Path = STATIONS_FILE) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def save_stations(data: dict, path: Path = STATIONS_FILE) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def display_name(station: dict) -> str:
    """Navnet som vises i spillelistene.

    Regionale kanaler får fylket bak navnet, slik at de er lette å skille i VLC
    og andre spillere. Fylket utelates når det alt står i navnet — det gir
    «NRK P1 Buskerud», men «NRK P1 Hordaland (Vestland)», siden Hordaland ikke
    er et fylke lenger.
    """
    name = station["name"]
    region = station.get("region", "")
    if region in ("", "Riksdekkende"):
        return name
    if re.search(rf"\b{re.escape(region)}\b", name):
        return name
    return f"{name} ({region})"


def best_url(station: dict, preferred: str | None = None) -> str | None:
    """Returner beste tilgjengelige strøm-URL for en kanal."""
    streams = station.get("streams", {})
    if preferred and streams.get(preferred):
        return streams[preferred]
    for quality in QUALITIES:
        if streams.get(quality):
            return streams[quality]
    return None


def iter_streams(data: dict):
    """Gå gjennom alle (kanal, kvalitet, url) i datasettet."""
    for station in data["stations"]:
        for quality in QUALITIES:
            url = station.get("streams", {}).get(quality)
            if url:
                yield station, quality, url
