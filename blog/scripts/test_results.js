// Run after Jekyll build: node blog/scripts/test_results.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { JSDOM } = require('../../web/node_modules/jsdom');
const { init, sweeperLabel } = require('../assets/results');
const root = path.resolve(__dirname, '../..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'blog/_data/preliminary_results.json')));
const html = fs.readFileSync(path.join(root, 'blog/_site/index.html'), 'utf8');
const dom = new JSDOM(html);
const d = dom.window.document;
assert.deepEqual(JSON.parse(d.getElementById('preliminary-data').textContent), data, 'Rebuild Jekyll after exporting data');
const cards = [...d.querySelectorAll('[data-paper-result]')];
assert.equal(cards.length, 9);
assert.deepEqual(cards.map(c => c.querySelector('h3').textContent), data.titles);
assert.equal(new Set([...d.querySelectorAll('[id]')].map(el => el.id)).size, d.querySelectorAll('[id]').length);
for (const card of cards) {
  assert.ok(card.querySelector('details summary'));
  assert.match(card.querySelector('.text-link').getAttribute('href'), /\/experiments\//);
}
// Useful content is present before JavaScript; controls progressively enhance it.
assert.equal(d.getElementById('width-time').textContent, '8');
assert.ok(d.getElementById('occupation-toggle').hidden);
assert.equal(d.getElementById('occupation-ant').textContent, '0.81×');
init(d);
assert.equal(d.querySelectorAll('.result-controls[hidden], .result-toggle[hidden]').length, 0);
function slide(id, value) {
  const el = d.getElementById(id); el.value = String(value);
  el.dispatchEvent(new dom.window.Event('input', { bubbles: true }));
}
slide('width-factor', 1); assert.equal(d.getElementById('width-time').textContent, '1');
slide('width-factor', 4); assert.equal(d.getElementById('width-time').textContent, '64');
slide('width-factor', 2); assert.equal(d.getElementById('width-time').textContent, '8');
for (const m of [1, 3, 6]) {
  slide('lead-length', m);
  assert.equal(d.getElementById('lead-rule').textContent, `${'R'.repeat(m)}L…`);
  assert.ok(d.getElementById('lead-prediction').textContent.includes((data.law.a + data.law.b * m).toFixed(2)));
}
const toggle = d.getElementById('occupation-toggle');
toggle.click(); assert.equal(toggle.getAttribute('aria-pressed'), 'false');
assert.equal(d.getElementById('occupation-ant').textContent, data.ant_raw.toFixed(2));
assert.equal(d.getElementById('occupation-1').textContent, data.walkers[1].raw.toFixed(2));
toggle.click(); assert.equal(toggle.getAttribute('aria-pressed'), 'true');
assert.equal(d.getElementById('occupation-ant').textContent, '0.81×');
for (const [source, digest] of Object.entries(data.provenance.sha256)) {
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, source))).digest('hex'), digest, source);
}
for (const image of d.querySelectorAll('.result-image img')) {
  assert.ok(image.alt.length > 30);
  const rel = new URL(image.getAttribute('src'), 'https://example.test').pathname.replace(/^\/turmite-autoresearch/, '');
  assert.ok(fs.existsSync(path.join(root, 'blog/_site', rel)));
}
// Card 09: the static map and caption stand alone; the slider appears only once a browser draws the canvas.
const sw = data.sweeper, last = sw.t.length - 1;
assert.equal(sw.visited.length, sw.t.length); assert.equal(sw.colours.length, sw.t.length);
assert.ok(sw.t.every((t, i) => i === 0 || t > sw.t[i - 1]));
assert.ok(d.getElementById('sweeper-canvas').hidden && !d.getElementById('sweeper-fallback').hidden);
assert.ok(d.querySelector('.sweeper-controls').hidden, 'jsdom has no createImageBitmap, so the slider stays hidden');
assert.equal(d.getElementById('sweeper-frame').getAttribute('max'), String(last));
assert.equal(d.getElementById('sweeper-frame').getAttribute('value'), String(last));
assert.equal(sweeperLabel(sw, 0), 'Step 0.50 billion · still a blob · ' + (sw.visited[0] / 1e6).toFixed(1) + ' million cells visited');
assert.match(sweeperLabel(sw, last), /^Step 12\.97 billion · sweeping for 0\.30 billion steps · 83\.7 million cells visited$/);
assert.match(sweeperLabel(sw, sw.t.findIndex(t => t > sw.switch_t)), /sweeping for 3\.6 million steps/);
console.log('Nine paper findings, source hashes, no-JS content and interactive controls pass.');
