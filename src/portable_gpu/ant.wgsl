// A tile has one owner: the invocation running its ant. Packed cell writes
// therefore need no atomics, even when four cells share a word.
struct Lane {
    steps: vec2<u32>,
    budget: vec2<u32>,
    seed: vec2<u32>,
    status: u32,
    n: u32,
    x: i32,
    y: i32,
    minx: i32,
    maxx: i32,
    miny: i32,
    maxy: i32,
    heading: u32,
    acc: u32,
    turn: vec4<u32>,
    has_bg: u32,
    ring_cursor: u32,
    padding: vec2<u32>,
}

struct Params {
    grid: u32,
    dir_w: u32,
    ring_words: u32,
    lanes: u32,
    slice_steps: u32,
    retire_count: u32,
    pool_tiles: u32,
    padding: u32,
}

@group(0) @binding(0) var<uniform> params: Params;
@group(0) @binding(1) var<storage, read_write> lanes: array<Lane>;
@group(0) @binding(2) var<storage, read_write> dirs: array<u32>;
@group(0) @binding(3) var<storage, read_write> pool: array<u32>;
@group(0) @binding(4) var<storage, read_write> freelist: array<u32>;
@group(0) @binding(5) var<storage, read_write> free_count: atomic<i32>;
@group(0) @binding(6) var<storage, read_write> rings: array<u32>;
@group(0) @binding(7) var<storage, read> retired: array<u32>;

const RUN: u32 = 0u;
const BUDGET: u32 = 1u;
const ESCAPED: u32 = 2u;
const OOM: u32 = 3u;

// Low word first. Only the low 64 product bits are needed by SplitMix64.
fn mul64(a: vec2<u32>, b: vec2<u32>) -> vec2<u32> {
    let a0 = a.x & 65535u;
    let a1 = a.x >> 16u;
    let b0 = b.x & 65535u;
    let b1 = b.x >> 16u;
    let w0 = a0 * b0;
    let t = a1 * b0 + (w0 >> 16u);
    let w1 = a0 * b1 + (t & 65535u);
    let high = a1 * b1 + (t >> 16u) + (w1 >> 16u);
    return vec2<u32>(a.x * b.x, high + a.x * b.y + a.y * b.x);
}

fn shr64(a: vec2<u32>, shift: u32) -> vec2<u32> {
    return vec2<u32>((a.x >> shift) | (a.y << (32u - shift)), a.y >> shift);
}

fn mix64(value: vec2<u32>) -> vec2<u32> {
    var z = value;
    z = mul64(z ^ shr64(z, 30u), vec2<u32>(0x1ce4e5b9u, 0xbf58476du));
    z = mul64(z ^ shr64(z, 27u), vec2<u32>(0x133111ebu, 0x94d049bbu));
    return z ^ shr64(z, 31u);
}

fn bg_colour(seed: vec2<u32>, x: i32, y: i32, n: u32) -> u32 {
    let key = vec2<u32>(bitcast<u32>(y), bitcast<u32>(x));
    let z = mix64(mix64(seed ^ vec2<u32>(0x4f6cdd1du, 0x2545f491u)) ^ key);
    // Base-65536 division keeps every intermediate below 2^32 for n <= 128.
    var rem = (z.y >> 16u) % n;
    rem = (rem * 65536u + (z.y & 65535u)) % n;
    rem = (rem * 65536u + (z.x >> 16u)) % n;
    return (rem * 65536u + (z.x & 65535u)) % n;
}

fn allocate_tile(state: Lane, di: u32, tx: u32, ty: u32) -> u32 {
    let old = atomicSub(&free_count, 1);
    if old <= 0 {
        atomicAdd(&free_count, 1);
        return 0u;
    }

    let id = freelist[u32(old - 1)];
    if state.has_bg != 0u {
        let half = i32(params.grid / 2u);
        for (var word = 0u; word < 1024u; word++) {
            var packed = 0u;
            for (var byte = 0u; byte < 4u; byte++) {
                let offset = word * 4u + byte;
                let x = i32(tx * 64u + (offset & 63u)) - half;
                let y = i32(ty * 64u + (offset >> 6u)) - half;
                packed |= bg_colour(state.seed, x, y, state.n) << (byte * 8u);
            }
            pool[id * 1024u + word] = packed;
        }
    }

    dirs[di] = id + 1u;
    return id + 1u;
}

@compute @workgroup_size(64)
fn init_pool(@builtin(global_invocation_id) gid: vec3<u32>) {
    if gid.x < params.pool_tiles {
        freelist[gid.x] = gid.x;
    }
}

@compute @workgroup_size(64)
fn step(@builtin(global_invocation_id) gid: vec3<u32>) {
    let tid = gid.x;
    if tid >= params.lanes {
        return;
    }

    var state = lanes[tid];
    if state.status != RUN {
        return;
    }

    let dir_base = tid * params.dir_w * params.dir_w;
    let ring_base = tid * params.ring_words;
    var cur_tx = 0xffffffffu;
    var cur_ty = 0xffffffffu;
    var tile_base = 0u;

    for (var done = 0u; done < params.slice_steps; done++) {
        if state.steps.y > state.budget.y ||
            (state.steps.y == state.budget.y && state.steps.x >= state.budget.x) {
            state.status = BUDGET;
            break;
        }

        let tx = u32(state.x) >> 6u;
        let ty = u32(state.y) >> 6u;
        if tx != cur_tx || ty != cur_ty {
            let di = dir_base + ty * params.dir_w + tx;
            var entry = dirs[di];
            if entry == 0u {
                entry = allocate_tile(state, di, tx, ty);
                if entry == 0u {
                    state.status = OOM;
                    break;
                }
            }
            tile_base = (entry - 1u) * 1024u;
            cur_tx = tx;
            cur_ty = ty;
        }

        let offset = ((u32(state.y) & 63u) << 6u) | (u32(state.x) & 63u);
        let wi = tile_base + (offset >> 2u);
        let shift = (offset & 3u) * 8u;
        let packed = pool[wi];
        let colour = (packed >> shift) & 255u;
        let right = (state.turn[colour >> 5u] >> (colour & 31u)) & 1u;
        state.heading = (state.heading + 3u - 2u * right) & 3u;
        let next = select(colour + 1u, 0u, colour + 1u == state.n);
        pool[wi] = (packed & ~(255u << shift)) | (next << shift);

        let heading_shift = (state.steps.x & 15u) * 2u;
        if heading_shift == 0u {
            state.acc = 0u;
        }
        state.acc |= state.heading << heading_shift;
        state.steps.x += 1u;
        if state.steps.x == 0u {
            state.steps.y += 1u;
        }
        state.x += i32(state.heading == 1u) - i32(state.heading == 3u);
        state.y += i32(state.heading == 2u) - i32(state.heading == 0u);

        if (state.steps.x & 15u) == 0u {
            rings[ring_base + state.ring_cursor] = state.acc;
            state.ring_cursor = (state.ring_cursor + 1u) % params.ring_words;
        }
        if state.x < 0 || state.y < 0 || u32(state.x) >= params.grid || u32(state.y) >= params.grid {
            state.status = ESCAPED;
            break;
        }

        state.minx = min(state.minx, state.x);
        state.maxx = max(state.maxx, state.x);
        state.miny = min(state.miny, state.y);
        state.maxy = max(state.maxy, state.y);
    }

    if state.status == RUN && all(state.steps == state.budget) {
        state.status = BUDGET;
    }
    if (state.steps.x & 15u) != 0u {
        rings[ring_base + state.ring_cursor] = state.acc;
    }
    lanes[tid] = state;
}

// Retirement is a separate dispatch, so allocations cannot race with tile reuse.
@compute @workgroup_size(64)
fn retire(@builtin(workgroup_id) group: vec3<u32>, @builtin(local_invocation_index) local: u32) {
    if group.x >= params.retire_count {
        return;
    }

    let dir_base = retired[group.x] * params.dir_w * params.dir_w;
    for (var di = local; di < params.dir_w * params.dir_w; di += 64u) {
        let entry = dirs[dir_base + di];
        if entry != 0u {
            let id = entry - 1u;
            for (var word = 0u; word < 1024u; word++) {
                pool[id * 1024u + word] = 0u;
            }
            dirs[dir_base + di] = 0u;
            let slot = atomicAdd(&free_count, 1);
            freelist[u32(slot)] = id;
        }
    }
}
