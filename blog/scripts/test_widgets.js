// Run from the repository root: node blog/scripts/test_widgets.js
// Checks the two home-page widgets (assets/ant-explainer.js, assets/walker-compare.js)
// against independent sparse oracles and the web simulator, then drives their controls in jsdom.
// Uses the simulator's pinned jsdom dependency: npm ci --prefix web.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('../../web/node_modules/jsdom');
const { Ant: SimAnt } = require('../../web/sim');
const explainer = require('../assets/ant-explainer');
const compare = require('../assets/walker-compare');
const read = file => fs.readFileSync(path.join(__dirname, file), 'utf8');

const DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];

// ---------- explainer: every step against web/sim.js ----------
assert.equal(explainer.parseRule(' rl '), 'RL');
assert.equal(explainer.parseRule('R'), null);
assert.equal(explainer.parseRule('RLX'), null);
assert.equal(explainer.parseRule('R'.repeat(13)), null);
for (const rule of ['RL', 'LLRR', 'RLR', 'RLLLLLRRL', 'RRLRLLRRRLR']) {
  const ant = new explainer.Ant(rule), oracle = new SimAnt(rule, 2048);
  for (let i = 1; i <= 5000; i++) {
    const colourBefore = ant.colourAt(ant.x, ant.y), headingBefore = ant.heading;
    const step = ant.step();
    oracle.run(1);
    assert.deepEqual([step.colour, step.before, step.turn], [colourBefore, headingBefore, rule[colourBefore]]);
    assert.equal(step.painted, (colourBefore + 1) % rule.length);
    assert.equal(step.after, ant.heading);
    assert.deepEqual([ant.x, ant.y, ant.heading, ant.steps], [oracle.x - 1024, oracle.y - 1024, oracle.h, i]);
  }
  for (const [key, colour] of ant.cells) {
    const x = key % 65536 - 32768, y = Math.floor(key / 65536) - 32768;
    assert.equal(oracle.cells[(y + 1024) * 2048 + x + 1024], colour);
  }
}
{
  const capped = new explainer.Ant('RL');
  capped.run(explainer.MAX_STEPS + 50);
  assert.equal(capped.steps, explainer.MAX_STEPS, 'runs stop at the cap');
}
assert.equal(explainer.describe({ colour: 0, turn: 'R', before: 0, after: 1, painted: 1 }).length, 4);
assert.equal(explainer.colourCss(0, 4, false), null);
assert.equal(new Set([1, 2, 3].map(c => explainer.colourCss(c, 4, false))).size, 3);

// ---------- walkers: each against a plain Map-based oracle ----------
function oracleRun(kind, options, steps) {
  const cells = new Map(), key = (x, y) => `${x},${y}`, visited = new Set([key(0, 0)]);
  const random = compare.rng(options.seed * 7919 + (kind === 'persistent' ? 1 : 0));
  let x = 0, y = 0, h = 0, moment = 0, extent = 0;
  const path = [[0, 0]];
  for (let i = 0; i < steps; i++) {
    const k = key(x, y);
    if (kind === 'ant') {
      const c = cells.get(k) || 0;
      h = (h + (options.rule[c] === 'R' ? 1 : 3)) & 3;
      cells.set(k, (c + 1) % options.rule.length);
    } else if (kind === 'rotor') {
      const arrow = ((cells.has(k) ? cells.get(k) : compare.initialArrow(options.seed, x, y)) + 1) & 3;
      cells.set(k, arrow);
      h = arrow;
    } else if (kind === 'randomwalk') h = (random() * 4) | 0;
    else h = (h + (random() < 0.5 ? 1 : 3)) & 3;
    x += DX[h]; y += DY[h];
    extent = Math.max(extent, Math.abs(x), Math.abs(y));
    if (!visited.has(key(x, y))) { visited.add(key(x, y)); moment += x * x + y * y; }
    path.push([x, y]);
  }
  return { x, y, h, area: visited.size, extent, spread: Math.sqrt(moment / visited.size), path };
}
for (const [kind, options] of [['ant', { rule: 'RLL' }], ['ant', { rule: 'LLRR' }], ['rotor', { seed: 3 }],
  ['randomwalk', { seed: 5 }], ['persistent', { seed: 7 }]]) {
  const steps = 60000, w = new compare.Walker(kind, options);
  // Odd chunk sizes exercise stopping and resuming around zoom changes.
  const race = new compare.Race('RL', 1);
  race.walkers = [w];
  for (let done = 0; done < steps; done += 977) race.advance(Math.min(977, steps - done));
  const o = oracleRun(kind, { seed: 1, rule: options.rule, ...options }, steps);
  assert.deepEqual([w.x, w.y, w.heading, w.steps, w.area, w.extent], [o.x, o.y, o.h, steps, o.area, o.extent], `${kind} state`);
  assert.ok(Math.abs(w.spread - o.spread) < 1e-9 * o.spread, `${kind} spread`);
  // The picture is the oracle's path binned at the final zoom, so zooming out lost nothing.
  const view = new Uint32Array(compare.VIEW ** 2);
  for (const [x, y] of o.path) view[((y >> w.k) + 128) * compare.VIEW + (x >> w.k) + 128]++;
  assert.deepEqual(w.view, view, `${kind} picture at zoom ${w.k}`);
  if (kind.endsWith('walk') || kind === 'persistent') assert.ok(w.k > 0, `${kind} should have needed to zoom out`);
}

// ---------- rotor arrows, races, seeds ----------
{
  const counts = [0, 0, 0, 0];
  for (let x = -100; x < 100; x++) for (let y = -100; y < 100; y++) counts[compare.initialArrow(9, x, y)]++;
  assert.ok(counts.every(c => Math.abs(c - 10000) < 400), `initial arrows are close to uniform: ${counts}`);
}
{
  const a = new compare.Race('RLL', 1), b = new compare.Race('RLL', 1), c = new compare.Race('RLL', 2);
  for (const r of [a, b, c]) r.advance(30000);
  a.walkers.forEach((w, i) => assert.deepEqual(w.view, b.walkers[i].view, 'same seed, same picture'));
  // (Pictures share one zoom, so compare the ant's state, not its binned picture.)
  const state = w => [w.x, w.y, w.heading, w.area, w.extent, w.spread];
  assert.deepEqual(state(a.walkers[0]), state(c.walkers[0]), 'the ant ignores the seed');
  for (const i of [1, 2, 3]) assert.notDeepEqual(a.walkers[i].view, c.walkers[i].view, `walker ${i} depends on the seed`);
  const fast = new compare.Race('RLL', 1), slow = new compare.Race('RLL', 1);
  fast.advance(30000);
  for (let i = 0; i < 300; i++) slow.advance(100);
  fast.walkers.forEach((w, i) => assert.deepEqual(w.view, slow.walkers[i].view, 'chunking does not change the result'));
  const highway = new compare.Race('RL', 1);
  highway.advance(compare.MAX_STEPS);
  assert.match(highway.walkers[0].stopped, /edge of the board/, 'Langton’s ant runs off the board');
  assert.ok(highway.walkers[0].steps < compare.MAX_STEPS);
  assert.equal(highway.walkers[1].steps, compare.MAX_STEPS, 'others carry on');
  assert.equal(highway.steps, compare.MAX_STEPS);
  assert.ok(highway.done);
  // Fitted pictures zoom independently but lose no visits.
  const fitted = new compare.Race('RLL', 1, false);
  fitted.advance(100000);
  assert.ok(fitted.walkers[0].k < fitted.walkers[2].k, 'the ant needs less zoom than the random walk');
  for (const w of fitted.walkers) assert.equal(w.view.reduce((a, b) => a + b, 0), w.steps + 1);
  // Blob-forming ants and the rotor grow far more slowly than random walks.
  const blob = new compare.Race('RLL', 1);
  blob.advance(compare.MAX_STEPS);
  const [ant, rotor, walk, persistent] = blob.walkers;
  const slope = w => Math.log(w.spread / w.samples.spread[Math.floor(w.samples.t.findIndex(t => t >= 2 ** 12))]) / Math.log(w.steps / 2 ** 12);
  assert.ok(Math.abs(slope(ant) - 1 / 3) < 0.05, `ant slope ${slope(ant)}`);
  assert.ok(Math.abs(slope(rotor) - 1 / 3) < 0.05, `rotor slope ${slope(rotor)}`);
  assert.ok(walk.spread > 3 * ant.spread && persistent.spread > 3 * ant.spread);
}

// ---------- controls, in jsdom ----------
function load(reduced) {
  const html = read('../index.html');
  const dom = new JSDOM(html, { runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window, d = w.document;
  const frames = new Map();
  let nextId = 0, now = 0, observer;
  w.matchMedia = query => ({ matches: query.includes('reduced-motion') && reduced, addEventListener() {} });
  const context = new Proxy({}, {
    get: (target, name) => (name in target ? target[name]
      : name === 'createImageData' ? (width, height) => ({ data: new Uint8ClampedArray(width * height * 4) })
      : name === 'measureText' ? () => ({ width: 0 }) : () => {}),
    set: (target, name, value) => { target[name] = value; return true; },
  });
  w.HTMLCanvasElement.prototype.getContext = () => context;
  w.requestAnimationFrame = cb => { frames.set(++nextId, cb); return nextId; };
  w.cancelAnimationFrame = id => frames.delete(id);
  w.IntersectionObserver = class { constructor(cb) { observer = cb; } observe() {} };
  const advance = () => {
    const callbacks = [...frames.values()];
    frames.clear(); now += 100;
    callbacks.forEach(cb => cb(now));
  };
  w.eval(read('../assets/ant-explainer.js'));
  w.eval(read('../assets/walker-compare.js'));
  return { dom, w, d, frames, advance, visible: on => observer([{ isIntersecting: on }]) };
}
function checkExplainer(reduced) {
  const { dom, d, advance, frames } = load(reduced);
  const $ = s => d.querySelector(s), steps = () => Number($('#ex-steps').textContent.replace(/[^0-9]/g, ''));
  assert.equal($('.ant-explainer').hidden, false);
  assert.equal(steps(), 0);
  assert.equal($('#ex-back').disabled, true);
  assert.equal(d.querySelectorAll('#ex-table tbody tr').length, 2);
  assert.equal(d.querySelectorAll('#ex-table tr.ex-now').length, 1, 'next row is highlighted');
  $('#ex-step').click();
  assert.equal(steps(), 1);
  assert.equal(d.querySelectorAll('#ex-narration li').length, 4, 'a step is narrated as read, turn, paint, move');
  assert.equal($('#ex-back').disabled, false);
  $('[data-skip="100"]').click();
  assert.equal(steps(), 101);
  $('#ex-back').click();
  assert.equal(steps(), 100);
  // Back must land exactly where stepping 100 times lands.
  const forward = new explainer.Ant('RL'); forward.run(100);
  assert.match($('#ex-summary').textContent, new RegExp(`facing ${['north', 'east', 'south', 'west'][forward.heading]}`));
  $('#ex-play').click();
  assert.equal($('#ex-play').getAttribute('aria-pressed'), 'true');
  advance(); advance();
  assert.ok(steps() > 100, 'play advances');
  $('#ex-play').click();
  const stopped = steps();
  advance();
  assert.equal(steps(), stopped, 'pause stops');
  assert.equal(frames.size, 0);
  // Flipping a table entry changes the rule and restarts.
  $('.ex-turn[data-index="0"]').click();
  assert.equal($('#ex-rule').value, 'LL');
  assert.equal(steps(), 0);
  $('#ex-rule').value = 'rlr';
  $('#ex-rule-form').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.equal($('#ex-rule').value, 'RLR');
  assert.equal(d.querySelectorAll('#ex-table tbody tr').length, 3);
  $('#ex-rule').value = 'RLQ';
  $('#ex-rule-form').dispatchEvent(new dom.window.Event('submit', { cancelable: true }));
  assert.match($('#ex-rule-error').textContent, /L or R/);
  assert.equal($('#ex-rule').value, 'RLQ', 'a bad rule does not replace the working one');
  $('.ex-preset[data-rule="LLRR"]').click();
  assert.equal(d.querySelectorAll('#ex-table tbody tr').length, 4);
  assert.equal($('.ex-preset[data-rule="LLRR"]').getAttribute('aria-pressed'), 'true');
  $('[data-skip="1000"]').click();
  $('#ex-reset').click();
  assert.equal(steps(), 0);
  dom.window.close();
}
function checkCompare(reduced) {
  const { dom, d, advance, visible, frames } = load(reduced);
  const $ = s => d.querySelector(s), steps = () => Number($('#wc-steps').textContent.replace(/[^0-9]/g, ''));
  assert.equal($('.walker-compare').hidden, false);
  assert.equal(steps(), 4096, 'a still preview is drawn at once');
  assert.equal($('#wc-play').getAttribute('aria-pressed'), String(!reduced));
  visible(true);
  if (reduced) { assert.equal(frames.size, 0); $('#wc-play').click(); }
  advance(); advance();
  assert.ok(steps() > 4096, 'running');
  visible(false);
  assert.equal(frames.size, 0, 'offscreen walkers stop scheduling frames');
  visible(true);
  $('#wc-play').click();
  assert.equal($('#wc-play').getAttribute('aria-pressed'), 'false');
  const before = steps();
  advance();
  assert.equal(steps(), before, 'pause stops');
  $('[data-skip="100000"]').click();
  assert.equal(steps(), 100000);
  $('[data-skip="10000"]').click();
  assert.equal(steps(), 100000, 'skipping never goes backwards');
  $('#wc-reseed').click();
  assert.equal($('#wc-seed').textContent, 'seed 2');
  assert.equal(steps(), 4096);
  $('#wc-rule').value = 'LLRR';
  $('#wc-rule').dispatchEvent(new dom.window.Event('change'));
  assert.equal(steps(), 4096);
  assert.match(d.querySelector('.wc-panel canvas').getAttribute('aria-label'), /^Ant LLRR after 4096 steps/);
  $('[data-skip="1048576"]').click();
  assert.match($('#wc-summary').textContent, /same scale/);
  $('#wc-scale').value = 'fit';
  $('#wc-scale').dispatchEvent(new dom.window.Event('change'));
  $('[data-skip="10000"]').click();
  assert.match($('#wc-summary').textContent, /fit its own walker/);
  assert.equal($('.wc-stats').textContent.includes('sites'), true);
  dom.window.close();
}
checkExplainer(false);
checkExplainer(true);
checkCompare(false);
checkCompare(true);
console.log('PASS: explainer vs web simulator, four walkers vs sparse oracles incl. zoom, chunk independence, seeds, board edge, exponents, controls, reduced motion');
