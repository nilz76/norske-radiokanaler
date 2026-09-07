/**
 * Tester logikken i docs/index.html — favoritter, spilling, volum og søk.
 *
 * Krever jsdom, som er den eneste avhengigheten i repoet og med vilje ikke
 * committet:
 *
 *     npm install jsdom
 *     node tests/player.test.js
 *
 * Testen leser docs/index.html slik den er bygget, så bygg siden først:
 *
 *     python3 scripts/build_webplayer.py
 */
const fs = require('fs');
const { JSDOM } = require('jsdom');

const path = require('path');
const html = fs.readFileSync(path.join(__dirname, '..', 'docs', 'index.html'), 'utf8');

function lag({ ua, volumSettbar = true, lagringVirker = true }) {
  const dom = new JSDOM(`<!doctype html><html><body>${html}</body></html>`, {
    runScripts: 'outside-only', pretendToBeVisual: true,
  });
  const w = dom.window;
  // jsdom 30 respekterer ikke userAgent-opsjonen, så navigator overstyres her.
  Object.defineProperty(w.navigator, 'userAgent', {
    value: ua || 'Mozilla/5.0 (Macintosh) Chrome/140', configurable: true,
  });
  const butikk = {};
  Object.defineProperty(w, 'localStorage', { value: {
    getItem: k => (lagringVirker ? (k in butikk ? butikk[k] : null) : (() => { throw new Error('blokkert'); })()),
    setItem: (k, v) => { if (!lagringVirker) throw new Error('blokkert'); butikk[k] = String(v); },
  }});
  // Minimal Audio-stubb. volume speiler ekte nettlesere: skrivebeskyttet på iOS.
  w.Audio = class {
    constructor() { this._v = 1; this.src = ''; }
    get volume() { return this._v; }
    set volume(v) { if (volumSettbar) this._v = v; }
    play() { return Promise.resolve(); }
    pause() {} load() {} removeAttribute() {} addEventListener() {}
  };
  const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
  w.eval(js);
  return { w, d: w.document, butikk };
}

let feil = 0;
function sjekk(navn, faktisk, forventet) {
  const ok = JSON.stringify(faktisk) === JSON.stringify(forventet);
  if (!ok) feil++;
  console.log(`  ${ok ? 'OK  ' : 'FEIL'} ${navn}${ok ? '' : `\n         fikk ${JSON.stringify(faktisk)}, ventet ${JSON.stringify(forventet)}`}`);
}
const favIder = d => [...d.querySelectorAll('#fav-grid .row')].map(r => r.dataset.id);

console.log('\n== Favoritter');
{
  const { d, butikk } = lag({});
  sjekk('tom liste ved oppstart', favIder(d), []);
  sjekk('tomtekst vises', !d.getElementById('fav-empty').hidden, true);

  const stjerne = id => d.querySelector(`main > section:not(#favoritter) .row[data-id="${id}"] .fav`);
  stjerne('4').click();
  sjekk('NRK P3 lagt til', favIder(d), ['4']);
  sjekk('tomtekst skjult', d.getElementById('fav-empty').hidden, true);
  sjekk('lagret i localStorage', JSON.parse(butikk.favoritter), ['4']);

  stjerne('60').click();
  sjekk('P4 lagt til, rekkefølge bevart', favIder(d), ['4', '60']);

  // Begge kopiene av samme kanal skal vise fylt stjerne
  const alle = [...d.querySelectorAll('.row[data-id="4"] .fav')].map(b => b.getAttribute('aria-pressed'));
  sjekk('stjernen fylt på begge kopier', alle, ['true', 'true']);

  // Fjerning fra klonen i favorittseksjonen
  d.querySelector('#fav-grid .row[data-id="4"] .fav').click();
  sjekk('fjernet via klonen', favIder(d), ['60']);
  sjekk('stjernen tømt i hovedlista',
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .fav').getAttribute('aria-pressed'), 'false');
}

console.log('\n== Spilling og markering');
{
  const { d, butikk } = lag({});
  d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .fav').click();
  d.querySelector('#fav-grid .row[data-id="4"] .play').click();
  const merket = [...d.querySelectorAll('.row[data-id="4"]')].map(r => r.getAttribute('aria-current'));
  sjekk('begge kopier markert som spillende', merket, ['true', 'true']);
  sjekk('kanalnavn i toppen', d.getElementById('now-name').textContent, 'NRK P3');
  sjekk('sisteKanal lagret', butikk.sisteKanal, '4');
  sjekk('stoppknapp aktiv', d.getElementById('stop').disabled, false);

  d.getElementById('stop').click();
  sjekk('markering fjernet etter stopp',
    [...d.querySelectorAll('.row[data-id="4"]')].map(r => r.getAttribute('aria-current')), ['false', 'false']);
  sjekk('stoppknapp deaktivert', d.getElementById('stop').disabled, true);
}

console.log('\n== Volum');
{
  const { d } = lag({ ua: 'Mozilla/5.0 (Macintosh) Chrome/140' });
  sjekk('vises i vanlig nettleser', d.getElementById('vol-wrap').hidden, false);
  const vol = d.getElementById('vol');
  vol.value = '35';
  vol.dispatchEvent(new d.defaultView.Event('input'));
  sjekk('viser prosent', d.getElementById('vol-val').textContent, '35 %');
}
{
  const ua = 'Mozilla/5.0 (X11; GNU/Linux) Chromium/79.0.3945.130 Safari/537.36 Tesla/2020.48.35';
  const { d } = lag({ ua });
  sjekk('skjult i Tesla', d.getElementById('vol-wrap').hidden, true);
}
{
  const { d } = lag({ ua: 'Mozilla/5.0 (iPhone) Safari', volumSettbar: false });
  sjekk('skjult der volume er skrivebeskyttet (iOS)', d.getElementById('vol-wrap').hidden, true);
}
{
  const { d, butikk } = lag({});
  const vol = d.getElementById('vol');
  vol.value = '60';
  vol.dispatchEvent(new d.defaultView.Event('change'));
  sjekk('volum lagres ved change', butikk.volum, '60');
}

console.log('\n== Søk');
{
  const { d } = lag({});
  d.querySelector('main > section:not(#favoritter) .row[data-id="103"] .fav').click();
  const f = d.getElementById('filter');
  f.value = 'trøndelag';
  f.dispatchEvent(new d.defaultView.Event('input'));
  const synlige = [...d.querySelectorAll('main > section:not(#favoritter) .row')].filter(r => !r.hidden);
  sjekk('bare Trøndelag-treff igjen', synlige.every(r => r.dataset.search.includes('trøndelag')), true);
  sjekk('favoritten treffer også', favIder(d).filter(id => !d.querySelector(`#fav-grid .row[data-id="${id}"]`).hidden), ['103']);

  f.value = 'finnesikke';
  f.dispatchEvent(new d.defaultView.Event('input'));
  sjekk('favorittseksjon skjules uten treff', d.getElementById('favoritter').hidden, true);

  f.value = '';
  f.dispatchEvent(new d.defaultView.Event('input'));
  sjekk('alt tilbake etter tømt søk',
    [...d.querySelectorAll('main > section:not(#favoritter) .row')].filter(r => r.hidden).length, 0);
  sjekk('favorittseksjon synlig igjen', d.getElementById('favoritter').hidden, false);
}

console.log('\n== Uten localStorage (privat modus)');
{
  const { d } = lag({ lagringVirker: false });
  // Antallet endres med kanallista, så testen sjekker at siden har rader i det hele tatt.
  sjekk('siden laster med kanaler', d.querySelectorAll('.row').length > 50, true);
  d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .fav').click();
  sjekk('stjerneklikk kaster ikke', true, true);
  d.querySelector('.row[data-id="4"] .play').click();
  sjekk('spilling virker fortsatt', d.getElementById('now-name').textContent, 'NRK P3');
}

console.log(feil ? `\n${feil} FEIL` : '\nAlle tester bestått');
process.exit(feil ? 1 : 0);
