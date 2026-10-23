//! Census sweeps on native GPUs. macOS selects Metal.

use rayon::prelude::*;
use std::error::Error;
use std::fmt::Write as _;
use std::io::{self, Write};
use turmite::Rule;
use turmite::fast::Stop;
use turmite::onset::{OnsetScratch, highway_onset_reusing};
use turmite::portable_gpu::{GpuConfig, GpuSweeper, Job};

const USAGE: &str = "usage: wgpu_sweep MIN MAX MAX_STEPS [GRID] [flags]
   or: wgpu_sweep - - MAX_STEPS [GRID] [flags]

stdin: RULE [BACKGROUND_SEED], one job per line
flags:
  --lanes N       resident ants (default 1024)
  --slice N       steps per dispatch (default 65536)
  --pool-tiles N  4096-byte tiles in the shared pool (default 65536)
  --device K      native hardware adapter ordinal (default 0)
  --bg-seeds A..B cross each unseeded rule with seeds A through B
  --stats FILE    write job, step, dispatch and retry counters as JSON
  --help          show this help

Requires --features wgpu. macOS uses Metal; other native platforms use Vulkan/DX12.";

struct Options {
    gpu: GpuConfig,
    jobs: Vec<Job>,
    stats_path: Option<String>,
}

fn options(
    args: impl Iterator<Item = String>,
    input: impl io::BufRead,
) -> Result<Option<Options>, Box<dyn Error>> {
    let mut gpu = GpuConfig::default();
    let mut pos = Vec::new();
    let mut seeds = None;
    let mut stats_path = None;
    let mut args = args.peekable();

    while let Some(arg) = args.next() {
        if arg == "--help" || arg == "-h" {
            return Ok(None);
        }

        let mut value = || args.next().ok_or_else(|| format!("{arg} needs a value"));

        match arg.as_str() {
            "--lanes" => gpu.lanes = value()?.parse()?,
            "--slice" => gpu.slice_steps = value()?.parse()?,
            "--pool-tiles" => gpu.pool_tiles = value()?.parse()?,
            "--device" => gpu.device = value()?.parse()?,
            "--stats" => stats_path = Some(value()?),
            "--bg-seeds" => {
                let spec = value()?;
                let (a, b) = spec.split_once("..").ok_or("--bg-seeds needs A..B")?;
                let (a, b) = (a.parse::<u64>()?, b.parse::<u64>()?);

                if a > b {
                    return Err("background seed range must be increasing".into());
                }

                seeds = Some((a, b));
            }
            _ if arg.starts_with("--") => return Err(format!("unknown flag: {arg}").into()),
            _ => pos.push(arg),
        }
    }

    if !(3..=4).contains(&pos.len()) {
        return Err(USAGE.into());
    }

    let max_steps = pos[2].parse::<u64>()?;
    gpu.grid = pos
        .get(3)
        .map(|s| s.parse())
        .transpose()?
        .unwrap_or(gpu.grid);
    let rules = if pos[0] == "-" && pos[1] == "-" {
        let mut rules = Vec::new();

        for line in input.lines() {
            let line = line?;
            let mut fields = line.split_whitespace();
            let Some(rule) = fields.next() else { continue };
            let rule = rule.parse::<Rule>()?;
            let seed = fields.next().map(str::parse::<u64>).transpose()?;

            if fields.next().is_some() {
                return Err("stdin expects RULE [BACKGROUND_SEED]".into());
            }

            rules.push((rule, seed));
        }

        rules
    } else {
        let (lo, hi) = (pos[0].parse::<usize>()?, pos[1].parse::<usize>()?);

        if lo < 2 || hi > 31 || lo > hi {
            return Err("rule lengths must satisfy 2 <= MIN <= MAX <= 31".into());
        }

        (lo..=hi)
            .flat_map(|n| (0..1u32 << n).map(move |b| Rule::from_bits(b, n)))
            .filter(|rule| rule.is_canonical() && !rule.is_trivial())
            .map(|rule| (rule, None))
            .collect::<Vec<_>>()
    };
    let mut jobs = Vec::new();

    for (rule, seed) in rules {
        match (seed, seeds) {
            (Some(seed), _) => jobs.push(Job {
                rule,
                bg_seed: Some(seed),
                max_steps,
            }),
            (None, Some((a, b))) => {
                for seed in a..=b {
                    jobs.push(Job {
                        rule: rule.clone(),
                        bg_seed: Some(seed),
                        max_steps,
                    });
                }
            }
            (None, None) => jobs.push(Job {
                rule,
                bg_seed: None,
                max_steps,
            }),
        }
    }

    Ok(Some(Options {
        gpu,
        jobs,
        stats_path,
    }))
}

fn json_string(value: &str) -> String {
    let mut out = String::from("\"");

    for c in value.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            c if c < ' ' => {
                let _ = write!(out, "\\u{:04x}", c as u32);
            }
            c => out.push(c),
        }
    }

    out.push('"');
    out
}

fn run(opts: Options) -> Result<(), Box<dyn Error>> {
    let Options {
        gpu,
        jobs,
        stats_path,
    } = opts;
    let mut sweeper = GpuSweeper::new(gpu.clone())?;
    eprintln!(
        "{} ({:?}) | {} jobs | {} lanes | grid {} | {} tiles | slice {}",
        sweeper.device_name,
        sweeper.backend,
        jobs.len(),
        gpu.lanes,
        gpu.grid,
        gpu.pool_tiles,
        gpu.slice_steps
    );
    let results = sweeper.run(&jobs, |_| {})?;
    let onsets = jobs
        .par_iter()
        .zip(&results)
        .map_init(
            || None::<OnsetScratch>,
            |scratch, (job, result)| match (result.highway, job.bg_seed) {
                (Some(hw), None) => highway_onset_reusing(
                    &job.rule,
                    hw,
                    result.steps,
                    scratch.get_or_insert_with(|| OnsetScratch::new(gpu.grid)),
                )
                .to_string(),
                _ => String::new(),
            },
        )
        .collect::<Vec<_>>();
    let seeded = jobs.iter().any(|job| job.bg_seed.is_some());
    let mut out = io::BufWriter::new(io::stdout().lock());
    let seed_header = if seeded { "bg_seed," } else { "" };
    writeln!(
        out,
        "rule,{seed_header}n,stop,steps,period,dx,dy,onset,width,height,tail_period"
    )?;

    for ((job, result), onset) in jobs.iter().zip(&results).zip(&onsets) {
        let seed_col = if seeded {
            format!(
                "{},",
                job.bg_seed.map(|s| s.to_string()).unwrap_or_default()
            )
        } else {
            String::new()
        };
        let stop = match result.stop {
            Stop::Budget => "budget",
            Stop::Escaped => "escaped",
        };
        let (period, dx, dy) = result
            .highway
            .map(|hw| (hw.period.to_string(), hw.dx.to_string(), hw.dy.to_string()))
            .unwrap_or_default();
        let tail = result
            .periodic_tail
            .map(|hw| hw.period.to_string())
            .unwrap_or_default();
        writeln!(
            out,
            "{},{seed_col}{},{stop},{},{period},{dx},{dy},{onset},{},{},{tail}",
            job.rule,
            job.rule.len(),
            result.steps,
            result.extent.0,
            result.extent.1
        )?;
    }

    out.flush()?;

    if let Some(path) = stats_path {
        let stats = &sweeper.stats;
        std::fs::write(
            path,
            format!(
                "{{\"jobs\":{},\"total_steps\":{},\"launches\":{},\"oom_requeues\":{},\"device\":{},\"backend\":{},\"lanes\":{},\"grid\":{},\"pool_tiles\":{},\"slice\":{}}}\n",
                stats.jobs,
                stats.total_steps,
                stats.launches,
                stats.oom_requeues,
                json_string(&sweeper.device_name),
                json_string(&format!("{:?}", sweeper.backend)),
                gpu.lanes,
                gpu.grid,
                gpu.pool_tiles,
                gpu.slice_steps,
            ),
        )?;
    }

    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    match options(std::env::args().skip(1), io::stdin().lock())? {
        Some(opts) => run(opts),
        None => {
            println!("{USAGE}");
            Ok(())
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn parse(args: &[&str], stdin: &str) -> Result<Option<Options>, Box<dyn Error>> {
        options(args.iter().map(|s| (*s).to_owned()), stdin.as_bytes())
    }

    #[test]
    fn stdin_seeds_override_the_cross_product() {
        let opts = parse(
            &["-", "-", "17", "64", "--bg-seeds", "1..2"],
            "RL\nRLR 18446744073709551615\n",
        )
        .unwrap()
        .unwrap();
        assert_eq!(
            opts.jobs.iter().map(|j| j.bg_seed).collect::<Vec<_>>(),
            [Some(1), Some(2), Some(u64::MAX)]
        );
        assert!(opts.jobs.iter().all(|j| j.max_steps == 17));
        assert_eq!(opts.gpu.grid, 64);
    }

    #[test]
    fn help_and_invalid_input_need_no_gpu() {
        assert!(parse(&["--help"], "").unwrap().is_none());

        for args in [
            &[][..],
            &["2", "32", "10"],
            &["2", "6", "10", "--slice"],
            &["2", "6", "10", "--unknown"],
        ] {
            assert!(parse(args, "").is_err());
        }

        assert!(parse(&["-", "-", "10"], "RL 1 extra").is_err());
        assert!(parse(&["-", "-", "10", "--bg-seeds", "2..1"], "RL").is_err());
    }
}
