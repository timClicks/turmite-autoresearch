#!/bin/bash
# Items 26/27 experiments. usage (WSL): bash experiments/archive/2026-10-ext-other-lattices-turmites-noise/scripts/ext_specs_26_27.sh   (writes experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_*.csv)
cd /mnt/f/Code/turmite
E=$CARGO_TARGET_DIR/release/ext
# H27: many ants, deterministic
for r in RLR RLL RLRLRRRLLR RRRLR; do for m in 1 2 4 8; do echo "sq:$r:m=$m"; done; done | $E 12 26 8192 64 > experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_many.csv
# H26b: turn noise
for r in RLR RLL RLRLRRRLLR; do for e in 0 0.0001 0.001 0.01 0.1; do for s in 1 2 3; do echo "sq:$r:eps=$e:seed=$s"; done; done; done | $E 12 27 8192 64 > experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise.csv
# H26a: random background
for r in RLR RLL RLRLRRRLLR RRRLR; do for s in 1 2 3 4; do echo "sq:$r:bg:seed=$s"; done; done | $E 12 24 8192 64 > experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_bg.csv
# H26b extension: where does noise finally change the class? (added after the first noise run showed no change up to eps=0.1)
for r in RLR RLL RLRLRRRLLR; do for e in 0.3 0.6 1.0; do for s in 1 2 3; do echo "sq:$r:eps=$e:seed=$s"; done; done; done | $E 12 26 8192 64 > experiments/archive/2026-10-ext-other-lattices-turmites-noise/results/ext_noise_high.csv
