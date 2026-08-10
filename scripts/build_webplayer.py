#!/usr/bin/env python3
"""Generer docs/index.html — en nettleserspiller laget for Tesla MCU2 og liknende.

Siden er én fil uten avhengigheter, med store trykkflater og ett enkelt
<audio>-element som bytter kilde. Den bygges fra stations.json.

Nettleseren i MCU2 legger to begrensninger på hvilke strømmer som kan brukes:

1. Siden serveres over https (GitHub Pages), og da blokkerer Chromium alle
   http-strømmer som mixed content. Bare https-URL-er kommer med.
2. AAC i Icecast (audio/aacp) spilles ikke pålitelig. MP3 velges når kanalen har
   det, og AAC brukes bare når det er eneste alternativ.

Kanaler som ikke har noen https-strøm listes nederst på siden som utelatt, med
begrunnelse, slik at de ikke bare blir borte i det stille.

Bruk:
    python3 scripts/build_webplayer.py
"""

from __future__ import annotations

import html
import json
import sys

from common import REPO_ROOT, display_name, load_stations

OUTPUT = REPO_ROOT / "docs" / "index.html"

# Rekkefølgen kilder velges i for MCU2: MP3 først, AAC bare som siste utvei.
MCU2_QUALITIES = ["mp3_high", "mp3_low", "aac_high", "aac_low"]


def playable_url(station: dict) -> tuple[str | None, str | None]:
    """Returner (url, kvalitet) som er trygg i MCU2, eller (None, None)."""
    for quality in MCU2_QUALITIES:
        url = station.get("streams", {}).get(quality)
        if url and url.startswith("https://"):
            return url, quality
    return None, None


def group_of(station: dict) -> str:
    if station["broadcaster"] == "NRK":
        return "NRK" if station["region"] == "Riksdekkende" else "NRK P1 distrikt"
    if station["id"] < 100:
        return station["broadcaster"]
    return station["region"]


CSS = """
:root {
  --bg: #12141a; --panel: #1c1f27; --panel-hi: #262a35; --line: #333846;
  --text: #f2f4f8; --dim: #9aa3b4; --accent: #4da3ff; --accent-ink: #06121f;
}
* { box-sizing: border-box; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 17px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  -webkit-text-size-adjust: 100%;
}
header {
  position: sticky; top: 0; z-index: 10; background: var(--panel);
  border-bottom: 1px solid var(--line); padding: 14px 18px;
}
h1 { margin: 0 0 4px; font-size: 20px; }
.sub { color: var(--dim); font-size: 14px; }
#now {
  display: flex; align-items: center; gap: 14px; margin-top: 12px;
  background: var(--panel-hi); border: 1px solid var(--line); border-radius: 12px;
  padding: 12px 14px; min-height: 62px;
}
#now-name { flex: 1; font-size: 18px; font-weight: 600; }
#now-meta { color: var(--dim); font-size: 13px; font-weight: 400; }
button {
  font: inherit; color: var(--text); background: var(--panel-hi);
  border: 1px solid var(--line); border-radius: 12px; cursor: pointer;
}
#stop {
  min-width: 104px; min-height: 52px; font-weight: 600;
}
#stop:disabled { opacity: .4; }
#filter {
  width: 100%; margin-top: 10px; padding: 14px; font: inherit;
  color: var(--text); background: var(--panel-hi);
  border: 1px solid var(--line); border-radius: 12px;
}
main { padding: 8px 18px 60px; }
h2 {
  font-size: 14px; text-transform: uppercase; letter-spacing: .08em;
  color: var(--dim); margin: 26px 0 10px;
}
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; }
.station {
  display: flex; align-items: center; gap: 10px; text-align: left;
  min-height: 64px; padding: 10px 14px;
}
.station:active { background: var(--accent); color: var(--accent-ink); }
.station[aria-current="true"] {
  background: var(--accent); color: var(--accent-ink); border-color: var(--accent);
}
.num {
  flex: 0 0 auto; min-width: 34px; font-variant-numeric: tabular-nums;
  color: var(--dim); font-size: 14px;
}
.station[aria-current="true"] .num { color: var(--accent-ink); }
.nm { flex: 1; font-weight: 600; }
footer { color: var(--dim); font-size: 13px; padding: 0 18px 40px; }
footer ul { padding-left: 20px; }
a { color: var(--accent); }
.hidden { display: none !important; }
"""

JS = """
var audio = new Audio();
audio.preload = 'none';
var nowName = document.getElementById('now-name');
var nowMeta = document.getElementById('now-meta');
var stopBtn = document.getElementById('stop');
var current = null;

function play(button) {
  if (current) { current.setAttribute('aria-current', 'false'); }
  current = button;
  button.setAttribute('aria-current', 'true');
  nowName.textContent = button.dataset.name;
  nowMeta.textContent = 'kobler til …';
  stopBtn.disabled = false;
  // Ny src på samme element: unngår at flere strømmer lastes samtidig.
  audio.src = button.dataset.url;
  audio.play().then(function () {
    nowMeta.textContent = button.dataset.quality;
  }).catch(function (err) {
    nowMeta.textContent = 'kunne ikke spille: ' + err.message;
  });
  try { localStorage.setItem('sisteKanal', button.dataset.id); } catch (e) {}
}

function stop() {
  audio.pause();
  audio.removeAttribute('src');
  audio.load();
  if (current) { current.setAttribute('aria-current', 'false'); current = null; }
  nowName.textContent = 'Ingen kanal';
  nowMeta.textContent = '';
  stopBtn.disabled = true;
}

audio.addEventListener('stalled', function () { nowMeta.textContent = 'strømmen stopper opp …'; });
audio.addEventListener('playing', function () {
  if (current) { nowMeta.textContent = current.dataset.quality; }
});

document.querySelectorAll('.station').forEach(function (button) {
  button.addEventListener('click', function () { play(button); });
});
stopBtn.addEventListener('click', stop);

// Søkefeltet skjuler både kanaler og grupper som blir tomme.
var filter = document.getElementById('filter');
filter.addEventListener('input', function () {
  var q = filter.value.trim().toLowerCase();
  document.querySelectorAll('section').forEach(function (section) {
    var synlige = 0;
    section.querySelectorAll('.station').forEach(function (button) {
      var treff = !q || button.dataset.search.indexOf(q) !== -1;
      button.classList.toggle('hidden', !treff);
      if (treff) { synlige++; }
    });
    section.classList.toggle('hidden', synlige === 0);
  });
});

// Marker forrige kanal, men start ikke av seg selv: nettlesere krever et
// trykk for å spille lyd, og bilen skal ikke begynne å lage lyd ved åpning.
try {
  var siste = localStorage.getItem('sisteKanal');
  if (siste) {
    var button = document.querySelector('.station[data-id="' + siste + '"]');
    if (button) {
      nowName.textContent = button.dataset.name;
      nowMeta.textContent = 'trykk for å spille';
    }
  }
} catch (e) {}
"""


def main() -> int:
    data = load_stations()
    groups: dict[str, list[tuple[dict, str, str]]] = {}
    skipped: list[dict] = []

    for station in data["stations"]:
        url, quality = playable_url(station)
        if not url:
            skipped.append(station)
            continue
        groups.setdefault(group_of(station), []).append((station, url, quality))

    # NRK og de riksdekkende kommersielle først, deretter fylkene alfabetisk.
    lead = ["NRK", "NRK P1 distrikt", "Bauer Media", "P4-gruppen"]
    order = [g for g in lead if g in groups] + sorted(g for g in groups if g not in lead)

    playable = sum(len(v) for v in groups.values())
    parts = [
        "<title>Norsk radio</title>",
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<style>{CSS}</style>",
        "<header>",
        "<h1>Norsk radio</h1>",
        f'<div class="sub">{playable} kanaler — trykk for å spille</div>',
        '<div id="now"><div id="now-name">Ingen kanal<div id="now-meta"></div></div>',
        '<button id="stop" disabled>Stopp</button></div>',
        '<input id="filter" type="search" placeholder="Søk på kanal eller fylke" autocomplete="off">',
        "</header>",
        "<main>",
    ]

    labels = {"mp3_high": "MP3 høy", "mp3_low": "MP3", "aac_high": "AAC", "aac_low": "AAC lav"}
    for group in order:
        parts.append(f"<section><h2>{html.escape(group)}</h2><div class='grid'>")
        for station, url, quality in sorted(groups[group], key=lambda row: row[0]["id"]):
            shown = display_name(station)
            haystack = " ".join(filter(None, [
                shown, station["broadcaster"], station["region"], station.get("area", "")
            ])).lower()
            parts.append(
                "<button class='station'"
                f' data-id="{station["id"]}"'
                f' data-url="{html.escape(url, quote=True)}"'
                f' data-name="{html.escape(shown, quote=True)}"'
                f' data-quality="{labels[quality]}"'
                f' data-search="{html.escape(haystack, quote=True)}">'
                f"<span class='num'>{station['id']}</span>"
                f"<span class='nm'>{html.escape(shown)}</span>"
                "</button>"
            )
        parts.append("</div></section>")
    parts.append("</main>")

    parts.append("<footer>")
    if skipped:
        parts.append(
            f"<p>{len(skipped)} kanaler er utelatt fordi de bare finnes over http. "
            "Denne siden går over https, og nettleseren blokkerer da http-strømmer "
            "som usikkert innhold:</p><ul>"
        )
        for station in skipped:
            parts.append(f"<li>{station['id']}. {html.escape(display_name(station))}</li>")
        parts.append("</ul>")
    parts.append(
        "<p>Generert av <code>scripts/build_webplayer.py</code> fra "
        '<a href="https://github.com/nilz76/norske-radiokanaler">norske-radiokanaler</a>. '
        "Rediger stations.json, ikke denne filen.</p>"
    )
    parts.append("</footer>")
    parts.append(f"<script>{JS}</script>")

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"{OUTPUT.relative_to(REPO_ROOT)}: {playable} spillbare kanaler, {len(skipped)} utelatt")
    for station in skipped:
        print(f"  utelatt (kun http): {station['id']} {station['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
