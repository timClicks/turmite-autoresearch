/* Illustrations evaluate stated assumptions or display saved measurements.
   No simulation, fitted estimator or animation runs here. The only request is
   card 09's saved arrival map, a same-site image. */
(function () {
  'use strict';
  const billions = t => (t / 1e9).toFixed(2);
  const millions = n => (n / 1e6).toFixed(1);
  // Readout for snapshot k of card 09's RLRLLL run (data.sweeper from export_results.py).
  function sweeperLabel(sw, k) {
    const t = sw.t[k], cells = `${millions(sw.visited[k])} million cells visited`;
    return t <= sw.switch_t
      ? `Step ${billions(t)} billion · still a blob · ${cells}`
      : `Step ${billions(t)} billion · sweeping for ${t - sw.switch_t < 1e8
        ? `${millions(t - sw.switch_t)} million` : `${billions(t - sw.switch_t)} billion`} steps · ${cells}`;
  }
  // Draw only once the browser can decode the map without colour conversion; the
  // static image and caption stay in place otherwise.
  function initSweeper(document, sw) {
    const win = document.defaultView, get = id => document.getElementById(id);
    const figure = get('sweeper-map');
    if (!figure || typeof win.createImageBitmap !== 'function') return;
    const canvas = get('sweeper-canvas'), slider = get('sweeper-frame');
    const progress = get('sweeper-progress'), readout = get('sweeper-readout');
    const palette = sw.colours.map(hex => [1, 3, 5].map(i => parseInt(hex.slice(i, i + 2), 16)));
    const end = sw.t[sw.t.length - 1];
    const image = new win.Image();
    image.src = figure.dataset.arrival;
    image.decode()
      .then(() => win.createImageBitmap(image, { colorSpaceConversion: 'none', premultiplyAlpha: 'none' }))
      .then(bitmap => {
        const { width, height } = bitmap;
        const scratch = document.createElement('canvas');
        scratch.width = width; scratch.height = height;
        const sctx = scratch.getContext('2d', { willReadFrequently: true });
        sctx.drawImage(bitmap, 0, 0);
        const grey = sctx.getImageData(0, 0, width, height).data;
        // The PNG rows run from low y to high y; the figure shows high y at the top.
        const arrival = new Uint8Array(width * height);
        for (let y = 0; y < height; y++)
          for (let x = 0; x < width; x++)
            arrival[(height - 1 - y) * width + x] = grey[4 * (y * width + x)];
        if (arrival.some(a => a > sw.t.length)) throw new Error('arrival map does not match the snapshot list');
        canvas.width = width; canvas.height = height;
        const ctx = canvas.getContext('2d');
        const frame = ctx.createImageData(width, height);
        function draw(k) {
          const px = frame.data;
          for (let i = 0; i < arrival.length; i++) {
            const a = arrival[i];
            if (a > 0 && a - 1 <= k) {
              const c = palette[a - 1];
              px[4 * i] = c[0]; px[4 * i + 1] = c[1]; px[4 * i + 2] = c[2]; px[4 * i + 3] = 255;
            } else px[4 * i + 3] = 0;
          }
          ctx.putImageData(frame, 0, 0);
          const label = sweeperLabel(sw, k);
          readout.textContent = label;
          slider.setAttribute('aria-valuetext', label);
          progress.style.width = `${(100 * sw.t[k] / end).toFixed(2)}%`;
          progress.classList.toggle('is-sweeping', sw.t[k] > sw.switch_t);
          progress.style.setProperty('--switch', `${(100 * sw.switch_t / sw.t[k]).toFixed(2)}%`);
        }
        slider.addEventListener('input', () => draw(Number(slider.value)));
        draw(Number(slider.value));
        canvas.hidden = false;
        get('sweeper-fallback').hidden = true;
        figure.querySelector('.sweeper-controls').hidden = false;
      })
      .catch(() => {});
  }
  function init(document) {
    const root = document.querySelector('.preliminary-results');
    if (!root) return;
    const data = JSON.parse(document.getElementById('preliminary-data').textContent);
    const get = id => document.getElementById(id);
    const width = get('width-factor');
    width.addEventListener('input', () => {
      get('width-label').textContent = `${width.value}×`;
      get('width-time').textContent = String(Number(width.value) ** 3);
    });
    const lead = get('lead-length');
    function showLead() {
      const m = Number(lead.value), cost = data.law.a + data.law.b * m;
      get('lead-label').textContent = `${m} turn${m === 1 ? '' : 's'}`;
      const rule = get('lead-rule');
      rule.replaceChildren(document.createTextNode('R'.repeat(m)));
      const suffix = document.createElement('span'); suffix.textContent = 'L…'; rule.append(suffix);
      rule.setAttribute('aria-label', `Example rule with an opening run of ${m} right turn${m === 1 ? '' : 's'}`);
      get('lead-prediction').textContent = `Model: about ${cost.toFixed(2)} boundary steps per new cell (c ≈ ${(1 / cost).toFixed(3)}).`;
    }
    lead.addEventListener('input', showLead); showLead();
    const toggle = get('occupation-toggle');
    let adjusted = true;
    function showOccupation() {
      toggle.setAttribute('aria-pressed', String(adjusted));
      toggle.textContent = `Adjust for growth: ${adjusted ? 'on' : 'off'}`;
      get('occupation-mode').textContent = adjusted ? 'Occupation / each walker’s uniform reference' : 'Original probe κ · endpoint normalization';
      const rows = [{ key: 'ant', value: adjusted ? data.ant_ratio : data.ant_raw },
        ...data.walkers.map((w, i) => ({ key: String(i), value: adjusted ? w.ratio : w.raw }))];
      for (const row of rows) {
        get(`occupation-${row.key}`).textContent = `${row.value.toFixed(2)}${adjusted ? '×' : ''}`;
        root.querySelector(`[data-occupation="${row.key}"]`).style.width = `${row.value * 50}%`;
      }
    }
    toggle.addEventListener('click', () => { adjusted = !adjusted; showOccupation(); }); showOccupation();
    root.querySelectorAll('.result-controls, .result-toggle').forEach(el => { el.hidden = false; });
    initSweeper(document, data.sweeper);
  }
  if (typeof module !== 'undefined') module.exports = { init, sweeperLabel };
  if (typeof document !== 'undefined') init(document);
})();
