// Run from any directory. Each sample includes process setup and CSV output.
import { spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { readFileSync, writeFileSync, appendFileSync, mkdirSync, openSync, closeSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const root = fileURLToPath(new URL('../../../../', import.meta.url));
const experiment = path.join(root, 'experiments/active/2026-10-macos-gpu');
const scratch = path.join(experiment, 'scratch/bench');
mkdirSync(scratch, { recursive: true });
const cases = {
  small: { args: ['2', '6', '32768', '256'], lanes: 64 },
  batch: { args: ['2', '12', '1000000', '2048'], lanes: 4096 },
  'wide-pool': { args: ['2', '12', '10000000', '2048'], lanes: 4096, pool: 262144 },
  wide: { args: ['2', '12', '10000000', '2048'], lanes: 4096 },
  long: { args: ['2', '10', '10000000', '2048'], lanes: 1024 },
};
const name = process.argv[2];
if (!cases[name]) throw new Error('usage: node bench.mjs small|batch|long|wide|wide-pool [rerun-tag]');
// Committed records are never replaced: a rerun needs a tag and lands in its own file.
const tag = process.argv[3] ? `-${process.argv[3]}` : '';
const resultPath = path.join(experiment, 'results', `benchmark-${name}${tag}.json`);
if (existsSync(resultPath)) throw new Error(`${resultPath} exists; pass a rerun tag to save under a distinct path`);
// Hash and execute the same binaries cargo built, wherever CARGO_TARGET_DIR points.
const targetDir = path.resolve(root, process.env.CARGO_TARGET_DIR ?? 'target');
const config = cases[name];
const backends = ['sweep', 'sweep_lean', 'wgpu_sweep'];
const sha = bytes => createHash('sha256').update(bytes).digest('hex');
const capture = (command, args) => spawnSync(command, args, { cwd: root, encoding: 'utf8' }).stdout?.trim();
const env = { ...process.env, RAYON_NUM_THREADS: '16', TURMITE_GRID: 'dense' };
for (const key of ['TURMITE_CKPT_DIR', 'TURMITE_CKPT_EVERY', 'TURMITE_GRID_STATS']) delete env[key];
const result = {
  started: new Date().toISOString(), revision: capture('git', ['rev-parse', 'HEAD']),
  platform: capture('sw_vers', []), cpu: capture('sysctl', ['-n', 'machdep.cpu.brand_string']),
  thermalBefore: capture('pmset', ['-g', 'therm']),
  processesBefore: capture('ps', ['-A', '-o', '%cpu,comm', '-r'])?.split('\n').slice(0, 16),
  node: process.version, rustc: capture('rustc', ['--version']),
  targetDir, harnessSha256: sha(readFileSync(fileURLToPath(import.meta.url))),
  case: name, config, rayonThreads: 16, warmupsPerBackend: 1, samplesPerBackend: 5,
  method: 'Monotonic process wall time; one unmeasured warmup per backend; five rounds with rotating backend order. Includes startup, simulation, detection, onset and CSV writes. Each output hash checked.',
  binaries: {}, samples: [],
};
for (const backend of backends) result.binaries[backend] = sha(readFileSync(path.join(targetDir, 'release', backend)));
let expected;
function run(backend, round) {
  const binary = path.join(targetDir, 'release', backend);
  const args = [...config.args];
  const statsPath = path.join(scratch, `${name}-${backend}.json`);
  if (backend === 'wgpu_sweep') args.push('--lanes', String(config.lanes), '--pool-tiles', String(config.pool ?? 65536), '--slice', '65536', '--stats', statsPath);
  const outputPath = path.join(scratch, `${name}-${backend}.csv`);
  const fd = openSync(outputPath, 'w');
  const start = process.hrtime.bigint();
  const child = spawnSync(binary, args, { cwd: root, env, stdio: ['ignore', fd, 'pipe'], timeout: 180000 });
  const seconds = Number(process.hrtime.bigint() - start) / 1e9;
  closeSync(fd);
  if (child.status !== 0) throw new Error(`${backend}: ${child.error ?? child.stderr}`);
  const bytes = readFileSync(outputPath);
  const hash = sha(bytes);
  expected ??= hash;
  if (hash !== expected) throw new Error(`CSV differs: ${backend}, expected ${expected}, got ${hash}`);
  const stats = backend === 'wgpu_sweep' ? JSON.parse(readFileSync(statsPath)) : undefined;
  const sample = { backend, round, seconds, command: [binary, ...args], outputSha256: hash, rows: bytes.toString().trim().split('\n').length - 1, stats };
  if (round >= 0) result.samples.push(sample);
  console.log(`${name} ${round < 0 ? 'warmup' : `round ${round + 1}`} ${backend}: ${seconds.toFixed(3)}s, CSV matched${stats ? `, retries=${stats.oom_requeues}` : ''}`);
  writeFileSync(path.join(scratch, `${name}-partial.json`), JSON.stringify(result, null, 2) + '\n');
}
for (const backend of backends) run(backend, -1);
for (let round = 0; round < 5; round++) {
  for (let offset = 0; offset < backends.length; offset++) run(backends[(round + offset) % backends.length], round);
}
result.finished = new Date().toISOString();
result.thermalAfter = capture('pmset', ['-g', 'therm']);
result.summary = Object.fromEntries(backends.map(backend => {
  const times = result.samples.filter(x => x.backend === backend).map(x => x.seconds).sort((a,b) => a-b);
  return [backend, { median: times[2], min: times[0], max: times[4] }];
}));
result.speedupVsFast = result.summary.sweep.median / result.summary.wgpu_sweep.median;
result.speedupVsLean = result.summary.sweep_lean.median / result.summary.wgpu_sweep.median;
writeFileSync(resultPath, JSON.stringify(result, null, 2) + '\n', { flag: 'wx' });
appendFileSync(path.join(experiment, 'NOTEBOOK.md'), `\n## ${result.finished} — observation (${result.revision})\n\nCompleted ${name}${tag}: five samples per backend, one warmup each, rotating order. Every CSV matched SHA-256 ${expected}. Median seconds: fast=${result.summary.sweep.median}, lean=${result.summary.sweep_lean.median}, Metal=${result.summary.wgpu_sweep.median}. See results/benchmark-${name}${tag}.json for all samples and provenance.\n`);
console.log(JSON.stringify(result.summary, null, 2));
