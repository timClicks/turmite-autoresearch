// Colour-intervention sampler for experiments/archive/2026-10-boundary-return-map (registration: its README).
// stdin: one spec per line (RULE@SEED, rotor:SEED, rw:SEED).
// args: OUT CAP BOARD K GAP REPS RADII(comma) BANDS(comma, lower area edges) HASH THREADS
// OUT/<spec>.dep.csv: one row per sampled departure (baseline episode); OUT/<spec>.rep.csv: one row per replica.
// Territory cannot change inside an interior episode, so a departure is replayed on the cropped colour field.
use rayon::prelude::*;
use std::fmt::Write as _;
use std::path::Path;
use turmite::walkers::{PatchedAnt, RandomWalk, Rotor, Walker};
use turmite::{DIRS, Rule};

fn splitmix(s: &mut u64) -> u64 {
    *s = s.wrapping_add(0x9E37_79B9_7F4A_7C15);
    let mut z = *s;
    z = (z ^ (z >> 30)).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    z = (z ^ (z >> 27)).wrapping_mul(0x94D0_49BB_1331_11EB);
    z ^ (z >> 31)
}

fn hash_str(s: &str) -> u64 {
    s.bytes().fold(0xcbf2_9ce4_8422_2325u64, |h, b| (h ^ b as u64).wrapping_mul(0x100_0000_01b3))
}

struct Ep {
    t: u64,
    pos: usize,
    heading: u8,
    col: u8,
    cens: bool,
    reach: u64,
}

/// Run from an interior state until the first step that lands on a non-inner cell.
fn episode<W: Walker + Clone>(w: &W, c: &mut [u8], inner: &[bool], off: [isize; 4], mut pos: usize, mut heading: u8, cap: u64, mut seen: Option<&mut [bool]>) -> Ep {
    let mut w = w.clone();
    let mut t = 0u64;
    let start = pos;
    let width = off[2].unsigned_abs().max(off[0].unsigned_abs()).max(off[1].unsigned_abs()).max(off[3].unsigned_abs());
    let mut reach = 0;
    loop {
        if let Some(s) = seen.as_deref_mut() {
            s[pos] = true;
        }
        let mut cell = c[pos];
        w.step(&mut cell, &mut heading);
        c[pos] = cell;
        pos = (pos as isize + off[heading as usize]) as usize;
        t += 1;
        reach = reach.max((pos % width).abs_diff(start % width).max((pos / width).abs_diff(start / width)) as u64);
        if !inner[pos] {
            if let Some(s) = seen.as_deref_mut() {
                s[pos] = true;
            }
            return Ep { t, pos, heading, col: c[pos], cens: false, reach };
        }
        if t >= cap {
            return Ep { t, pos: usize::MAX, heading: 9, col: 255, cens: true, reach };
        }
    }
}

struct Cfg<'a> {
    out: &'a Path,
    cap: u64,
    board: usize,
    k_dep: usize,
    gap: u64,
    reps: usize,
    radii: Vec<i64>,
    bands: Vec<u64>,
}

fn run<W: Walker + Clone>(mut w: W, spec: &str, ncol: usize, cfg: &Cfg) {
    let s = cfg.board;
    let n = s * s;
    let off: [isize; 4] = DIRS.map(|(dx, dy)| dx as isize + dy as isize * s as isize);
    let mut col = vec![0u8; n];
    let mut vis = vec![false; n];
    let (mut area, mut t) = (0u64, 0u64);
    let mut pos = (s / 2) * s + s / 2;
    let mut heading = 0u8;
    let (mut lo, mut hi) = ((usize::MAX, usize::MAX), (0usize, 0usize));
    // response table: heading a colour produces (distinguishes "turn changed" for any walker)
    let resp: Vec<u8> = (0..256usize)
        .map(|c| {
            if c >= ncol {
                return 255;
            }
            let mut cl = w.clone();
            let (mut cell, mut h) = (c as u8, 0u8);
            cl.step(&mut cell, &mut h);
            h
        })
        .collect();
    let spec_hash = hash_str(spec);
    let mut dep = String::from("spec,band,dep,stratum,t0,area,perim,base_t,base_dx,base_dy,base_h,base_c,base_cens,maxdepth,live_ok
");
    let mut rep = String::from("spec,band,dep,pair,arm,cell,match_n,base_t,base_reach,t,reach,cens,ident
");
    let mut hist = String::from("spec,band,bucket,n
");
    // live episode record: departure state plus an undo log of overwritten colours, so the departure field
    // can be rebuilt after the episode's length (the sampling stratum) is known
    struct Rec<W> {
        w0: W,
        t0: u64,
        pos0: usize,
        h0: u8,
        log: Vec<(usize, u8)>,
        overflow: bool,
    }
    let strata_of = |t: u64| if t <= 3 { 0usize } else if t <= 31 { 1 } else if t <= 511 { 2 } else { 3 };
    let mut band = 0usize;
    let mut taken = [0usize; 4];
    let mut last_t0 = [0u64; 4];
    let mut bh = [0u64; 25];
    let mut n_row = 0usize;
    let mut rec: Option<Rec<W>> = None;
    let mut prev_z = true;
    loop {
        if !vis[pos] {
            vis[pos] = true;
            let (x, y) = ((pos % s) as i64 - (s / 2) as i64, (pos / s) as i64 - (s / 2) as i64);
            col[pos] = w.initial_cell(x, y);
            area += 1;
            lo = (lo.0.min(pos % s), lo.1.min(pos / s));
            hi = (hi.0.max(pos % s), hi.1.max(pos / s));
        }
        let (px, py) = (pos % s, pos / s);
        assert!(px > 2 && py > 2 && px < s - 3 && py < s - 3, "{spec}: reached the board edge at t={t}");
        let z = off.iter().any(|d| !vis[(pos as isize + d) as usize]);
        if band < cfg.bands.len() && area >= cfg.bands[band] + cfg.bands[band] / 16 && rec.is_none() {
            for (k, &n) in bh.iter().enumerate() {
                if n > 0 {
                    let _ = writeln!(hist, "{spec},{band},{k},{n}");
                }
            }
            band += 1;
            taken = [0; 4];
            last_t0 = [0; 4];
            bh = [0; 25];
        }
        if band >= cfg.bands.len() && rec.is_none() {
            break;
        }
        if z {
            if let Some(r) = rec.take() {
                let tt = t - r.t0;
                bh[(64 - tt.leading_zeros() as usize).min(24)] += 1;
                let st = strata_of(tt);
                if st == 3 && !r.overflow && taken[st] < cfg.k_dep && (taken[st] == 0 || r.t0 - last_t0[st] >= cfg.gap) {
                    taken[st] += 1;
                    last_t0[st] = r.t0;
                    let mut row = sample(&r.w0, spec, spec_hash, band, n_row, st, &r.log, r.t0, area, &col, &vis, lo, hi, s, r.pos0, r.h0, cfg, &resp, &mut rep);
                    let ok = row.0.t == tt && row.0.pos == pos && row.0.heading == heading && row.0.col == col[pos];
                    assert!(ok, "live replay mismatch {spec}");
                    row.1.push_str(&format!(",{}", ok as u8));
                    dep.push_str(&row.1);
                    dep.push('\n');
                    n_row += 1;
                }
            }
        } else if prev_z && band < cfg.bands.len() && area >= cfg.bands[band] && rec.is_none() {
            rec = Some(Rec { w0: w.clone(), t0: t, pos0: pos, h0: heading, log: Vec::new(), overflow: false });
        }
        prev_z = z;
        if let Some(r) = rec.as_mut() {
            if r.log.len() as u64 >= cfg.cap {
                r.overflow = true;
            } else {
                r.log.push((pos, col[pos]));
            }
        }
        let mut cell = col[pos];
        w.step(&mut cell, &mut heading);
        col[pos] = cell;
        pos = (pos as isize + off[heading as usize]) as usize;
        t += 1;
        assert!(t < 4_000_000_000, "{spec}: step budget exhausted");
    }
    let name = spec.replace([':', '@'], "_");
    std::fs::write(cfg.out.join(format!("{name}.dep.csv")), dep).unwrap();
    std::fs::write(cfg.out.join(format!("{name}.rep.csv")), rep).unwrap();
    std::fs::write(cfg.out.join(format!("{name}.hist.csv")), hist).unwrap();
}

#[allow(clippy::too_many_arguments)]
fn sample<W: Walker + Clone>(
    w: &W, spec: &str, spec_hash: u64, band: usize, dep_i: usize, stratum: usize, undo: &[(usize, u8)], t: u64, area: u64, col: &[u8], vis: &[bool], lo: (usize, usize), hi: (usize, usize), s: usize, pos: usize, heading: u8,
    cfg: &Cfg, resp: &[u8], rep: &mut String,
) -> (Ep, String) {
    // crop with a 1-cell margin so neighbour reads stay in range
    let (x0, y0) = (lo.0 - 1, lo.1 - 1);
    let (cw, ch) = (hi.0 - lo.0 + 3, hi.1 - lo.1 + 3);
    let loc = |idx: usize| (idx / s - y0) * cw + (idx % s - x0);
    let mut c0 = vec![0u8; cw * ch];
    let mut vl = vec![false; cw * ch];
    for y in lo.1..=hi.1 {
        for x in lo.0..=hi.0 {
            let g = y * s + x;
            if vis[g] {
                let l = loc(g);
                vl[l] = true;
                c0[l] = col[g];
            }
        }
    }
    // rebuild the departure field: undo the live episode's writes in reverse order
    for &(g, old) in undo.iter().rev() {
        c0[loc(g)] = old;
    }
    let loff: [isize; 4] = DIRS.map(|(dx, dy)| dx as isize + dy as isize * cw as isize);
    let inner: Vec<bool> = (0..cw * ch).map(|i| vl[i] && i > cw && i + cw < cw * ch && loff.iter().all(|d| vl[(i as isize + d) as usize])).collect();
    let perim = (0..cw * ch).filter(|&i| vl[i] && !inner[i]).count();
    // depth by BFS through visited cells from the boundary
    let mut depth = vec![u32::MAX; cw * ch];
    let mut q: std::collections::VecDeque<usize> = (0..cw * ch).filter(|&i| vl[i] && !inner[i]).collect();
    for &i in &q {
        depth[i] = 0;
    }
    while let Some(i) = q.pop_front() {
        for d in loff {
            let j = (i as isize + d) as usize;
            if vl[j] && depth[j] == u32::MAX {
                depth[j] = depth[i] + 1;
                q.push_back(j);
            }
        }
    }
    let lp = loc(pos);
    let (px, py) = ((lp % cw) as i64, (lp / cw) as i64);
    // baseline
    let mut cb = c0.clone();
    let mut seen = vec![false; cw * ch];
    let base = episode(w, &mut cb, &inner, loff, lp, heading, cfg.cap, Some(&mut seen));
    let maxdepth = (0..cw * ch).filter(|&i| seen[i] && inner[i]).map(|i| depth[i]).max().unwrap_or(0);
    let (bdx, bdy) = if base.cens { (0, 0) } else { ((base.pos % cw) as i64 - px, (base.pos / cw) as i64 - py) };
    // Rank baseline read traffic, never perturbation outcomes.
    let mut traffic = vec![0u64; c0.len()];
    let mut c = c0.clone();
    let mut ww = w.clone();
    let (mut pp, mut hh) = (lp, heading);
    for _ in 0..base.t {
        traffic[pp] += 1;
        ww.step(&mut c[pp], &mut hh);
        pp = (pp as isize + loff[hh as usize]) as usize;
    }
    let mut ranked: Vec<usize> = (0..c0.len()).filter(|&i| traffic[i]>0 && inner[i]).collect();
    ranked.sort_by_key(|&i| (std::cmp::Reverse(traffic[i]), i));
    ranked.truncate(3);
    let dist = |i: usize| (i % cw).abs_diff(lp % cw).max((i / cw).abs_diff(lp / cw));
    let mut rng = spec_hash ^ ((band as u64)<<56) ^ ((dep_i as u64)<<32) ^ 2026102201;
    let mut used = ranked.clone();
    let mut arms: Vec<(usize, &str, usize, u8, usize)> = vec![(99,"sham",lp,c0[lp],1)];
    for (k,&g) in ranked.iter().enumerate() {
        let pool: Vec<usize> = (0..c0.len()).filter(|i| inner[*i] && traffic[*i]>0 && !used.contains(i) && c0[*i]==c0[g] && depth[*i]/8==depth[g]/8 && dist(*i)/8==dist(g)/8).collect();
        if pool.is_empty() {
            let _ = writeln!(rep,"{spec},{band},{dep_i},{k},missing,{g},0,{},{},0,0,0,0",base.t,base.reach);
            continue;
        }
        let h = pool[(splitmix(&mut rng) % pool.len() as u64) as usize];
        used.push(h);
        let options: Vec<u8> = (0..resp.len()).filter(|&i| resp[i]!=255 && resp[i]!=resp[c0[g] as usize]).map(|i| i as u8).collect();
        let v = if options.is_empty() {c0[g]} else {options[(splitmix(&mut rng)%options.len() as u64) as usize]};
        arms.push((k,"gate",g,v,pool.len()));
        arms.push((k,"matched",h,v,pool.len()));
    }
    if let Some(i) = (0..c0.len()).find(|&i| inner[i] && traffic[i]==0) {
        let v = (0..resp.len()).find(|&v| resp[v]!=255 && resp[v]!=resp[c0[i] as usize]).unwrap_or(c0[i] as usize) as u8;
        arms.push((99,"offpath",i,v,1));
    }
    for (k,arm,i,v,mn) in arms {
        let mut cc = c0.clone(); cc[i]=v;
        let mut path = vec![false;c0.len()];
        let e = episode(w,&mut cc,&inner,loff,lp,heading,cfg.cap,Some(&mut path));
        let ident = e.t==base.t && e.pos==base.pos && e.heading==base.heading && e.reach==base.reach;
        if arm=="sham" || arm=="offpath" || spec.starts_with("rw:") {assert!(ident,"negative control failed");}
        let _ = writeln!(rep,"{spec},{band},{dep_i},{k},{arm},{i},{mn},{},{},{},{},{},{}",base.t,base.reach,e.t,e.reach,e.cens as u8,ident as u8);
    }
    let row = format!("{spec},{band},{dep_i},{stratum},{t},{area},{perim},{},{bdx},{bdy},{},{},{},{maxdepth}", base.t, base.heading, base.col, base.cens as u8);
    // arrival position in board coordinates, for the live-ant check
    let gpos = if base.cens { usize::MAX } else { (y0 + base.pos / cw) * s + x0 + base.pos % cw };
    (Ep { pos: gpos, ..base }, row)
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    assert_eq!(a.len(), 11, "OUT CAP BOARD K GAP REPS RADII BANDS HASH THREADS");
    let out = Path::new(&a[1]);
    let radii: Vec<i64> = a[7].split(',').map(|x| x.parse().unwrap()).collect();
    let bands: Vec<u64> = a[8].split(',').map(|x| x.parse().unwrap()).collect();
    let cfg = Cfg { out, cap: a[2].parse().unwrap(), board: a[3].parse().unwrap(), k_dep: a[4].parse().unwrap(), gap: a[5].parse().unwrap(), reps: a[6].parse().unwrap(), radii, bands };
    let marker = format!("single_cell_gate_v1 {} cap={} board={} k={} gap={} reps={} radii={:?} bands={:?}\n", a[9], cfg.cap, cfg.board, cfg.k_dep, cfg.gap, cfg.reps, cfg.radii, cfg.bands);
    rayon::ThreadPoolBuilder::new().num_threads(a[10].parse().unwrap()).build_global().unwrap();
    std::fs::create_dir_all(out).unwrap();
    let specs: Vec<String> = std::io::stdin().lines().map(|s| s.unwrap()).filter(|s| !s.trim().is_empty()).collect();
    specs.par_iter().for_each(|spec| {
        let name = spec.replace([':', '@'], "_");
        let done = out.join(format!("{name}.done"));
        if std::fs::read_to_string(&done).is_ok_and(|s| s == marker) {
            eprintln!("skip {spec}");
            return;
        }
        assert!(!done.exists(), "different config marker: {spec}; use a new output directory");
        let clock = std::time::Instant::now();
        if let Some(sd) = spec.strip_prefix("rotor:") {
            run(Rotor { seed: sd.parse().unwrap() }, spec, 4, &cfg);
        } else if let Some(sd) = spec.strip_prefix("rw:") {
            run(RandomWalk { state: sd.parse().unwrap() }, spec, 1, &cfg);
        } else {
            let (rule, seed) = spec.split_once('@').unwrap();
            let rule: Rule = rule.parse().unwrap();
            let n = rule.len();
            run(PatchedAnt::new(&rule, seed.parse().unwrap(), 2), spec, n, &cfg);
        }
        std::fs::write(&done, &marker).unwrap();
        eprintln!("done {spec} in {:.1}s", clock.elapsed().as_secs_f64());
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn sparse_oracle() {
        use std::collections::BTreeMap;
        let rule: Rule = "RLLLRRLRLL".parse().unwrap();
        for seed in 1..=20 {
            for changed in [false,true] {
                let w = PatchedAnt::new(&rule,seed,2);
                let size=17usize;
                let off=[-(size as isize),1,size as isize,-1];
                let inner: Vec<bool>=(0..size*size).map(|i| i/size>0 && i/size<size-1 && i%size>0 && i%size<size-1).collect();
                let mut c: Vec<u8>=(0..size*size).map(|i| ((i*7+seed as usize)%rule.len()) as u8).collect();
                let start=8*size+8;
                if changed {c[start]=((c[start] as usize+1)%rule.len()) as u8;}
                let mut sparse: BTreeMap<(i32,i32),u8>=(0..size*size).map(|i| ((i as i32%17,i as i32/17),c[i])).collect();
                let e=episode(&w,&mut c,&inner,off,start,0,4096,None);
                let (mut x,mut y,mut h,mut reach)=(8i32,8i32,0u8,0u64);
                let mut ww=w.clone();
                let mut expected=None;
                for t in 1..=4096 {
                    ww.step(sparse.get_mut(&(x,y)).unwrap(),&mut h);
                    let (dx,dy)=[(0,-1),(1,0),(0,1),(-1,0)][h as usize];
                    x+=dx;y+=dy;
                    reach=reach.max((x-8).abs().max((y-8).abs()) as u64);
                    if x==0 || x==16 || y==0 || y==16 {expected=Some((t,(y*17+x) as usize,h));break;}
                }
                assert_eq!(e.reach,reach);
                if let Some((t,p,h))=expected {assert!(!e.cens);assert_eq!((e.t,e.pos,e.heading),(t,p,h));} else {assert!(e.cens);}
            }
        }
    }
}
