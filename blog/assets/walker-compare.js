// "Compare walkers": an ant, a rotor walker and two random walkers, run in lock-step
// from the same origin. Dynamics follow src/walkers.rs (heading 0 = north; the ant reads,
// turns, advances the colour, then moves; the rotor advances its arrow, then steps along it).
// Differences from the Rust code: every random choice (the rotor's initial arrows, and the
// random and persistent walks' draws) comes from a 32-bit generator (mix32 / mulberry32),
// not the Rust SplitMix64 stream, and the board is finite (see HALF).
(() => {
  'use strict';
  const DX = [0, 1, 0, -1], DY = [-1, 0, 1, 0];
  // Walkers stop if they reach the edge of their board. The ant and rotor need a byte per
  // square for their state; the random walks only need a visited bit, so theirs is wider
  // (a 2^20-step walk has rms displacement near 1000, so 1024 would end half the runs early).
  const HALF = 1024, WIDE_HALF = 4096;
  const VIEW = 256, MAX_STEPS = 1 << 20;   // picture resolution; stopping point
  const VISITED = 128;

  function mix32(h) {
    h ^= h >>> 16; h = Math.imul(h, 0x85ebca6b);
    h ^= h >>> 13; h = Math.imul(h, 0xc2b2ae35);
    return (h ^ (h >>> 16)) >>> 0;
  }
  function initialArrow(seed, x, y) { return mix32(mix32(mix32(seed + 0x9e3779b9) ^ x) ^ y) & 3; }
  function rng(seed) {                        // mulberry32
    let s = seed >>> 0;
    return () => {
      s = (s + 0x6d2b79f5) >>> 0;
      let t = Math.imul(s ^ (s >>> 15), 1 | s);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  class Walker {
    constructor(kind, options = {}) {
      this.kind = kind;
      this.rule = options.rule || null;
      this.seed = options.seed || 1;
      // Ant and rotor: a byte per square. Low bits: ant colour, or rotor arrow + 1 (0 = not yet
      // left); bit 7: ever visited. Random walks: one visited bit per square.
      this.bits = kind === 'randomwalk' || kind === 'persistent';
      this.half = this.bits ? WIDE_HALF : HALF;
      this.side = 2 * this.half;
      this.board = new Uint8Array(this.bits ? this.side * this.side / 8 : this.side * this.side);
      if (kind === 'ant') {
        this.turn = Uint8Array.from(this.rule, ch => (ch === 'R' ? 1 : 3));
        this.next = Uint8Array.from(this.rule, (_, i) => (i + 1) % this.rule.length);
      }
      this.random = rng(this.seed * 7919 + (kind === 'persistent' ? 1 : 0));
      this.view = new Uint32Array(VIEW * VIEW);
      this.k = 0;
      this.x = this.y = this.heading = this.steps = 0;
      this.extent = 0; this.area = 0;
      this.moment = 0;   // sum of x^2 + y^2 over distinct visited sites
      this.stopped = null;
      this.pending = false;
      this.samples = { t: [], spread: [] };
      this.nextSample = 1;
      this.visit(this.half * this.side + this.half);
    }
    // Record that the walker is on the square at board[index]: area, and the picture.
    visit(index) {
      let fresh;
      if (this.bits) {
        const byte = index >> 3, mask = 1 << (index & 7);
        fresh = !(this.board[byte] & mask);
        this.board[byte] |= mask;
      } else {
        fresh = !(this.board[index] & VISITED);
        this.board[index] |= VISITED;
      }
      if (fresh) { this.area++; this.moment += this.x * this.x + this.y * this.y; }
      this.plot();
    }
    plot() {
      const u = (this.x >> this.k) + VIEW / 2, v = (this.y >> this.k) + VIEW / 2;
      if ((u | v) & ~(VIEW - 1)) { this.pending = true; return false; }
      this.view[v * VIEW + u]++;
      this.pending = false;
      return true;
    }
    zoomOut() {
      const old = this.view, half = VIEW / 2;
      this.view = new Uint32Array(VIEW * VIEW);
      for (let v = 0; v < VIEW; v++) for (let u = 0; u < VIEW; u++) {
        const count = old[v * VIEW + u];
        if (count) this.view[(((v - half) >> 1) + half) * VIEW + ((u - half) >> 1) + half] += count;
      }
      this.k++;
      if (this.pending) this.plot();
    }
    // Root-mean-square distance from the start of the sites visited so far: a smooth size
    // for the whole territory, unlike the furthest square, which only ever steps up.
    get spread() { return Math.sqrt(this.moment / this.area); }
    sample() {
      this.samples.t.push(this.steps); this.samples.spread.push(this.spread);
      this.nextSample = Math.max(this.steps + 1, Math.floor(this.steps * 1.05));
    }
    // Runs up to `count` steps; stops early (leaving `pending` set) when the picture needs to zoom out.
    run(count) {
      const board = this.board, kind = this.kind, half = this.half, side = this.side;
      let done = 0;
      while (done < count && !this.stopped && !this.pending && this.steps < MAX_STEPS) {
        let { x, y, heading } = this;
        const index = (y + half) * side + x + half;
        if (kind === 'ant') {
          const c = board[index] & 127;
          heading = (heading + this.turn[c]) & 3;
          board[index] = (board[index] & VISITED) | this.next[c];
        } else if (kind === 'rotor') {
          const stored = board[index] & 7;
          const arrow = ((stored ? stored - 1 : initialArrow(this.seed, x, y)) + 1) & 3;
          board[index] = (board[index] & VISITED) | (arrow + 1);
          heading = arrow;
        } else if (kind === 'randomwalk') {
          heading = (this.random() * 4) | 0;
        } else {
          heading = (heading + (this.random() < 0.5 ? 1 : 3)) & 3;
        }
        x += DX[heading]; y += DY[heading];
        this.x = x; this.y = y; this.heading = heading;
        this.steps++; done++;
        const reach = Math.max(Math.abs(x), Math.abs(y));
        if (reach > this.extent) this.extent = reach;
        if (reach >= half - 1) { this.stopped = 'reached the edge of the board'; }
        else this.visit((y + half) * side + x + half);
        if (this.steps >= this.nextSample) this.sample();
      }
      if (this.steps >= MAX_STEPS && !this.stopped) this.stopped = 'finished';
      return done;
    }
  }

  class Race {
    // shared: every picture uses one scale, so sizes can be compared by eye; otherwise each
    // walker zooms out only as far as it needs to, which shows more of the small ones.
    constructor(rule, seed, shared = true) {
      this.rule = rule; this.seed = seed; this.shared = shared;
      this.clock = 0;   // lock-step time; a walker that left the board stops, the clock does not
      this.walkers = [
        new Walker('ant', { rule }), new Walker('rotor', { seed }),
        new Walker('randomwalk', { seed }), new Walker('persistent', { seed }),
      ];
    }
    get steps() { return this.clock; }
    get done() { return this.clock >= MAX_STEPS || this.walkers.every(w => w.stopped); }
    // Every walker takes `count` more steps. The picture is shared, so all zoom together.
    advance(count) {
      count = Math.min(count, MAX_STEPS - this.clock);
      this.clock += count;
      for (const w of this.walkers) {
        let left = count;
        while (left > 0 && !w.stopped && w.steps < MAX_STEPS) {
          const room = Math.min(left, MAX_STEPS - w.steps);
          left -= w.run(room);
          if (w.pending) { if (this.shared) this.zoomAll(); else w.zoomOut(); }
        }
      }
    }
    zoomAll() {
      const k = Math.max(...this.walkers.map(w => w.k)) + 1;
      for (const w of this.walkers) while (w.k < k) w.zoomOut();
    }
  }

  if (typeof module !== 'undefined') module.exports = { Walker, Race, initialArrow, rng, HALF, VIEW, MAX_STEPS };
  if (typeof document === 'undefined') return;
  const root = document.querySelector('.walker-compare');
  if (!root) return;
  const chart = root.querySelector('#wc-chart'), chartContext = chart && chart.getContext('2d');
  const panels = [...root.querySelectorAll('.wc-panel')].map(figure => ({
    figure, canvas: figure.querySelector('canvas'), context: figure.querySelector('canvas').getContext('2d'),
    stats: figure.querySelector('.wc-stats'),
  }));
  if (!chartContext || panels.length !== 4 || panels.some(p => !p.context)) return;

  const $ = selector => root.querySelector(selector);
  const playButton = $('#wc-play'), speed = $('#wc-speed'), ruleSelect = $('#wc-rule'), seedLabel = $('#wc-seed');
  const counter = $('#wc-steps'), summary = $('#wc-summary'), scaleSelect = $('#wc-scale');
  const dark = matchMedia('(prefers-color-scheme: dark)');
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const SPEEDS = [300, 3000, 30000, 300000];
  const SERIES = [
    { name: 'Ant', light: '#b74727', dark: '#f09b76', dash: [] },
    { name: 'Rotor', light: '#2f6f6a', dark: '#98bbb8', dash: [9, 4] },
    { name: 'Random walk', light: '#8a6d1f', dark: '#d7bc83', dash: [2, 3] },
    { name: 'Persistent walk', light: '#5d6f46', dark: '#b6c895', dash: [10, 3, 2, 3] },
  ];
  const colourOf = i => (dark.matches ? SERIES[i].dark : SERIES[i].light);

  let seed = 1, race = new Race(ruleSelect.value, seed, scaleSelect.value === 'shared');
  let playing = false, visible = false, frame = null, previous = null, owed = 0;

  function theme() {
    const s = getComputedStyle(root), v = name => s.getPropertyValue(name).trim();
    return { panel: v('--panel'), ink: v('--ink'), line: v('--line'), muted: v('--muted') };
  }

  const picture = document.createElement('canvas');
  picture.width = picture.height = VIEW;
  const pictureContext = picture.getContext('2d');

  function hexToRgb(hex) {
    const full = hex.length === 4 ? '#' + [...hex.slice(1)].map(c => c + c).join('') : hex;
    const n = parseInt(full.slice(1), 16);
    return [n >> 16, (n >> 8) & 255, n & 255];
  }

  function drawPanel(p, w, i, t) {
    const [r, g, b] = hexToRgb(colourOf(i)), [pr, pg, pb] = hexToRgb(t.panel);
    const image = pictureContext.createImageData(VIEW, VIEW), d = image.data;
    for (let j = 0; j < w.view.length; j++) {
      const count = w.view[j];
      // Every visited block shows; heavier visiting is darker, saturating at 255 visits per block.
      const a = count ? 0.3 + 0.7 * Math.min(1, Math.log2(1 + count) / 8) : 0;
      d[4 * j] = pr + (r - pr) * a; d[4 * j + 1] = pg + (g - pg) * a; d[4 * j + 2] = pb + (b - pb) * a; d[4 * j + 3] = 255;
    }
    pictureContext.putImageData(image, 0, 0);
    p.context.imageSmoothingEnabled = false;
    p.context.drawImage(picture, 0, 0);
    const scale = p.canvas.width / VIEW, half = VIEW / 2;
    const px = (((w.x >> w.k) + half) + .5) * scale, py = (((w.y >> w.k) + half) + .5) * scale;
    p.context.beginPath();
    p.context.arc(px, py, 3.5, 0, Math.PI * 2);
    p.context.fillStyle = t.ink;
    p.context.fill();
    p.context.strokeStyle = t.panel;
    p.context.lineWidth = 1.5;
    p.context.stroke();
    p.stats.textContent = `spread ${w.spread.toFixed(1)} · reach ${w.extent.toLocaleString('en-NZ')} · ${w.area.toLocaleString('en-NZ')} sites`
      + (w.k ? ` · 1 pixel = ${2 ** w.k}×${2 ** w.k}` : '')
      + (w.stopped && w.stopped !== 'finished' ? ` · ${w.stopped}` : '');
    p.canvas.setAttribute('aria-label', `${SERIES[i].name}${i === 0 ? ' ' + race.rule : ''} after ${w.steps} steps: reach ${w.extent}, ${w.area} sites visited.`);
  }

  function drawChart(t) {
    // Match the drawing size to the layout so text stays legible on narrow screens.
    const width = Math.max(300, Math.round(chart.clientWidth || 760));
    const height = width < 520 ? 300 : Math.round(width * 0.42);
    if (chart.width !== width || chart.height !== height) { chart.width = width; chart.height = height; }
    const c = chartContext, W = chart.width, H = chart.height;
    const pad = { l: 54, r: width < 520 ? 44 : 96, t: 14, b: 38 };
    const X0 = 0, X1 = Math.log10(MAX_STEPS), Y0 = 0, Y1 = Math.log10(2048);
    const sx = v => pad.l + (Math.log10(v) - X0) / (X1 - X0) * (W - pad.l - pad.r);
    const sy = v => H - pad.b - (Math.log10(Math.max(1, v)) - Y0) / (Y1 - Y0) * (H - pad.t - pad.b);
    c.fillStyle = t.panel;
    c.fillRect(0, 0, W, H);
    c.font = '11px ui-monospace, monospace';
    c.fillStyle = t.muted; c.strokeStyle = t.line; c.lineWidth = 1;
    c.textAlign = 'center'; c.textBaseline = 'top';
    for (let e = 0; e <= 6; e++) {
      const x = Math.round(sx(10 ** e)) + .5;
      c.beginPath(); c.moveTo(x, pad.t); c.lineTo(x, H - pad.b); c.stroke();
      c.fillText(e === 0 ? '1' : e === 1 ? '10' : `10${'⁰¹²³⁴⁵⁶⁷⁸⁹'[e]}`, x, H - pad.b + 6);
    }
    c.textAlign = 'right'; c.textBaseline = 'middle';
    for (let e = 0; e <= 3; e++) {
      const y = Math.round(sy(10 ** e)) + .5;
      c.beginPath(); c.moveTo(pad.l, y); c.lineTo(W - pad.r, y); c.stroke();
      c.fillText(e === 0 ? '1' : e === 1 ? '10' : `10${'⁰¹²³'[e]}`, pad.l - 6, y);
    }
    c.textAlign = 'center'; c.textBaseline = 'bottom';
    c.fillText('steps', (pad.l + W - pad.r) / 2, H - 2);
    c.save(); c.translate(11, (pad.t + H - pad.b) / 2); c.rotate(-Math.PI / 2); c.textBaseline = 'top'; c.fillText('spread (rms distance of visited sites)', 0, 0); c.restore();
    // Reference slopes through (1, 1): spread = steps^(1/2) and steps^(1/3).
    c.setLineDash([4, 4]); c.strokeStyle = t.muted; c.lineWidth = 1; c.fillStyle = t.muted; c.textAlign = 'left'; c.textBaseline = 'middle';
    for (const [a, label] of [[1 / 2, 't½'], [1 / 3, 't⅓']]) {
      c.beginPath(); c.moveTo(sx(1), sy(1)); c.lineTo(sx(MAX_STEPS), sy(MAX_STEPS ** a)); c.stroke();
      c.fillText(label, sx(MAX_STEPS) + 5, sy(MAX_STEPS ** a));
    }
    c.setLineDash([]);
    race.walkers.forEach((w, i) => {
      const s = w.samples, n = s.t.length;
      if (!n) return;
      c.strokeStyle = colourOf(i); c.lineWidth = 2; c.setLineDash(SERIES[i].dash); c.beginPath();
      for (let j = 0; j < n; j++) { const x = sx(s.t[j]), y = sy(s.spread[j]); if (j) c.lineTo(x, y); else c.moveTo(x, y); }
      c.lineTo(sx(Math.max(1, w.steps)), sy(w.spread));
      c.stroke();
    });
    // Legend: each series by line style as well as colour.
    c.setLineDash([]); c.textAlign = 'left'; c.textBaseline = 'middle'; c.font = '11px ui-monospace, monospace';
    SERIES.forEach((series, i) => {
      const y = pad.t + 12 + i * 16;
      c.strokeStyle = colourOf(i); c.lineWidth = 2; c.setLineDash(series.dash);
      c.beginPath(); c.moveTo(pad.l + 10, y); c.lineTo(pad.l + 40, y); c.stroke();
      c.setLineDash([]); c.fillStyle = t.ink;
      c.fillText(series.name, pad.l + 46, y);
    });
    chart.setAttribute('aria-label', `Log-log chart of spread against steps after ${race.steps} steps. `
      + race.walkers.map((w, i) => `${SERIES[i].name}: ${w.spread.toFixed(1)}`).join('; ')
      + '. Dashed reference lines show steps to the half and to the third.');
  }

  function render() {
    const t = theme();
    race.walkers.forEach((w, i) => drawPanel(panels[i], w, i, t));
    drawChart(t);
    counter.textContent = `${race.steps.toLocaleString('en-NZ')} steps`;
    summary.textContent = race.shared ? 'All four pictures are drawn at the same scale.'
      : 'Each picture is scaled to fit its own walker, so compare the numbers and the chart, not the sizes.';
    seedLabel.textContent = `seed ${seed}`;
    if (race.done && playing) pause();
    playButton.disabled = race.done;
  }

  function pause() {
    playing = false; previous = null;
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    playButton.textContent = 'Play';
  }
  function schedule() {
    if (frame !== null) cancelAnimationFrame(frame);
    frame = null;
    if (playing && visible && !document.hidden) frame = requestAnimationFrame(tick);
  }
  function play() {
    if (race.done) return;
    playing = true;
    playButton.textContent = 'Pause';
    schedule();
  }
  function tick(now) {
    frame = null;
    if (!playing || !visible || document.hidden) return;
    // Capping elapsed time avoids catch-up work after a busy or hidden tab.
    const elapsed = previous === null ? 0 : Math.min(100, now - previous);
    previous = now;
    owed += elapsed / 1000 * SPEEDS[Number(speed.value)];
    const whole = Math.floor(owed);
    owed -= whole;
    if (whole > 0) { race.advance(whole); render(); }
    schedule();
  }
  function restart(newSeed, first) {
    const resume = playing || first;
    pause();
    if (newSeed !== undefined) seed = newSeed;
    race = new Race(ruleSelect.value, seed, scaleSelect.value === 'shared');
    owed = 0;
    race.advance(1 << 12);   // a still preview, so the picture is never blank
    render();
    if (resume && !reducedMotion.matches) play();
  }
  function skipTo(target) {
    pause();
    if (race.steps < target) race.advance(target - race.steps);
    render();
  }

  playButton.addEventListener('click', () => (playing ? pause() : play()));
  $('#wc-reset').addEventListener('click', () => restart());
  $('#wc-reseed').addEventListener('click', () => restart(seed + 1));
  ruleSelect.addEventListener('change', () => restart());
  scaleSelect.addEventListener('change', () => restart());
  speed.addEventListener('input', () => { $('#wc-speed-label').textContent = `${SPEEDS[Number(speed.value)].toLocaleString('en-NZ')} steps/s`; });
  for (const b of root.querySelectorAll('[data-skip]')) b.addEventListener('click', () => skipTo(Number(b.dataset.skip)));
  document.addEventListener('visibilitychange', () => { previous = null; schedule(); });
  dark.addEventListener('change', render);
  addEventListener('resize', () => drawChart(theme()));
  reducedMotion.addEventListener('change', () => { if (reducedMotion.matches) pause(); });
  speed.value = '2';
  speed.dispatchEvent(new Event('input'));
  root.hidden = false;
  if (typeof IntersectionObserver === 'undefined') visible = true;
  restart(undefined, true);
  if (typeof IntersectionObserver !== 'undefined') {
    new IntersectionObserver(entries => {
      visible = entries[0].isIntersecting;
      previous = null;
      schedule();
    }).observe(root);
  }
})();
