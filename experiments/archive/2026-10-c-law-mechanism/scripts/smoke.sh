#!/bin/bash
# timing smoke test of the driver (no registered quantity is read from this)
cd /mnt/f/Code/turmite/.claude/worktrees/paper-figure-proposals
cargo build --release --example c_law_mechanism_trace 2>&1 | tail -2
time (echo RRRLRRLLLLR | ./target/release/examples/c_law_mechanism_trace blank 24 4096 | cut -c1-260)
time (echo RRRLRRLLLLR | ./target/release/examples/c_law_mechanism_trace band 26 256 1024 512 1 | cut -c1-260)
