import json
from scipy import stats

with open("experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.json") as f:
    d = json.load(f)

print("Pair breakdown (low kappa vs high kappa):")
disp_wins = 0
for p in d["pair_details"]:
    r_low, r_high = p["pair"]
    k_low, k_high = p["kappa_low"], p["kappa_high"]
    d_low, d_high = p["disp_low"], p["disp_high"]
    t_low, t_high = p["top1_low"], p["top1_high"]
    win = d_low > d_high
    if win:
        disp_wins += 1
    print(f"{r_low:<12} (k={k_low:5.2f}, D={d_low:6.4f}, top1={t_low:5.3f}) vs {r_high:<12} (k={k_high:5.2f}, D={d_high:6.4f}, top1={t_high:5.3f}) -> D_win={win}")

n = len(d["pair_details"])
p_val = stats.binomtest(disp_wins, n, 0.5, alternative='greater').pvalue
print(f"\nDisplacement D_med/R wins (low-kappa > high-kappa): {disp_wins}/{n} (sign test p = {p_val:.4e})")
