//! 2026-10-tiled-grid-backend: cost of packing one 64 x 64 tile, measured on its own so the main timings stay undistorted.
//! usage: tiled_grid_backend_codec [REPS]   (prints one TSV line per rule: n, colour width, packed bytes, microseconds per tile)
//! The tile is the central 64 x 64 block of a real run (3e6 steps), so colours and touched flags are realistic, not random.

use std::time::Instant;
use turmite::Rule;
use turmite::fast::Config;
use turmite::tiled::{TileConfig, TiledGrid, colour_width, pack_cells, packed_len, run_tiled, unpack_cells};

fn main() {
    let reps: usize = std::env::args().nth(1).map_or(20_000, |v| v.parse().unwrap());
    println!("rule\tn\tw\tpacked_bytes\traw_bytes\tencode_us\tdecode_us\tcell_ns_encode\tcell_ns_decode");
    for r in ["RLR", "RRRRRRRLLRRR", "RLLRLLLRRRLL"] {
        let rule: Rule = r.parse().unwrap();
        let mut g = TiledGrid::new(8192, TileConfig::default()).unwrap();
        run_tiled(&rule, &mut g, &Config { max_steps: 3_000_000, ..Config::default() });
        let cells: Vec<u8> = (-32..32i64).flat_map(|y| (-32..32i64).map(move |x| (x, y))).map(|(x, y)| g.byte_at(x, y).unwrap()).collect();
        let (n, w) = (rule.len(), colour_width(rule.len()));
        let packed = pack_cells(&cells, 64, w);
        assert_eq!(packed.len(), packed_len(64, w));
        assert_eq!(unpack_cells(&packed, 64, w, n).unwrap(), cells);
        let t = Instant::now();
        let mut sink = 0usize;
        for _ in 0..reps {
            sink += std::hint::black_box(pack_cells(std::hint::black_box(&cells), 64, w)).len();
        }
        let enc = t.elapsed().as_secs_f64() / reps as f64;
        let t = Instant::now();
        for _ in 0..reps {
            sink += std::hint::black_box(unpack_cells(std::hint::black_box(&packed), 64, w, n).unwrap()).len();
        }
        let dec = t.elapsed().as_secs_f64() / reps as f64;
        println!("{r}\t{n}\t{w}\t{}\t{}\t{:.2}\t{:.2}\t{:.2}\t{:.2}", packed.len(), cells.len(), enc * 1e6, dec * 1e6, enc * 1e9 / 4096.0, dec * 1e9 / 4096.0);
        assert!(sink > 0);
    }
}
