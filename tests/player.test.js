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

function lag({ ua, volumSettbar = true, lagringVirker = true, touch = 0, lagret = {},
              mediaSession = false, playAvvises = null }) {
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
  // Audio-stubb som ekte EventTarget, slik at sidens hendelseslyttere fyres.
  // volume speiler nettlesere: skrivebeskyttet på iOS.
  w.__lyd = [];
  w.Audio = class extends w.EventTarget {
    constructor() {
      super();
      this._v = 1; this._src = ''; this.paused = true; this.srcLogg = [];
      w.__lyd.push(this);
    }
    get volume() { return this._v; }
    set volume(v) { if (volumSettbar) this._v = v; }
    get src() { return this._src; }
    set src(v) { this._src = v; this.srcLogg.push(v); }
    play() {
      if (playAvvises) { return Promise.reject(playAvvises); }
      this.paused = false;
      const p = Promise.resolve();
      p.then(() => this.dispatchEvent(new w.Event('playing')));
      return p;
    }
    pause() { this.paused = true; }
    load() {}
    removeAttribute() { this._src = ''; }
  };
  // Media Session-stubb. Registreres før skriptet kjøres, slik at siden ser den.
  const handlinger = {};
  if (mediaSession) {
    w.navigator.mediaSession = {
      metadata: null, playbackState: '',
      setActionHandler: (n, f) => { handlinger[n] = f; },
    };
    w.MediaMetadata = class { constructor(o) { Object.assign(this, o); } };
  }
  const js = html.match(/<script>([\s\S]*)<\/script>/)[1];
  w.eval(js);
  // Første Audio-instans er spillerens; den andre er volumprøven.
  return { w, d: w.document, butikk, lyd: w.__lyd[0], handlinger };
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
}

console.log('\n== Volum: nivået huskes');
{
  const { d, butikk } = lag({ ua: UA_MAC });
  const vol = d.getElementById('vol');
  vol.value = '60';
  vol.dispatchEvent(new d.defaultView.Event('change'));
  sjekk('volumnivå lagres', butikk.volum, '60');
}
{
  const { d } = lag({ ua: UA_MAC, lagret: { volum: '45' } });
  sjekk('lagret nivå brukes ved åpning', d.getElementById('vol-val').textContent, '45 %');
}

console.log('\n== Kompakt topp');
{
  const { d } = lag({ ua: UA_MAC });
  const header = d.querySelector('header');
  sjekk('ingen h1 i toppen', header.querySelector('h1'), null);
  sjekk('ingen undertekst', header.querySelector('.sub'), null);
  sjekk('ingen volumbryter', d.getElementById('vol-toggle'), null);
  // Direkte barn av header = antall elementer som kan bli egne rader.
  sjekk('fire elementer i toppen', header.children.length, 4);
  sjekk('kanaltallet flyttet til søkefeltet',
    /Søk blant \d+ kanaler/.test(d.getElementById('filter').placeholder), true);
  sjekk('navnet kuttes ikke over flere linjer',
    /#now-name[^}]*white-space:\s*nowrap/.test(d.querySelector('style').textContent), true);
}

console.log('\n== Nettleserstreng vises');
{
  const { d } = lag({ ua: UA_TESLA_UMERKET, touch: 10 });
  sjekk('UA skrevet ut på siden', d.getElementById('ua').textContent, UA_TESLA_UMERKET);
}

const sov = ms => new Promise(r => setTimeout(r, ms));

async function testGjenoppkobling() {
  console.log('\n== Gjenoppkobling ved brudd');
  {
    const { d, lyd } = lag({});
    const spill = id => d.querySelector(`main > section:not(#favoritter) .row[data-id="${id}"] .play`).click();
    spill('4');
    await sov(10);
    sjekk('koblet til én gang', lyd.srcLogg.length, 1);

    lyd.dispatchEvent(new d.defaultView.Event('error'));
    sjekk('varsler om brudd og nytt forsøk',
      /prøver igjen om \d+ s/.test(d.getElementById('now-meta').textContent), true);

    await sov(1300);
    sjekk('koblet til på nytt av seg selv', lyd.srcLogg.length, 2);
    sjekk('samme kanal', lyd.srcLogg[1], lyd.srcLogg[0]);
  }
  {
    // Pausen skal øke når forsøkene fortsetter å feile, slik at vi ikke hamrer
    // på en server som er nede.
    const { d, lyd } = lag({ playAvvises: new Error('nede') });
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(20);
    const forste = d.getElementById('now-meta').textContent;
    await sov(1300);
    const andre = d.getElementById('now-meta').textContent;
    sjekk('pausen dobles ved gjentatt feil',
      [forste.includes('1 s'), andre.includes('2 s'), lyd.srcLogg.length], [true, true, 2]);
  }
  {
    // Lykkes gjenoppkoblingen, skal pausen nullstilles.
    const { d, lyd } = lag({});
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(10);
    lyd.dispatchEvent(new d.defaultView.Event('error'));
    await sov(1300);
    lyd.dispatchEvent(new d.defaultView.Event('error'));
    sjekk('pausen nullstilles etter et vellykket forsøk',
      d.getElementById('now-meta').textContent.includes('1 s'), true);
  }
  {
    // Brukeren stopper: da skal ingen gjenoppkobling skje.
    const { d, lyd } = lag({});
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(10);
    d.getElementById('stop').click();
    const etterStopp = lyd.srcLogg.length;
    lyd.dispatchEvent(new d.defaultView.Event('error'));
    await sov(1300);
    sjekk('ingen gjenoppkobling etter at brukeren stoppet', lyd.srcLogg.length, etterStopp);
  }
  {
    // Nettet tilbake: prøv straks, ikke vent ut pausen.
    const { w, d, lyd } = lag({});
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(10);
    lyd.paused = true;
    w.dispatchEvent(new w.Event('offline'));
    sjekk('melder om manglende nettverk', d.getElementById('now-meta').textContent, 'ingen nettverk');
    w.dispatchEvent(new w.Event('online'));
    sjekk('kobler til straks nettet er tilbake', lyd.srcLogg.length, 2);
  }
  {
    // Manglende brukertrykk kan ikke løses med nye forsøk.
    const feil = new Error('blokkert'); feil.name = 'NotAllowedError';
    const { d, lyd } = lag({ playAvvises: feil });
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(1300);
    sjekk('NotAllowedError gir ikke nye forsøk', lyd.srcLogg.length, 1);
    sjekk('ber brukeren trykke', d.getElementById('now-meta').textContent, 'trykk for å spille');
  }
  {
    const { d, lyd } = lag({});
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    await sov(10);
    lyd.dispatchEvent(new d.defaultView.Event('stalled'));
    sjekk('stalled vises uten å rive ned straks',
      d.getElementById('now-meta').textContent, 'strømmen stopper opp …');
  }
}

function testMediaSession() {
  console.log('\n== Media Session');
  {
    const { d, handlinger } = lag({ mediaSession: true });
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    const ms = d.defaultView.navigator.mediaSession;
    sjekk('kanalnavn til systemet', ms.metadata.title, 'NRK P3');
    sjekk('kringkaster som artist', ms.metadata.artist, 'NRK');
    sjekk('tilstand satt', ms.playbackState, 'playing');
    sjekk('handlinger registrert', Object.keys(handlinger).sort(),
      ['nexttrack', 'pause', 'play', 'previoustrack', 'stop']);

    handlinger.nexttrack();
    sjekk('neste kanal', d.getElementById('now-name').textContent, 'NRK P3 Musikk');
    handlinger.previoustrack();
    sjekk('forrige kanal', d.getElementById('now-name').textContent, 'NRK P3');
    handlinger.pause();
    sjekk('pause stopper', d.getElementById('now-name').textContent, 'Ingen kanal');
    sjekk('tilstand nullstilt', ms.playbackState, 'none');
  }
  {
    // Uten Media Session skal siden virke som før.
    const { d } = lag({ mediaSession: false });
    d.querySelector('main > section:not(#favoritter) .row[data-id="4"] .play').click();
    sjekk('spiller uten Media Session', d.getElementById('now-name').textContent, 'NRK P3');
  }
}

function testSortering() {
  console.log('\n== Rekkefølge i gruppene');
  const { d } = lag({});
  const navni = h2 => {
    const sek = [...d.querySelectorAll('main > section')].find(s => s.querySelector('h2') && s.querySelector('h2').textContent === h2);
    return [...sek.querySelectorAll('.row')].map(r => r.dataset.name);
  };
  const nrk = navni('NRK');
  sjekk('NRK beholder P1/P1+/P2-rekkefølgen', nrk.slice(0, 4),
    ['NRK P1', 'NRK P1+', 'NRK P2', 'NRK P3']);
  const innl = navni('Innlandet');
  sjekk('fylke er alfabetisk', innl, [...innl].sort((a, b) => a.toLowerCase() < b.toLowerCase() ? -1 : 1));
  const p4 = navni('P4-gruppen');
  sjekk('P4-gruppen beholder nummerrekkefølgen', p4.slice(0, 3), ['P4', 'P5 Hits', 'P5 Nonstop Hits']);
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

(async () => {
  await testGjenoppkobling();
  testMediaSession();
  testSortering();
  console.log(feil ? `\n${feil} FEIL` : '\nAlle tester bestått');
  process.exit(feil ? 1 : 0);
})();
