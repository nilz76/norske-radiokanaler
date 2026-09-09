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

function lag({ ua, volumSettbar = true, lagringVirker = true, touch = 0, lagret = {} }) {
  const dom = new JSDOM(`<!doctype html><html><body>${html}</body></html>`, {
    runScripts: 'outside-only', pretendToBeVisual: true,
  });
  const w = dom.window;
  // jsdom 30 respekterer ikke userAgent-opsjonen, så navigator overstyres her.
  Object.defineProperty(w.navigator, 'userAgent', {
    value: ua || 'Mozilla/5.0 (Macintosh) Chrome/140', configurable: true,
  });
  Object.defineProperty(w.navigator, 'maxTouchPoints', { value: touch, configurable: true });
  const butikk = Object.assign({}, lagret);
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
// Nettleserstrenger observert i praksis. MCU2 oppgir ikke alltid «Tesla».
const UA_MAC = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/140 Safari/537.36';
const UA_TESLA_MERKET = 'Mozilla/5.0 (X11; GNU/Linux) Chromium/79.0.3945.130 Safari/537.36 Tesla/2020.48.35';
const UA_TESLA_UMERKET = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36';
const UA_IPHONE = 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) Safari/604.1';

{
  const { d } = lag({ ua: UA_MAC });
  sjekk('vises på Mac', d.getElementById('vol-wrap').hidden, false);
  sjekk('bryter tilgjengelig', d.getElementById('vol-toggle').hidden, false);
  const vol = d.getElementById('vol');
  vol.value = '35';
  vol.dispatchEvent(new d.defaultView.Event('input'));
  sjekk('viser prosent', d.getElementById('vol-val').textContent, '35 %');
}
{
  const { d } = lag({ ua: UA_TESLA_MERKET, touch: 10 });
  sjekk('skjult i Tesla (merket UA)', d.getElementById('vol-wrap').hidden, true);
}
{
  // Dette er tilfellet som feilet i bilen: ingen «Tesla» i strengen.
  const { d } = lag({ ua: UA_TESLA_UMERKET, touch: 10 });
  sjekk('skjult i Tesla (umerket UA, Linux + touch)', d.getElementById('vol-wrap').hidden, true);
}
{
  const { d } = lag({ ua: UA_TESLA_UMERKET, touch: 0 });
  sjekk('Linux uten touch regnes som skrivebord', d.getElementById('vol-wrap').hidden, false);
}
{
  const { d } = lag({ ua: UA_IPHONE, volumSettbar: false, touch: 5 });
  sjekk('skjult på iOS', d.getElementById('vol-wrap').hidden, true);
  sjekk('bryter skjult når volum ikke kan settes', d.getElementById('vol-toggle').hidden, true);
}

console.log('\n== Volum: brukerens valg overstyrer');
{
  // Bilen gjetter feil -> ett trykk skal skjule det, og huskes.
  const { d, butikk } = lag({ ua: UA_MAC });
  sjekk('synlig i utgangspunktet', d.getElementById('vol-wrap').hidden, false);
  d.getElementById('vol-toggle').click();
  sjekk('skjult etter trykk', d.getElementById('vol-wrap').hidden, true);
  sjekk('valget lagret', butikk.visVolum, 'nei');
  sjekk('bryterteksten oppdatert', d.getElementById('vol-toggle').textContent, 'Vis volumkontroll');
}
{
  const { d } = lag({ ua: UA_MAC, lagret: { visVolum: 'nei' } });
  sjekk('valget huskes ved ny åpning', d.getElementById('vol-wrap').hidden, true);
}
{
  // Motsatt vei: vil man ha det i bilen likevel, skal det være mulig.
  const { d, butikk } = lag({ ua: UA_TESLA_UMERKET, touch: 10 });
  sjekk('skjult som standard i bil', d.getElementById('vol-wrap').hidden, true);
  d.getElementById('vol-toggle').click();
  sjekk('kan slås på i bil', d.getElementById('vol-wrap').hidden, false);
  sjekk('valget lagret', butikk.visVolum, 'ja');
}
{
  const { d } = lag({ ua: UA_TESLA_UMERKET, touch: 10, lagret: { visVolum: 'ja' } });
  sjekk('påslått valg huskes i bil', d.getElementById('vol-wrap').hidden, false);
}
{
  const { d, butikk } = lag({ ua: UA_MAC });
  const vol = d.getElementById('vol');
  vol.value = '60';
  vol.dispatchEvent(new d.defaultView.Event('change'));
  sjekk('volumnivå lagres', butikk.volum, '60');
}

console.log('\n== Nettleserstreng vises');
{
  const { d } = lag({ ua: UA_TESLA_UMERKET, touch: 10 });
  sjekk('UA skrevet ut på siden', d.getElementById('ua').textContent, UA_TESLA_UMERKET);
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
