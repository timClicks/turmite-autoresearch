with open('experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_specs.txt') as f:
    rules = [line.strip() for line in f if line.strip()]

specs = []
# Patched starts seeds 0..7
for r in rules:
    for s in range(8):
        specs.append(f"{r}@{s}")

# Blank board starts
for r in rules:
    specs.append(r)

# Controls
for s in [301, 302, 303, 304]:
    specs.append(f"rotor:{s}")
for s in [301, 302, 303, 304]:
    specs.append(f"rw:{s}")

with open('experiments/archive/2026-10-t1-excursion-tomography/results/t1_specs.txt', 'w') as out:
    for sp in specs:
        out.write(sp + '\n')

print(f"Wrote {len(specs)} specs to experiments/archive/2026-10-t1-excursion-tomography/results/t1_specs.txt")
