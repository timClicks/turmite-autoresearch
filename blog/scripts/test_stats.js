// Run from the repository root: node blog/scripts/test_stats.js
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const { JSDOM } = require('../../web/node_modules/jsdom');
const { slope, uniform, summarize } = require('../assets/stats');
const root = path.resolve(__dirname, '../..');
const data = JSON.parse(fs.readFileSync(path.join(root, 'blog/_data/noisy_rotor.json')));
const near = (a, b, tolerance = 1e-10) => assert.ok(Math.abs(a - b) <= tolerance, `${a} != ${b}`);

// Known mathematical controls and the removable singularity of the reference.
near(slope([0, 1, 2], [3, 5, 7]), 2);
near(uniform(0, 0.5), 1);
near(uniform(1, 0), 2 * Math.LN2);
near(uniform(1 + 1e-12, 0), 2 * Math.LN2);
const synthetic = { runs: [{ eps: 0, escaped: false, windows: [12, 13, 14].map(k => {
  const t = 2 ** k, area = t ** (2 / 3), perimeter = Math.sqrt(area);
  return [k, t, area, perimeter, t / 2 * perimeter / area * uniform(2 / 3, 0.5)];
}) }] };
near(summarize(synthetic, 12, 14)[0].ratio, 1);
assert.equal(summarize(synthetic, 12, 15)[0].n, 0);
assert.equal(summarize(synthetic, 12, 14)[0].sd, null);
assert.throws(() => summarize(synthetic, 14, 14));

for (const [input, hash] of Object.entries(data.inputs)) {
  assert.equal(crypto.createHash('sha256').update(fs.readFileSync(path.join(root, input))).digest('hex'), hash);
}
// Independent oracle: all published, numpy-computed rows, including missing runs,
// sample sd, and stationarity counts. Published text is rounded to three decimals.
const analysis = fs.readFileSync(path.join(root, 'experiments/archive/2026-10-kappa-walker-reference/results/analysis_nrotor.txt'), 'utf8');
let rows, checked = 0;
for (const line of analysis.split('\n')) {
  const window = line.match(/^== windows k=(\d+)\.\.(\d+)/);
  if (window) rows = summarize(data, +window[1], +window[2]);
  if (!/^\s*\d+\.\d+\s/.test(line)) continue;
  const values = line.trim().split(/\s+/), row = rows.find(r => r.eps === +values[0]);
  if (line.includes('no usable')) { assert.equal(row.n, 0); checked++; continue; }
  assert.equal(row.n, +values[1]); assert.equal(row.escaped, +values[2]);
  near(row.a, +values[3], 0.000501);
  near(row.ratio, +values[10], 0.000501);
  if (row.sd !== null) near(row.sd, parseFloat(values[11].slice(1)), 0.000501);
  assert.equal(row.stationary, +values[14]); checked++;
}
assert.equal(checked, 27);

// Exercise the actual include markup and browser script, with two independent instances.
const markup = fs.readFileSync(path.join(root, 'blog/_includes/stats-explorer.html'), 'utf8')
  .replace(/\{%[\s\S]*?%\}/g, '').replace('{{ stats | jsonify }}', JSON.stringify(data));
const dom = new JSDOM(markup + markup, { runScripts: 'outside-only' });
dom.window.eval(fs.readFileSync(path.join(root, 'blog/assets/stats.js'), 'utf8'));
const panels = dom.window.document.querySelectorAll('[data-stats-explorer]');
const panel = panels[0];
const set = (key, value) => {
  const input = panel.querySelector(`[data-control="${key}"]`);
  input.value = value; input.dispatchEvent(new dom.window.Event('input'));
};
assert.equal(panel.querySelector('[data-live]').hidden, false);
assert.equal(panel.querySelector('[data-fallback]').hidden, true);
assert.match(panel.querySelector('.stats-summary').textContent, /2\.588/);
set('lo', 20); set('hi', 26); set('eps', 8);
assert.match(panel.querySelector('.stats-summary').textContent, /No seed/);
assert.match(panel.querySelector('.stats-warning').textContent, /selected subset/);
assert.equal(panel.querySelectorAll('tbody tr').length, 9);
set('eps', 3);
assert.match(panel.querySelector('.stats-summary').textContent, /sd unavailable/);
set('lo', 25); set('hi', 13);
assert.equal(panel.querySelector('[data-control="lo"]').value, '12');
set('lo', 25);
assert.equal(panel.querySelector('[data-control="hi"]').value, '26');
panel.querySelector('[data-reset]').click();
assert.match(panel.querySelector('.stats-summary').textContent, /2\.588/);
assert.equal(panels[1].querySelector('[data-control="lo"]').value, '12');
assert.doesNotMatch(panel.querySelector('svg').outerHTML, /NaN|Infinity/);
dom.window.close();
console.log('Statistics: synthetic controls, 27 published rows, input hashes, slider bounds, missing data, reset and independent instances passed.');
