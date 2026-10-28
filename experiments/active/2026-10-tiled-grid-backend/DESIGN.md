# Tiled grid backend: design, limits, format

Code: `src/tiled.rs` (backend), `src/bin/sweep_lean.rs` (CLI), `tests/tiled.rs` (oracle tests). Measurements and the
adoption decision are in [README.md](README.md); this file describes what exists and what it does not do.

## Why `sweep_lean` is the first target

It is the production CPU runner for census sweeps; it already has mid-run checkpoints, highway detection, onset replay and an
extent report, so one integration exercises every observable at once. Its dense grid is also the clearest memory cost:
`LeanGrid::new` and every `run_lean_ckpt` call write all `(size+2)^2` bytes (`clear`), so a worker costs `size^2` resident bytes
whatever the ant does (8 GiB for a 16384 board on 32 workers, 4 GiB per worker at 65536). `fast::run` has the same shape without
checkpoints; `probe` is a different instrument (see "Probe" below).

## Semantics that are preserved (and one that is copied, not endorsed)

Same bounded square board as `LeanGrid` (side `size`, start at `size/2`, escape = leaving it), same step counts, positions,
headings, `RunResult` (highway, periodic tail, extent), and the same CSV. Tests compare the complete logical state with
`reference::Ant` (every colour and every touched flag), and the whole `RunResult` Debug string with `run_lean`.

* **Visited is not colour 0.** Each cell carries a touched bit (bit 7 of the lean byte, set when the ant writes the cell); it is
  stored in packed tiles as its own bit plane and is what extent and the "touched by arrival" logic read.
* **Bounded escape is unchanged.** The board is still `size x size`; tiles only decide where bytes live. Cells of a boundary tile
  that lie outside the board are `SENT`, exactly like lean's ring, so escape happens on the same step. An unbounded mode would
  change escape and highway semantics (a highway "leaves the grid" by definition) and is a separate extension, not attempted.
* **Quirk copied from lean, not fixed:** if `max_steps` ends exactly on the step that leaves the board, lean (and so the tiled
  backend) reports `Budget` with the ring position and an extent that counts the ring cell (wrong by one, or wrapped to a width
  of 0), where `fast::run` reports `Escaped`. This is pinned in `tests/tiled.rs`
  (`budget_ending_on_the_escaping_step_is_lean_compatible`). Fixing it in lean would change sweep CSVs, so it is left alone and
  recorded in the notebook.

## Layout and tile states

Relative coordinates `(x, y)` (start = `(0, 0)`, board `[-size/2, size - size/2)` on each axis) map to tile
`(x.div_euclid(T), y.div_euclid(T))`, `T = 2^tile_log2` (2^2 .. 2^12; default 2^6). About half of all tile indices are
negative; tile keys pack two `i32`s and the board is limited to `2^30` so they fit.

```
absent  --first visit-->  resident  --evict-->  packed | raw     (all-blank resident tiles are dropped: back to absent)
                             ^                      |
                             +------ load/decode ---+
```

* **Absent** - no payload; every cell is blank background (colour 0, untouched). Never scanned or initialised.
* **Resident** - a `(T+2)^2` byte buffer, lean's encoding, one-cell halo of `SENT` plus `SENT` for off-board interior cells.
  The halo is never written, which is what lets `lean::advance` run unchanged inside a tile: it stops exactly when the ant steps
  onto a cell that is not this tile's. The cursor then moves to the owning tile (`settle`, outside the inner loop).
* **Packed** - `ceil(T^2 * w / 8)` bytes of fixed-width colours (`w = ceil(log2 n)`, 0 for the one-colour rule; little-endian
  bit order) followed by `T^2 / 8` bytes of touched bits. Off-board cells are stored blank and rebuilt as `SENT` on load.
  Decoding validates length, every colour `< n`, and that off-board cells are blank.
* **Raw inactive** - `T^2` bytes (the resident encoding without halo). Used by `Inactive::Raw`, and as the fallback when packing
  would not be smaller: `w = 7` (65 or more colours) gives `7/8 + 1/8 = 1` byte per cell, so those rules are stored raw.
* **Compressed** - an LZ4 block (`lz4_flex`, safe mode) of the canonical packed (or raw) payload, built on eviction only and kept only if smaller; expanded on a miss (length checked, then the packed-decode validation). `Inactive::Compressed`, `TURMITE_INACTIVE=lz4`. Checkpoints always hold the canonical form, so no codec version is persisted.

There is exactly one authoritative copy of each cell. A resident tile has no backing copy: loading a tile removes its inactive
payload, eviction creates a fresh one. The stepper writes the first cell it enters, so every resident tile is dirty from the
moment it becomes current; there is no clean-eviction shortcut to implement or count. Read-only accessors (extent, checkpoint,
`logical_cells`) read the resident tile when there is one and decode a packed tile into scratch without changing the cache.

## Cache

`cache_tiles: Option<usize>`: the maximum number of resident tiles (`None` = unlimited: sparse allocation only, nothing is ever
evicted). Minimum 2 (`MIN_CACHE_TILES`), enforced: the ant needs its current tile and keeping the previous one stops a tile-edge
ping-pong from decoding on every step. Policy: deterministic LRU. Every tile *entry* (never a step) stamps a counter; the victim
is the live tile with the smallest stamp other than the current one (a linear scan over at most `cache_tiles` stamps, only on a
miss). Buffers are recycled, so a long run allocates `cache_tiles` buffers once. Output never depends on the cache size or its
history (`configuration_independent`); only counters and time do. Trail reversal and the onset replay use the same tile entry
path, one tile at a time, so the minimum of 2 is enough for the stepping backend.

**Cost model:** a transition into a resident tile is a hash lookup (about tens of ns); a miss costs one encode and one decode of
`T^2` cells; a tile bigger than the structure with a tiny cache therefore thrashes badly (observed: T = 2^10, cache 2, board 256,
where the start sits at the corner of four tiles: the 57-rule, 32768-step batch was killed after 9 minutes; the same batch takes
0.05 s at T = 2^6 with an unlimited cache and 3.6 s at T = 2^6 with cache 2). A cache of at least the structure's tile footprint
avoids evictions altogether.

## Memory accounting

`TiledGrid::memory()` reports logical bytes: resident buffers (all allocated buffers, `(T+2)^2` each, including free-listed ones),
packed bytes, raw-inactive bytes, a directory estimate (hash-table capacity x (key + slot + control byte)) and pool bookkeeping.
`TileStats` has per-run counters (transitions, hits, misses, creations, evictions, blank drops, packed/raw stores, bytes encoded
and decoded) and peaks (resident tiles, inactive bytes, total). Limiting `cache_tiles` bounds only the resident part; the
inactive store grows with the number of tiles ever touched (`n_tiles x packed_len`, or `T^2` raw), so total memory is
`cache_tiles x (T+2)^2 + n_tiles x payload + directory`. Logical bytes are not process memory: allocator overhead, the trail
(`history x 24` bytes for positions, indices and reconstruction) and the OS decide RSS, so the benchmarks report peak RSS beside
the logical figures. The dense baseline is *committed* memory (it writes every byte), so a lazily-zeroed dense allocation is not a
cheaper baseline here.

## Supported configurations and explicit limits

* Square grid, one ant, blank background, fewer than 100 colours (lean's limit), `size` in `1 ..= 2^30`.
  `initial_cell` backgrounds (patched, sparse, rotor) are **rejected by omission**: the CLI only reaches the plain-rule path.
* Tile side 2^2 .. 2^12; cache >= 2; `Inactive::{Raw, Packed, Compressed}`.
* No unbounded mode, no turmites with states, no other lattices, no walkers other than the plain ant.
* Checkpoints do not interoperate with the dense format or across tile sizes (rejected with an explicit error).
* The CLI aborts the sweep with a message when a tiled checkpoint is damaged or belongs to another run; the dense loader silently
  restarts. Delete the file to restart.

## CLI

`sweep_lean` keeps its positional arguments and CSV. Backend selection follows its existing environment convention:

```bash
# dense (default), as before
echo RLR | sweep_lean - - 100000000 8192
# sparse tiles only
echo RLR | TURMITE_GRID=tiled TURMITE_TILE_LOG2=6 TURMITE_CACHE_TILES=unlimited sweep_lean - - 100000000 8192
# bounded cache, packed inactive tiles, statistics to a separate file, checkpoints
echo RLR | TURMITE_GRID=tiled TURMITE_CACHE_TILES=1024 TURMITE_INACTIVE=packed \
  TURMITE_GRID_STATS=run.json TURMITE_CKPT_DIR=ck TURMITE_CKPT_EVERY=1000000000 sweep_lean - - 100000000 65536
```

`TURMITE_GRID_STATS` is written for dense runs too (backend, board, wall time, peak RSS), so the two can be compared from the
same file format. Invalid values exit with status 2 and a message.

## Checkpoint format (`TTK1`, version 1)

Little-endian: `"TTK1"`, `u32` version, `u32` rule-name length + name, `u64` board side, `u32` tile_log2, `u8` colour width,
`u64` steps, `i64` x, `i64` y (cursor relative to the start; may be a ring cell if a budget ended there), `u8` heading, `u64`
tile count, then per tile in ascending `(ty, tx)` order: `i32` tx, `i32` ty, `u8` tag (1 packed, 2 raw), `u32` payload length,
payload; finally the `u64` FNV-1a hash of everything before it. Blank tiles are omitted, and the payload form (packed when
smaller than raw, else raw) depends only on (colour count, tile size), so the bytes do not depend on cache size, eviction
history or `Inactive` mode (`checkpoint_resume_exact` compares them across settings). The file is written to a temporary name
and renamed. Loading rejects: bad magic, checksum mismatch or truncation (`Corrupt`), another version, rule, board size or tile
size (`Incompatible`), tiles out of order or outside the board, a tag that does not match the canonical form, a stored blank
tile, a colour out of range, a non-blank off-board cell, and trailing bytes. A checkpoint past `max_steps` is ignored as in
lean. Dense and tiled checkpoints use different extensions (`.ckpt`, `.tkpt`) and magics.
`experiments/active/2026-10-tiled-grid-backend/scripts/compress_estimate.py` is an independent reader of this format.

## Probe: what is and is not done

Not integrated. `probe_walker` keeps two dense `size^2` arrays (colour and the per-cell unvisited-neighbour count that also
encodes "visited"), i.e. up to `2 x size^2` bytes (128 MiB at 8192, 512 MiB at 16384; measured peak RSS is lower because zeroed pages are committed only where the ant has been: 69 MiB at 8192 for RLR to 2^22 steps), plus, for walkers with `RANDOM_INIT`, a
`size^2` initial-background fill. `Region::visit` updates the four neighbours of each newly visited cell, so a tiled probe needs
cross-tile neighbour access (pinning up to five tiles, or sequential per-neighbour access), and the unvisited-count array is
*not* compressible by colour packing: it is visited-status plus a 0-4 counter per cell. Colour compression alone therefore
cannot solve probe memory; a tiled probe needs the same sparse tiles for the `unv` plane and a measured design. Follow-up in the
README.
