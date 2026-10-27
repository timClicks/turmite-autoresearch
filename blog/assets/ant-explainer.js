// "How an ant works": a step-through of one rule on a blank grid.
// Same convention as src/reference.rs, web/sim.js and ants.js: heading 0 = north,
// read the colour, turn by rule[colour], write colour + 1 (mod n), then move forward.
(() => {
  'use strict';
  const DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
  const HEADINGS = ['north', 'east', 'south', 'west'];
  const MAX_STEPS = 100000;
  const MAX_RULE = 12;

  function parseRule(text) {
    const rule = String(text).trim().toUpperCase();
    return /^[LR]{2,12}$/.test(rule) ? rule : null;
  }

  // Sparse, unbounded board. step() returns what happened so the page can narrate it.
  class Ant {
    constructor(rule) {
      this.rule = rule;
      this.cells = new Map();
      this.x = this.y = this.heading = this.steps = 0;
      this.minX = this.maxX = this.minY = this.maxY = 0;
    }
    static key(x, y) { return (y + 32768) * 65536 + (x + 32768); }
    colourAt(x, y) { return this.cells.get(Ant.key(x, y)) || 0; }
    step() {
      const { x, y } = this, colour = this.colourAt(x, y), before = this.heading;
      const turn = this.rule[colour];
      this.heading = (before + (turn === 'R' ? 1 : 3)) & 3;
      const painted = (colour + 1) % this.rule.length;
      this.cells.set(Ant.key(x, y), painted);
      this.x += DX[this.heading];
      this.y += DY[this.heading];
      this.minX = Math.min(this.minX, this.x); this.maxX = Math.max(this.maxX, this.x);
      this.minY = Math.min(this.minY, this.y); this.maxY = Math.max(this.maxY, this.y);
      this.steps++;
      return { x, y, colour, turn, before, after: this.heading, painted };
    }
    run(count) {
      let last = null;
      for (let i = 0; i < count && this.steps < MAX_STEPS; i++) last = this.step();
      return last;
    }
  }

  // Colour 0 is the blank board. Others are spread around the hue wheel; the page
  // also prints each colour's number, so colour is never the only cue.
  function colourCss(index, count, dark) {
    if (index === 0) return null;
    const hue = Math.round((14 + (index - 1) * (360 / Math.max(1, count - 1))) % 360);
    return dark ? `hsl(${hue} 50% 66%)` : `hsl(${hue} 52% 46%)`;
  }

  function describe(step) {
    const facing = HEADINGS[step.before], now = HEADINGS[step.after];
    const turn = step.turn === 'R' ? 'right' : 'left';
    return [
      `Read: the square under the ant is colour ${step.colour}.`,
      `Turn: the rule gives ${step.turn} for colour ${step.colour}, so the ant turns ${turn} from facing ${facing} to facing ${now}.`,
      `Paint: the square becomes colour ${step.painted}${step.painted === 0 ? ' (blank again, because the colours wrap round)' : ''}.`,
      `Move: one square ${now}.`,
    ];
  }

  if (typeof module !== 'undefined') module.exports = { Ant, parseRule, colourCss, describe, MAX_STEPS };
  if (typeof document === 'undefined') return;
  const root = document.querySelector('.ant-explainer');
  if (!root) return;
  const canvas = root.querySelector('canvas');
  const context = canvas && canvas.getContext('2d');
  if (!context) return;

  const $ = selector => root.querySelector(selector);
  const ruleInput = $('#ex-rule'), ruleError = $('#ex-rule-error'), table = $('#ex-table tbody');
  const stepButton = $('#ex-step'), backButton = $('#ex-back'), playButton = $('#ex-play');
  const speed = $('#ex-speed'), speedLabel = $('#ex-speed-label'), counter = $('#ex-steps');
  const narration = $('#ex-narration'), summary = $('#ex-summary');
  const dark = matchMedia('(prefers-color-scheme: dark)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const SPEEDS = [1, 3, 10, 30, 100, 300, 1000, 3000];

  let ant = new Ant('RL'), last = null, playing = false, frame = null, previous = null, owed = 0;

  function theme() {
    const s = getComputedStyle(root), v = name => s.getPropertyValue(name).trim();
    return { panel: v('--panel'), ink: v('--ink'), line: v('--line'), muted: v('--muted') };
  }

  function buildTable() {
    const n = ant.rule.length, frag = document.createDocumentFragment();
    for (let c = 0; c < n; c++) {
      const row = document.createElement('tr');
      row.dataset.colour = c;
      const swatch = (index) => {
        const cell = document.createElement('td'), chip = document.createElement('span');
        chip.className = 'ex-chip' + (index === 0 ? ' ex-blank' : '');
        chip.textContent = index;
        const css = colourCss(index, n, dark.matches);
        if (css) chip.style.background = css;
        cell.appendChild(chip);
        return cell;
      };
      const turnCell = document.createElement('td'), toggle = document.createElement('button');
      toggle.type = 'button';
      toggle.className = 'ex-turn';
      toggle.dataset.index = c;
      const turn = ant.rule[c];
      toggle.textContent = turn === 'R' ? 'R · turn right' : 'L · turn left';
      toggle.setAttribute('aria-label', `Colour ${c}: turn ${turn === 'R' ? 'right' : 'left'}. Activate to flip.`);
      turnCell.appendChild(toggle);
      row.append(swatch(c), turnCell, swatch((c + 1) % n));
      frag.appendChild(row);
    }
    table.replaceChildren(frag);
  }

  function markCurrentRow() {
    const current = ant.colourAt(ant.x, ant.y);
    for (const row of table.rows) row.classList.toggle('ex-now', Number(row.dataset.colour) === current);
  }

  function draw() {
    const t = theme(), n = ant.rule.length, W = canvas.width, H = canvas.height;
    context.fillStyle = t.panel;
    context.fillRect(0, 0, W, H);
    // Show at least 15 squares across; zoom out as the pattern grows.
    const spanX = Math.max(15, ant.maxX - ant.minX + 5), spanY = Math.max(15, ant.maxY - ant.minY + 5);
    const size = Math.min(40, W / spanX, H / spanY);
    const left = W / 2 - ((ant.minX + ant.maxX + 1) / 2) * size;
    const top = H / 2 - ((ant.minY + ant.maxY + 1) / 2) * size;
    if (size >= 9) {
      context.strokeStyle = t.line;
      context.lineWidth = 1;
      context.beginPath();
      const first = Math.floor(-left / size), lastX = Math.ceil((W - left) / size);
      for (let gx = first; gx <= lastX; gx++) { const px = Math.round(left + gx * size) + .5; context.moveTo(px, 0); context.lineTo(px, H); }
      const firstY = Math.floor(-top / size), lastY = Math.ceil((H - top) / size);
      for (let gy = firstY; gy <= lastY; gy++) { const py = Math.round(top + gy * size) + .5; context.moveTo(0, py); context.lineTo(W, py); }
      context.stroke();
    }
    context.textAlign = 'center';
    context.textBaseline = 'middle';
    context.font = `${Math.floor(size * .5)}px ui-monospace, monospace`;
    for (const [key, colour] of ant.cells) {
      if (!colour) continue;
      const cx = key % 65536 - 32768, cy = Math.floor(key / 65536) - 32768;
      context.fillStyle = colourCss(colour, n, dark.matches);
      const pad = size >= 9 ? 1 : 0;
      context.fillRect(left + cx * size + pad, top + cy * size + pad, size - pad, size - pad);
      if (size >= 22) { context.fillStyle = dark.matches ? '#1b2220' : '#fff'; context.fillText(colour, left + (cx + .5) * size, top + (cy + .5) * size); }
    }
    // The square just left is ringed, so the change is easy to spot.
    if (last) {
      context.strokeStyle = t.ink;
      context.lineWidth = 2;
      context.strokeRect(left + last.x * size + 1, top + last.y * size + 1, size - 2, size - 2);
    }
    // The ant is a triangle pointing along its heading.
    const cx = left + (ant.x + .5) * size, cy = top + (ant.y + .5) * size, r = Math.max(4, size * .38);
    context.save();
    context.translate(cx, cy);
    context.rotate(ant.heading * Math.PI / 2);
    context.beginPath();
    context.moveTo(0, -r); context.lineTo(r * .8, r * .8); context.lineTo(-r * .8, r * .8); context.closePath();
    context.fillStyle = t.ink;
    context.fill();
    context.strokeStyle = t.panel;
    context.lineWidth = 1.5;
    context.stroke();
    context.restore();
  }

  function render() {
    const painted = [...ant.cells.values()].filter(Boolean).length;
    counter.textContent = `${ant.steps.toLocaleString('en-NZ')} step${ant.steps === 1 ? '' : 's'}`;
    summary.textContent = `${painted.toLocaleString('en-NZ')} squares not blank · facing ${HEADINGS[ant.heading]}`;
    canvas.setAttribute('aria-label', `Rule ${ant.rule} after ${ant.steps} steps: ${painted} non-blank squares, ant facing ${HEADINGS[ant.heading]}.`);
    backButton.disabled = ant.steps === 0;
    const atCap = ant.steps >= MAX_STEPS;
    stepButton.disabled = atCap;
    if (atCap && playing) pause();
    if (last) {
      const lines = describe(last);
      narration.replaceChildren(...lines.map(text => Object.assign(document.createElement('li'), { textContent: text })));
    } else {
      narration.replaceChildren(Object.assign(document.createElement('li'),
        { textContent: 'The board starts blank (colour 0) and the ant faces north. Press Step to watch it follow the table.' }));
    }
    if (atCap) narration.append(Object.assign(document.createElement('li'), { textContent: `Stopped at ${MAX_STEPS.toLocaleString('en-NZ')} steps; reset to start again.` }));
    markCurrentRow();
    draw();
  }

  function setRule(rule, announce) {
    pause();
    ant = new Ant(rule);
    last = null;
    ruleInput.value = rule;
    ruleError.textContent = '';
    for (const b of root.querySelectorAll('.ex-preset')) b.setAttribute('aria-pressed', String(b.dataset.rule === rule));
    buildTable();
    render();
    if (announce) ruleInput.setAttribute('aria-invalid', 'false');
  }

  function advance(count) {
    const result = ant.run(count);
    if (result) last = result;
    render();
  }
  function rewind() {
    // Replaying is exact and cheap at this scale, so there is no undo stack to keep correct.
    const target = ant.steps - 1;
    ant = new Ant(ant.rule);
    last = ant.run(target);
    render();
  }

  function pause() {
    playing = false;
    previous = null;
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    playButton.textContent = 'Play';
    playButton.setAttribute('aria-pressed', 'false');
    narration.setAttribute('aria-live', 'polite');
  }
  function play() {
    if (ant.steps >= MAX_STEPS) return;
    playing = true;
    narration.setAttribute('aria-live', 'off');
    playButton.textContent = 'Pause';
    playButton.setAttribute('aria-pressed', 'true');
    frame = requestAnimationFrame(tick);
  }
  function tick(now) {
    frame = null;
    if (!playing) return;
    const elapsed = previous === null ? 0 : Math.min(100, now - previous);
    previous = now;
    owed += elapsed / 1000 * SPEEDS[Number(speed.value)];
    const whole = Math.floor(owed);
    owed -= whole;
    if (whole > 0) advance(whole);
    if (playing) frame = requestAnimationFrame(tick);
  }

  stepButton.addEventListener('click', () => { pause(); advance(1); });
  backButton.addEventListener('click', () => { pause(); if (ant.steps > 0) rewind(); });
  playButton.addEventListener('click', () => (playing ? pause() : play()));
  for (const b of root.querySelectorAll('[data-skip]')) b.addEventListener('click', () => { pause(); advance(Number(b.dataset.skip)); });
  $('#ex-reset').addEventListener('click', () => setRule(ant.rule));
  speed.addEventListener('input', () => { speedLabel.textContent = `${SPEEDS[Number(speed.value)].toLocaleString('en-NZ')} steps/s`; });
  for (const b of root.querySelectorAll('.ex-preset')) b.addEventListener('click', () => setRule(b.dataset.rule, true));
  $('#ex-rule-form').addEventListener('submit', event => {
    event.preventDefault();
    const rule = parseRule(ruleInput.value);
    if (rule) setRule(rule, true);
    else { ruleError.textContent = `Use ${2}–${MAX_RULE} letters, each L or R.`; ruleInput.setAttribute('aria-invalid', 'true'); }
  });
  table.addEventListener('click', event => {
    const button = event.target.closest('.ex-turn');
    if (!button) return;
    const i = Number(button.dataset.index);
    setRule(ant.rule.slice(0, i) + (ant.rule[i] === 'R' ? 'L' : 'R') + ant.rule.slice(i + 1));
    table.querySelector(`.ex-turn[data-index="${i}"]`).focus();
  });
  dark.addEventListener('change', () => { buildTable(); render(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) pause(); });
  speed.value = '4';
  speed.dispatchEvent(new Event('input'));
  root.hidden = false;
  setRule('RL');
})();
