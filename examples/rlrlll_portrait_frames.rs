//! experiments/archive/2026-10-rlrlll-portrait: whole-territory snapshots of RLRLLL from a blank board, for the
//! homepage visual of the late column sweeper. No statistic is computed here; the frames are pictures.
//! usage: rlrlll_portrait_frames RULE TIMES_FILE OUTDIR [GRID=32768] [BLOCK=16] [CROP=256]
//! TIMES_FILE: one step count per line, ascending. At each listed t (before step t is taken) and once more when
//! the ant leaves the board (t = steps taken), writes OUTDIR/frame_T.bin: header line "t ant_x ant_y size block n", then for each
//! block (row-major, (size/block)^2 blocks) n little-endian u16 counts of visited cells of colour 0..n-1
//! (unvisited = block^2 - sum). Also OUTDIR/crop_T.bin: header "t x0 y0 w h", then raw colours (255 = unvisited)
//! of the CROP x CROP window centred on the ant. Coordinates are offsets from the centre.
//! Same plain loop, DIRS and update order as `g1_ribbon_breakout_builder_dump`.
use std::io::Write;
use turmite::{DIRS, Rule};

const SEEN: u8 = 0x80;

fn write_frame(out: &std::path::Path, t: u64, cells: &[u8], size: usize, block: usize, n: usize, ax: i64, ay: i64, crop: i64) {
    let c = (size / 2) as i64;
    let nb = size / block;
    let mut counts = vec![0u16; nb * nb * n];
    for y in 0..size {
        let row = &cells[y * size..(y + 1) * size];
        let base = (y / block) * nb;
        for (x, &v) in row.iter().enumerate() {
            if v & SEEN != 0 {
                counts[(base + x / block) * n + (v & !SEEN) as usize] += 1;
            }
        }
    }
    let mut f = std::io::BufWriter::new(std::fs::File::create(out.join(format!("frame_{t}.bin"))).unwrap());
    writeln!(f, "{t} {} {} {size} {block} {n}", ax - c, ay - c).unwrap();
    for v in &counts {
        f.write_all(&v.to_le_bytes()).unwrap();
    }
    let (x0, y0) = ((ax - crop / 2).clamp(0, size as i64 - crop), (ay - crop / 2).clamp(0, size as i64 - crop));
    let mut f = std::io::BufWriter::new(std::fs::File::create(out.join(format!("crop_{t}.bin"))).unwrap());
    writeln!(f, "{t} {} {} {crop} {crop}", x0 - c, y0 - c).unwrap();
    for y in y0..y0 + crop {
        for x in x0..x0 + crop {
            let v = cells[y as usize * size + x as usize];
            f.write_all(&[if v & SEEN == 0 { 255 } else { v & !SEEN }]).unwrap();
        }
    }
}

fn main() {
    let a: Vec<String> = std::env::args().collect();
    let rule: Rule = a[1].parse().unwrap();
    let times: Vec<u64> = std::fs::read_to_string(&a[2]).unwrap().lines()
        .filter(|l| !l.trim().is_empty()).map(|l| l.trim().parse().unwrap()).collect();
    assert!(times.windows(2).all(|w| w[0] < w[1]), "TIMES_FILE must be ascending");
    let out = std::path::PathBuf::from(&a[3]);
    let size: usize = a.get(4).map_or(32768, |v| v.parse().unwrap());
    let block: usize = a.get(5).map_or(16, |v| v.parse().unwrap());
    let crop: i64 = a.get(6).map_or(256, |v| v.parse().unwrap());
    assert!(size % block == 0 && block * block <= u16::MAX as usize);
    std::fs::create_dir_all(&out).unwrap();
    let n = rule.len();
    let turn: Vec<u8> = rule.0.iter().map(|t| t.delta()).collect();
    let mut cells = vec![0u8; size * size];
    let c = (size / 2) as i64;
    let (mut x, mut y, mut h) = (c, c, 0u8);
    let mut next = 0;
    let mut t: u64 = 0;
    loop {
        if next < times.len() && times[next] == t {
            write_frame(&out, t, &cells, size, block, n, x, y, crop);
            eprintln!("frame at {t}");
            next += 1;
        }
        let i = (y as usize) * size + x as usize;
        let col = (cells[i] & !SEEN) as usize;
        h = (h + turn[col]) & 3;
        cells[i] = SEEN | ((col + 1) % n) as u8;
        let (dx, dy) = DIRS[h as usize];
        x += dx as i64;
        y += dy as i64;
        t += 1;
        if x < 1 || y < 1 || x >= size as i64 - 1 || y >= size as i64 - 1 {
            eprintln!("left the board after {t} steps");
            write_frame(&out, t, &cells, size, block, n, x, y, crop);
            break;
        }
    }
}
