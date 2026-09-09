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
import sys

from common import REPO_ROOT, display_name, load_stations

OUTPUT = REPO_ROOT / "docs" / "index.html"

# Rekkefølgen kilder velges i for MCU2: MP3 først, AAC bare som siste utvei.
MCU2_QUALITIES = ["mp3_high", "mp3_low", "aac_high", "aac_low"]

QUALITY_LABELS = {"mp3_high": "MP3 høy", "mp3_low": "MP3", "aac_high": "AAC", "aac_low": "AAC lav"}


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
  --star: #ffc94d;
}
* { box-sizing: border-box; }
[hidden] { display: none !important; }
body {
  margin: 0; background: var(--bg); color: var(--text);
  font: 17px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  -webkit-text-size-adjust: 100%;
}
/* Toppen er festet, så hver piksel her spises av visningsflaten resten av
   tiden. Alt ligger derfor på én rad som bare brytes når bredden krever det —
   på en bilskjerm blir det én linje. */
header {
  position: sticky; top: 0; z-index: 10; background: var(--panel);
  border-bottom: 1px solid var(--line); padding: 8px 12px;
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
#now-text {
  flex: 1 1 170px; min-width: 0; display: flex; align-items: center; gap: 8px;
  background: var(--panel-hi); border: 1px solid var(--line); border-radius: 10px;
  padding: 0 12px; height: 46px;
}
/* Navnet kuttes med ellipse framfor å brekke til en ny linje og øke høyden. */
#now-name {
  font-size: 16px; font-weight: 600;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
#now-meta { color: var(--dim); font-size: 12px; white-space: nowrap; flex: 0 0 auto; }
button {
  font: inherit; color: var(--text); background: var(--panel-hi);
  border: 1px solid var(--line); border-radius: 10px; cursor: pointer;
}
#stop { flex: 0 0 auto; min-width: 84px; height: 46px; font-weight: 600; }
#stop:disabled { opacity: .4; }

/* Volumfeltet vises bare der nettleseren faktisk lar lydstyrken settes.
   I Tesla styres volumet av bilen, og på iOS er audio.volume skrivebeskyttet. */
#vol-wrap { display: flex; align-items: center; gap: 8px; flex: 0 1 150px; min-width: 120px; height: 46px; }
#vol-icon { color: var(--dim); font-size: 16px; flex: 0 0 auto; }
#vol {
  flex: 1; min-width: 70px; height: 46px; margin: 0;
  background: transparent; -webkit-appearance: none; appearance: none;
}
#vol::-webkit-slider-runnable-track { height: 8px; border-radius: 4px; background: var(--line); }
#vol::-moz-range-track { height: 8px; border-radius: 4px; background: var(--line); }
#vol::-webkit-slider-thumb {
  -webkit-appearance: none; appearance: none; width: 26px; height: 26px; margin-top: -9px;
  border: none; border-radius: 50%; background: var(--accent);
}
#vol::-moz-range-thumb { width: 26px; height: 26px; border: none; border-radius: 50%; background: var(--accent); }
#vol-val { color: var(--dim); font-size: 12px; min-width: 34px; text-align: right; font-variant-numeric: tabular-nums; flex: 0 0 auto; }

#filter {
  flex: 1 1 190px; min-width: 140px; height: 46px; padding: 0 12px; font: inherit;
  color: var(--text); background: var(--panel-hi);
  border: 1px solid var(--line); border-radius: 10px;
}
main { padding: 4px 12px 60px; max-width: 1400px; margin: 0 auto; }
h2 {
  font-size: 13px; text-transform: uppercase; letter-spacing: .08em;
  color: var(--dim); margin: 18px 0 8px;
}
/* 250px ga sju kolonner på en 1920px bilskjerm, som tvinger øyet til å skanne i
   to retninger. Bredere kort og et tak på main gir tre-fire kolonner. */
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 10px; }

/* Én rad = spilleknapp + stjerne. Stjernen kan ikke ligge inne i spilleknappen;
   en knapp inne i en knapp er ugyldig markup og oppfører seg uforutsigbart. */
.row { display: flex; gap: 6px; }
.play {
  flex: 1; display: flex; align-items: center; gap: 10px; text-align: left;
  min-height: 64px; padding: 10px 14px; min-width: 0;
}
.play:active { background: var(--accent); color: var(--accent-ink); }
.row[aria-current="true"] .play {
  background: var(--accent); color: var(--accent-ink); border-color: var(--accent);
}
.num {
  flex: 0 0 auto; min-width: 34px; font-variant-numeric: tabular-nums;
  color: var(--dim); font-size: 14px;
}
.row[aria-current="true"] .num { color: var(--accent-ink); }
.nm { flex: 1; font-weight: 600; overflow-wrap: anywhere; }
.fav {
  flex: 0 0 auto; width: 56px; min-height: 64px; font-size: 22px; line-height: 1;
  color: var(--dim);
}
.fav[aria-pressed="true"] { color: var(--star); }
footer { color: var(--dim); font-size: 13px; padding: 0 12px 40px; }
footer ul { padding-left: 20px; }
a { color: var(--accent); }
#fav-empty { color: var(--dim); font-size: 14px; }
#ua { word-break: break-all; font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 12px; }
"""

JS = """
var audio = new Audio();
audio.preload = 'none';
var nowName = document.getElementById('now-name');
var nowMeta = document.getElementById('now-meta');
var stopBtn = document.getElementById('stop');
var favSection = document.getElementById('favoritter');
var favGrid = document.getElementById('fav-grid');
var favEmpty = document.getElementById('fav-empty');
var currentId = null;

/* ---------------------------------------------------------------- lagring */
/* localStorage kan kaste i privat modus og der nettleseren blokkerer lagring,
   så alle kall er innkapslet. Siden skal virke uten at noe lagres. */
function lagre(nokkel, verdi) {
  try { localStorage.setItem(nokkel, verdi); } catch (e) {}
}
function hent(nokkel) {
  try { return localStorage.getItem(nokkel); } catch (e) { return null; }
}

function favoritter() {
  try {
    var raw = hent('favoritter');
    var liste = raw ? JSON.parse(raw) : [];
    return Array.isArray(liste) ? liste.map(String) : [];
  } catch (e) { return []; }
}
function settFavoritter(liste) { lagre('favoritter', JSON.stringify(liste)); }

/* ------------------------------------------------------------- favoritter */
/* Favorittradene er kloner av radene i kanallistene. Klikk håndteres med
   delegering på document, så klonene virker uten at noe bindes på nytt. */
function tegnFavoritter() {
  var liste = favoritter();
  favGrid.textContent = '';
  liste.forEach(function (id) {
    var kilde = document.querySelector('main > section:not(#favoritter) .row[data-id="' + id + '"]');
    if (kilde) { favGrid.appendChild(kilde.cloneNode(true)); }
  });
  favEmpty.hidden = liste.length > 0;
  favSection.hidden = false;
  oppdaterStjerner();
  merkSpillende();
}

function oppdaterStjerner() {
  var liste = favoritter();
  document.querySelectorAll('.row').forEach(function (rad) {
    var er = liste.indexOf(rad.dataset.id) !== -1;
    var stjerne = rad.querySelector('.fav');
    stjerne.setAttribute('aria-pressed', er ? 'true' : 'false');
    stjerne.title = er ? 'Fjern fra favoritter' : 'Legg til favoritter';
  });
}

function vekslFavoritt(id) {
  var liste = favoritter();
  var i = liste.indexOf(id);
  if (i === -1) { liste.push(id); } else { liste.splice(i, 1); }
  settFavoritter(liste);
  tegnFavoritter();
  filtrer();
}

/* ----------------------------------------------------------------- spiller */
/* En kanal kan finnes to steder samtidig — i favorittene og i sin egen gruppe —
   så markeringen settes på alle radene med samme id. */
function merkSpillende() {
  document.querySelectorAll('.row').forEach(function (rad) {
    rad.setAttribute('aria-current', rad.dataset.id === currentId ? 'true' : 'false');
  });
}

/* ------------------------------------------------- gjenoppkobling ved brudd */
/* En bil mister dekning i tunneler og utkanter, og en Icecast-strøm kan falle
   uten videre. Uten dette blir det bare stille, mens toppen fortsatt viser
   kanalnavnet som om alt er i orden. Vi prøver derfor igjen av oss selv, med
   økende pause slik at vi ikke hamrer på en server som er nede. */
var FORSTE_PAUSE = 1000;
var MAKS_PAUSE = 30000;
var pause = FORSTE_PAUSE;
var gjenopptaTimer = null;
var vaktTimer = null;
var vilSpille = false;   // brukerens intensjon, ikke elementets tilstand

function aktivRad() {
  return currentId && document.querySelector('.row[data-id="' + currentId + '"]');
}

function avbrytTimere() {
  if (gjenopptaTimer) { clearTimeout(gjenopptaTimer); gjenopptaTimer = null; }
  if (vaktTimer) { clearTimeout(vaktTimer); vaktTimer = null; }
}

function planleggGjenopptak(grunn) {
  if (!vilSpille || gjenopptaTimer) { return; }
  nowMeta.textContent = grunn + ' — prøver igjen om ' + Math.round(pause / 1000) + ' s';
  gjenopptaTimer = setTimeout(function () {
    gjenopptaTimer = null;
    pause = Math.min(pause * 2, MAKS_PAUSE);
    kobleTil();
  }, pause);
}

function kobleTil() {
  var rad = aktivRad();
  if (!rad || !vilSpille) { return; }
  nowMeta.textContent = 'kobler til …';
  // Ny src på samme element: unngår at flere strømmer lastes samtidig.
  audio.src = rad.dataset.url;
  var forsok = audio.play();
  if (forsok && forsok.catch) {
    forsok.catch(function (err) {
      // NotAllowedError betyr manglende brukertrykk — da hjelper ikke nye forsøk.
      if (err && err.name === 'NotAllowedError') {
        vilSpille = false;
        nowMeta.textContent = 'trykk for å spille';
        return;
      }
      planleggGjenopptak('ingen forbindelse');
    });
  }
}

function spill(rad) {
  avbrytTimere();
  pause = FORSTE_PAUSE;
  vilSpille = true;
  currentId = rad.dataset.id;
  merkSpillende();
  nowName.textContent = rad.dataset.name;
  stopBtn.disabled = false;
  kobleTil();
  lagre('sisteKanal', currentId);
  oppdaterMediaSession(rad);
}

function stopp() {
  vilSpille = false;
  avbrytTimere();
  audio.pause();
  audio.removeAttribute('src');
  audio.load();
  currentId = null;
  merkSpillende();
  nowName.textContent = 'Ingen kanal';
  nowMeta.textContent = '';
  stopBtn.disabled = true;
  if ('mediaSession' in navigator) {
    try { navigator.mediaSession.playbackState = 'none'; } catch (e) {}
  }
}

audio.addEventListener('playing', function () {
  avbrytTimere();
  pause = FORSTE_PAUSE;
  var rad = aktivRad();
  if (rad) { nowMeta.textContent = rad.dataset.quality; }
  if ('mediaSession' in navigator) {
    try { navigator.mediaSession.playbackState = 'playing'; } catch (e) {}
  }
});

audio.addEventListener('error', function () { planleggGjenopptak('strømmen falt'); });

// En direktestrøm skal aldri ta slutt; skjer det, har den blitt brutt.
audio.addEventListener('ended', function () { planleggGjenopptak('strømmen ble brutt'); });

// stalled/waiting kan gå over av seg selv, så vi venter litt før vi river ned
// og kobler på nytt — men ikke i det uendelige.
function settVakt(tekst) {
  if (!vilSpille || vaktTimer) { return; }
  nowMeta.textContent = tekst;
  vaktTimer = setTimeout(function () {
    vaktTimer = null;
    if (vilSpille && audio.paused) { planleggGjenopptak('strømmen stoppet'); }
  }, 8000);
}
audio.addEventListener('stalled', function () { settVakt('strømmen stopper opp …'); });
audio.addEventListener('waiting', function () { settVakt('venter på data …'); });

window.addEventListener('offline', function () {
  if (vilSpille) { nowMeta.textContent = 'ingen nettverk'; }
});
window.addEventListener('online', function () {
  // Nettet er tilbake: prøv straks, uten å vente ut pausen.
  if (vilSpille && audio.paused) {
    avbrytTimere();
    pause = FORSTE_PAUSE;
    kobleTil();
  }
});

/* ------------------------------------------------------------ Media Session */
/* Gir kanalnavn på låseskjermen og lar systemets egne knapper — og på noen
   biler rattknappene — styre avspillingen. */
function synligeRader() {
  return [].slice.call(document.querySelectorAll('main > section:not(#favoritter) .row'));
}

function bytteKanal(steg) {
  var rader = synligeRader();
  var i = -1;
  for (var n = 0; n < rader.length; n++) {
    if (rader[n].dataset.id === currentId) { i = n; break; }
  }
  if (i === -1) { return; }
  var neste = rader[(i + steg + rader.length) % rader.length];
  if (neste) { spill(neste); }
}

function oppdaterMediaSession(rad) {
  if (!('mediaSession' in navigator)) { return; }
  try {
    if (typeof MediaMetadata !== 'undefined') {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: rad.dataset.name,
        artist: rad.dataset.broadcaster || 'Norsk radio',
        album: 'Norsk radio',
      });
    }
    navigator.mediaSession.playbackState = 'playing';
  } catch (e) {}
}

if ('mediaSession' in navigator) {
  var handlinger = {
    play: function () { var rad = aktivRad(); if (rad) { spill(rad); } },
    pause: stopp,
    stop: stopp,
    nexttrack: function () { bytteKanal(1); },
    previoustrack: function () { bytteKanal(-1); },
  };
  Object.keys(handlinger).forEach(function (navn) {
    // Ikke alle handlinger støttes overalt; en ustøttet gir TypeError.
    try { navigator.mediaSession.setActionHandler(navn, handlinger[navn]); } catch (e) {}
  });
}

document.addEventListener('click', function (event) {
  var stjerne = event.target.closest('.fav');
  if (stjerne) { vekslFavoritt(stjerne.closest('.row').dataset.id); return; }
  var play = event.target.closest('.play');
  if (play) { spill(play.closest('.row')); }
});
stopBtn.addEventListener('click', stopp);

/* ------------------------------------------------------------------ volum */
/* Volumfeltet er meningsløst der bilen eller systemet styrer lydstyrken, så det
   skjules der. Automatikken kan ikke gjøres helt sikker:

   - I Chromium kan audio.volume ALLTID settes, også i Tesla. Prøven under
     fanger derfor bare iOS, der volume er skrivebeskyttet og blir stående på 1.
   - Tesla-nettleseren oppgir ikke alltid «Tesla» i nettleserstrengen.

   Gjetter den feil, blir volumfeltet stående synlig. Det koster ingen høyde:
   feltet ligger på samme rad som resten av toppen. Nettleserstrengen vises
   nederst på siden, slik at deteksjonen kan gjøres treffsikker for en skjerm
   som oppfører seg annerledes. */
function volumKanSettes() {
  try {
    var probe = new Audio();
    probe.volume = 0.42;
    return Math.abs(probe.volume - 0.42) < 0.01;
  } catch (e) { return false; }
}

function ventetBilskjerm() {
  var ua = navigator.userAgent;
  if (/Tesla|QtCarBrowser/i.test(ua)) { return true; }
  // Linux med berøringsskjerm og uten Android er nesten alltid en bilskjerm.
  // Skulle det treffe en Linux-maskin med touch, slår brukeren det på igjen.
  var linux = /Linux|X11/i.test(ua) && !/Android/i.test(ua);
  var touch = (navigator.maxTouchPoints || 0) > 0;
  return linux && touch;
}

var volWrap = document.getElementById('vol-wrap');
var vol = document.getElementById('vol');
var volVal = document.getElementById('vol-val');

function settVolum(prosent) {
  audio.volume = Math.min(100, Math.max(0, prosent)) / 100;
  volVal.textContent = Math.round(prosent) + ' %';
}

var lagretVolum = parseInt(hent('volum'), 10);
if (isNaN(lagretVolum)) { lagretVolum = 100; }

var visVolum = volumKanSettes() && !ventetBilskjerm();
volWrap.hidden = !visVolum;

if (visVolum) {
  vol.value = lagretVolum;
  settVolum(lagretVolum);
  vol.addEventListener('input', function () { settVolum(parseInt(vol.value, 10)); });
  vol.addEventListener('change', function () { lagre('volum', vol.value); });
}

var uaLinje = document.getElementById('ua');
if (uaLinje) { uaLinje.textContent = navigator.userAgent; }

/* ------------------------------------------------------------------- søk */
var filter = document.getElementById('filter');
function filtrer() {
  var q = filter.value.trim().toLowerCase();
  document.querySelectorAll('main > section').forEach(function (section) {
    var synlige = 0;
    section.querySelectorAll('.row').forEach(function (rad) {
      var treff = !q || rad.dataset.search.indexOf(q) !== -1;
      rad.hidden = !treff;
      if (treff) { synlige++; }
    });
    // Favorittseksjonen beholdes ved tomt søk, slik at tomteksten kan vises.
    if (section.id === 'favoritter') {
      section.hidden = q !== '' && synlige === 0;
      favEmpty.hidden = q !== '' || favoritter().length > 0;
    } else {
      section.hidden = synlige === 0;
    }
  });
}
filter.addEventListener('input', filtrer);

/* ------------------------------------------------------------- oppstart */
tegnFavoritter();

// Marker forrige kanal, men start ikke av seg selv: nettlesere krever et trykk
// for å spille lyd, og bilen skal ikke begynne å lage lyd ved åpning.
var siste = hent('sisteKanal');
if (siste) {
  var rad = document.querySelector('.row[data-id="' + siste + '"]');
  if (rad) {
    nowName.textContent = rad.dataset.name;
    nowMeta.textContent = 'trykk for å spille';
  }
}
"""


def row_html(station: dict, url: str, quality: str) -> str:
    shown = display_name(station)
    haystack = " ".join(
        bit for bit in [shown, station["broadcaster"], station["region"], station.get("area", "")] if bit
    ).lower()
    return (
        "<div class='row'"
        f' data-id="{station["id"]}"'
        f' data-url="{html.escape(url, quote=True)}"'
        f' data-name="{html.escape(shown, quote=True)}"'
        f' data-quality="{QUALITY_LABELS[quality]}"'
        f' data-broadcaster="{html.escape(station["broadcaster"], quote=True)}"'
        f' data-search="{html.escape(haystack, quote=True)}"'
        " aria-current='false'>"
        "<button class='play' type='button'>"
        f"<span class='num'>{station['id']}</span>"
        f"<span class='nm'>{html.escape(shown)}</span>"
        "</button>"
        "<button class='fav' type='button' aria-pressed='false'"
        f' aria-label="Favoritt: {html.escape(shown, quote=True)}"'
        " title='Legg til favoritter'>★</button>"
        "</div>"
    )


def main() -> int:
    data = load_stations()
    groups: dict[str, list[tuple[dict, str, str]]] = {}
    skipped: list[dict] = []

    offair: list[dict] = []
    for station in data["stations"]:
        if station.get("offair"):
            offair.append(station)
            continue
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
        '<div id="now-text"><span id="now-name">Ingen kanal</span><span id="now-meta"></span></div>',
        '<div id="vol-wrap" hidden>',
        '<span id="vol-icon" aria-hidden="true">\U0001f50a</span>',
        '<input id="vol" type="range" min="0" max="100" step="1" value="100" aria-label="Volum">',
        '<span id="vol-val">100 %</span>',
        "</div>",
        f'<input id="filter" type="search" placeholder="Søk blant {playable} kanaler" autocomplete="off">',
        '<button id="stop" type="button" disabled>Stopp</button>',
        "</header>",
        "<main>",
        "<section id='favoritter' hidden><h2>Favoritter</h2>",
        "<p id='fav-empty'>Trykk stjernen ved en kanal for å legge den her.</p>",
        "<div class='grid' id='fav-grid'></div></section>",
    ]

    for group in order:
        parts.append(f"<section><h2>{html.escape(group)}</h2><div class='grid'>")
        # NRK, Bauer og P4 har meningsfull nummerering (P1, P1+, P2, P3 …), så
        # der beholdes kanalnummer-rekkefølgen. Inne i et fylke er nummeret
        # tilfeldig — det følger hvilken Icecast-vert kanalen ble funnet på — og
        # da er alfabetisk det man forventer når man leter etter et navn.
        etter_navn = all(row[0]["id"] >= 100 for row in groups[group])
        nøkkel = (lambda row: display_name(row[0]).lower()) if etter_navn else (lambda row: row[0]["id"])
        for station, url, quality in sorted(groups[group], key=nøkkel):
            parts.append(row_html(station, url, quality))
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
    if offair:
        parts.append(
            "<p>Disse er av lufta nå — kilden sender ikke, så strømmen svarer ikke:</p><ul>"
        )
        for station in offair:
            parts.append(f"<li>{station['id']}. {html.escape(display_name(station))}</li>")
        parts.append("</ul>")
    parts.append(
        "<p>Favoritter, volum og valget over lagres bare i denne nettleseren, "
        "ikke på nett.</p>"
    )
    parts.append('<p>Nettleseren din melder seg som:<br><span id="ua"></span></p>')
    parts.append(
        "<p>Generert av <code>scripts/build_webplayer.py</code> fra "
        '<a href="https://github.com/nilz76/norske-radiokanaler">norske-radiokanaler</a>. '
        "Rediger stations.json, ikke denne filen.</p>"
    )
    parts.append("</footer>")
    parts.append(f"<script>{JS}</script>")

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
    print(f"{OUTPUT.relative_to(REPO_ROOT)}: {playable} spillbare kanaler, "
          f"{len(skipped)} utelatt, {len(offair)} av lufta")
    for station in offair:
        print(f"  av lufta: {station['id']} {station['name']}")
    for station in skipped:
        print(f"  utelatt (kun http): {station['id']} {station['name']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
