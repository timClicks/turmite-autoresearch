#!/bin/bash
# Pilot = every 4th rule (0,4,8,...) of the 48 sorted rules of the first-passage confirm cohort, seeds ...8001-2;
# confirmation = the other 36 rules, same seeds. Controls: rw:301, rotor:301-302.
set -e
cd "$(dirname "$0")/.."
SPECS=../2026-10-kappa-first-passage/results/confirm_specs.txt
cut -d@ -f1 $SPECS | sort -u > scratch/rules48.txt
awk 'NR%4==1' scratch/rules48.txt > results/pilot_rules.txt
awk 'NR%4!=1' scratch/rules48.txt > results/confirm_rules.txt
for kind in pilot confirm; do
  : > results/${kind}_specs.txt
  while read r; do for s in 202610208001 202610208002; do echo "$r@$s" >> results/${kind}_specs.txt; done; done < results/${kind}_rules.txt
done
printf 'rw:301\nrotor:301\nrotor:302\n' >> results/pilot_specs.txt
wc -l results/*_specs.txt
