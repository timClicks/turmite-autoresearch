#!/usr/bin/env python3
"""
Analysis of T1 excursion tomography data (experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv).
Tests pre-registered predictions from notes/excursion-tomography-2026-10-13.md.
"""

import json
import math
import sys
import polars as pl
import numpy as np
from scipy import stats

def parse_pairs(pairs_file):
    pairs = []
    with open(pairs_file) as f:
        for line in f:
            line = line.strip()
            if line.startswith("('") and line.endswith(")"):
                # e.g. ('RRLRLRRRL', 'RRLRRRLRL', 0.346, 0.347, 0.97, 1.72)
                parts = eval(line)
                r1, r2, c1, c2, k1, k2 = parts
                # ensure r_low has smaller kappa than r_high
                if k1 < k2:
                    pairs.append((r1, r2, c1, c2, k1, k2))
                else:
                    pairs.append((r2, r1, c2, c1, k2, k1))
    return pairs

def main():
    csv_path = "experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.csv"
    pairs_path = "experiments/archive/2026-10-arm-kappa-depletion-arms/results/armc_pairs.txt"

    df = pl.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")

    # Instrument checks
    exact_all = df["exact_budget"].all()
    escaped_any = (df["escaped"] != "fals").any()
    print(f"Instrument check 1: Exact budget satisfied for 100% of rows: {exact_all}")
    print(f"Instrument check 2: Any escapes: {escaped_any}")

    # Check controls
    rotor_df = df.filter(pl.col("spec").str.starts_with("rotor:"))
    rw_df = df.filter(pl.col("spec").str.starts_with("rw:"))
    print(f"Rotor controls (N={len(rotor_df)}): mean kappa={rotor_df['kappa'].mean():.3f}, c={rotor_df['c'].mean():.3f}")
    print(f"Random walk controls (N={len(rw_df)}): mean kappa={rw_df['kappa'].mean():.3f}, c={rw_df['c'].mean():.3f}")

    # Split patched vs blank
    # Patched specs contain '@'
    patched_df = df.filter(pl.col("spec").str.contains("@"))
    blank_df = df.filter(~pl.col("spec").str.contains("@") & ~pl.col("spec").str.starts_with("rotor:") & ~pl.col("spec").str.starts_with("rw:"))

    # Add rule and seed columns for patched
    patched_df = patched_df.with_columns([
        pl.col("spec").str.split("@").list.get(0).alias("rule"),
        pl.col("spec").str.split("@").list.get(1).cast(pl.Int32).alias("seed")
    ])

    pairs = parse_pairs(pairs_path)
    print(f"Loaded {len(pairs)} matched pairs from {pairs_path}")

    # Analyze window k=25 (largest completed octave 2^25 -> 2^26)
    k_target = 25
    p_k = patched_df.filter(pl.col("k") == k_target)

    # Compute rule means and sds over seeds
    rule_stats = p_k.group_by("rule").agg([
        pl.col("kappa").mean().alias("kappa_mean"),
        pl.col("kappa").std().alias("kappa_sd"),
        pl.col("c").mean().alias("c_mean"),
        pl.col("edge_dwell_mean").mean().alias("dwell_mean"),
        pl.col("l_med").mean().alias("l_med_mean"),
        pl.col("l_med").std().alias("l_med_sd"),
        pl.col("l_mean").mean().alias("l_mean_mean"),
        pl.col("l_max").mean().alias("l_max_mean"),
        pl.col("top1_share").mean().alias("top1_mean"),
        pl.col("top1_share").std().alias("top1_sd"),
        pl.col("top5_share").mean().alias("top5_mean"),
        pl.col("unresolved_share").mean().alias("unres_mean"),
        pl.col("disp_med").mean().alias("disp_med_mean"),
        pl.col("disp_mean").mean().alias("disp_mean_mean"),
        pl.col("depth_med").mean().alias("depth_med_mean"),
        pl.col("depth_mean").mean().alias("depth_mean_mean"),
    ]).to_dicts()

    stats_by_rule = {r["rule"]: r for r in rule_stats}

    # Prediction 1: Rare journeys over shallow loops
    # Low-kappa member has larger top1_share in >= 18 of 26 pairs;
    # ratio of paired l_med < 2.0.
    top1_wins = 0
    lmed_ratio_under_2 = 0
    lmed_ratios = []
    top1_diffs = []
    pair_details = []

    for r_low, r_high, c1, c2, k1, k2 in pairs:
        s_low = stats_by_rule.get(r_low)
        s_high = stats_by_rule.get(r_high)
        if not s_low or not s_high:
            continue

        # In case measured kappa ordered differently, keep nominal low/high from pair spec
        # Check top1 share
        top1_diff = s_low["top1_mean"] - s_high["top1_mean"]
        top1_diffs.append(top1_diff)
        if top1_diff > 0:
            top1_wins += 1

        ratio_med = s_low["l_med_mean"] / max(s_high["l_med_mean"], 1e-6)
        lmed_ratios.append(ratio_med)
        if ratio_med < 2.0:
            lmed_ratio_under_2 += 1

        pair_details.append({
            "pair": (r_low, r_high),
            "kappa_low": s_low["kappa_mean"],
            "kappa_high": s_high["kappa_mean"],
            "top1_low": s_low["top1_mean"],
            "top1_high": s_high["top1_mean"],
            "lmed_low": s_low["l_med_mean"],
            "lmed_high": s_high["l_med_mean"],
            "disp_low": s_low["disp_med_mean"],
            "disp_high": s_high["disp_med_mean"],
            "dwell_low": s_low["dwell_mean"],
            "dwell_high": s_high["dwell_mean"],
        })

    n_pairs = len(pair_details)
    sign_test_top1_p = stats.binomtest(top1_wins, n_pairs, 0.5, alternative='greater').pvalue

    print("\n--- TEST OF PREDICTION 1 (Rare journeys vs shallow loops) ---")
    print(f"Top 1% excursion share wins (low-kappa > high-kappa): {top1_wins}/{n_pairs} (p = {sign_test_top1_p:.4f})")
    print(f"Median duration ratio < 2.0: {lmed_ratio_under_2}/{n_pairs}")
    print(f"Mean top1_share diff: {np.mean(top1_diffs):.4f} (median: {np.median(top1_diffs):.4f})")
    print(f"Median duration ratios: mean={np.mean(lmed_ratios):.2f}, median={np.median(lmed_ratios):.2f}, min={np.min(lmed_ratios):.2f}, max={np.max(lmed_ratios):.2f}")

    # Prediction 2: Dwell time invariance
    dwells = [s["dwell_mean"] for s in stats_by_rule.values()]
    print("\n--- TEST OF PREDICTION 2 (Edge dwell invariance) ---")
    print(f"Mean edge dwell: {np.mean(dwells):.3f} +/- {np.std(dwells):.3f} (min={np.min(dwells):.3f}, max={np.max(dwells):.3f})")

    # Prediction 3: Chord transport (displacement vs kappa)
    kappas = [s["kappa_mean"] for s in stats_by_rule.values()]
    disps = [s["disp_med_mean"] for s in stats_by_rule.values()]
    l_meds = [s["l_med_mean"] for s in stats_by_rule.values()]
    top1s = [s["top1_mean"] for s in stats_by_rule.values()]

    rho_disp, p_disp = stats.spearmanr(disps, kappas)
    rho_lmed, p_lmed = stats.spearmanr(l_meds, kappas)
    rho_top1, p_top1 = stats.spearmanr(top1s, kappas)
    rho_dwell, p_dwell = stats.spearmanr(dwells, kappas)

    print("\n--- CORRELATIONS WITH KAPPA ACROSS 44 RULES ---")
    print(f"Spearman rho(D_med/R, kappa): {rho_disp:.3f} (p = {p_disp:.2e})")
    print(f"Spearman rho(top1_share, kappa): {rho_top1:.3f} (p = {p_top1:.2e})")
    print(f"Spearman rho(L_med, kappa): {rho_lmed:.3f} (p = {p_lmed:.2e})")
    print(f"Spearman rho(dwell, kappa): {rho_dwell:.3f} (p = {p_dwell:.2e})")

    # Prediction 4: Early window (k=22) forecasting late kappa (k=25)
    p_k22 = patched_df.filter(pl.col("k") == 22).group_by("rule").agg([
        pl.col("kappa").mean().alias("k22_kappa"),
        pl.col("top1_share").mean().alias("k22_top1"),
        pl.col("l_med").mean().alias("k22_lmed"),
        pl.col("disp_med").mean().alias("k22_disp"),
    ]).to_dicts()
    k22_map = {r["rule"]: r for r in p_k22}

    # LOOCV linear regression predicting late kappa from k22 features
    X_rules = [r for r in stats_by_rule if r in k22_map]
    y_true = np.array([stats_by_rule[r]["kappa_mean"] for r in X_rules])
    
    # Baseline: constant mean
    base_preds = []
    model_preds = []
    for i in range(len(X_rules)):
        train_idx = [j for j in range(len(X_rules)) if j != i]
        # Baseline: train mean
        base_preds.append(np.mean(y_true[train_idx]))
        
        # Fit regression on [k22_top1, k22_disp, k22_lmed]
        X_train = np.array([[k22_map[X_rules[j]]["k22_top1"], k22_map[X_rules[j]]["k22_disp"], k22_map[X_rules[j]]["k22_lmed"]] for j in train_idx])
        y_train = y_true[train_idx]
        X_train_c = np.column_stack([np.ones(len(train_idx)), X_train])
        beta = np.linalg.lstsq(X_train_c, y_train, rcond=None)[0]
        
        X_test = np.array([1.0, k22_map[X_rules[i]]["k22_top1"], k22_map[X_rules[i]]["k22_disp"], k22_map[X_rules[i]]["k22_lmed"]])
        model_preds.append(X_test @ beta)

    base_preds = np.array(base_preds)
    model_preds = np.array(model_preds)
    ss_tot = np.sum((y_true - np.mean(y_true))**2)
    ss_res_base = np.sum((y_true - base_preds)**2)
    ss_res_model = np.sum((y_true - model_preds)**2)
    r2_held_out = 1.0 - ss_res_model / ss_tot

    print("\n--- TEST OF PREDICTION 4 (Held-out forecasting) ---")
    print(f"Held-out R^2 of k=22 excursion features predicting k=25 kappa: {r2_held_out:.3f}")
    print(f"RMSE baseline: {np.sqrt(np.mean((y_true - base_preds)**2)):.3f}, RMSE model: {np.sqrt(np.mean((y_true - model_preds)**2)):.3f}")

    # Blank starts replication
    if len(blank_df) > 0:
        b_k = blank_df.filter(pl.col("k") == k_target)
        b_map = {row["spec"]: row for row in b_k.to_dicts()}
        blank_top1_wins = 0
        blank_usable = 0
        for r_low, r_high, c1, c2, k1, k2 in pairs:
            if r_low in b_map and r_high in b_map:
                blank_usable += 1
                if b_map[r_low]["top1_share"] > b_map[r_high]["top1_share"]:
                    blank_top1_wins += 1
        print("\n--- REPLICATION ON BLANK-BOARD COHORT ---")
        print(f"Blank-board top1_share wins (low-kappa > high-kappa): {blank_top1_wins}/{blank_usable}")

    # Save output summary json
    out_summary = {
        "n_specs": len(df),
        "n_pairs": n_pairs,
        "k_target": k_target,
        "top1_wins": top1_wins,
        "sign_test_top1_p": float(sign_test_top1_p),
        "lmed_ratio_under_2": lmed_ratio_under_2,
        "mean_top1_diff": float(np.mean(top1_diffs)),
        "mean_dwell": float(np.mean(dwells)),
        "std_dwell": float(np.std(dwells)),
        "rho_disp": float(rho_disp),
        "p_disp": float(p_disp),
        "rho_top1": float(rho_top1),
        "p_top1": float(p_top1),
        "rho_lmed": float(rho_lmed),
        "p_lmed": float(p_lmed),
        "r2_held_out": float(r2_held_out),
        "pair_details": pair_details,
    }
    with open("experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.json", "w") as jf:
        json.dump(out_summary, jf, indent=2)
    print("\nSaved detailed results to experiments/archive/2026-10-t1-excursion-tomography/results/t1_excursions.json")

if __name__ == "__main__":
    main()
