"""Combine the contour-radius runs (main generator and alternative generator)
into the page's verdict on the Kapri & Dhar contour comparison."""
import json

main = json.load(open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_contour.json"))
alt = json.load(open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_contour_alt.json"))
kd, kd_se = 145.436, 0.003
z = (main["pooled_ray"] - kd) / (main["se"] ** 2 + kd_se ** 2) ** 0.5
z_alt = (alt["pooled_ray"] - main["pooled_ray"]) / (main["se"] ** 2 + alt["se"] ** 2) ** 0.5
diff = main["pooled_ray"] - kd
verdict = (
    f"Everything matches except one number, by a hair. My contour radius is {main['pooled_ray']:.3f} ± {main['se']:.3f} "
    f"from {main['seeds']:,} starts, against their {kd} ± {kd_se}: a difference of {abs(diff):.3f} cells, or "
    f"{abs(diff) / kd * 100:.2f}%, which is {abs(z):.1f} standard errors. Two interpolation methods (rays, and their "
    f"triangles) give the same radius. The initial arrows pass checks for bias and neighbour correlation, and "
    f"{alt['seeds']:,} further starts with a completely different random generator give {alt['pooled_ray']:.3f} ± {alt['se']:.3f}, "
    f"{abs(z_alt):.1f} standard errors from the main run. So the gap isn't in my generator or my contour-finding. "
    f"The rule variants I could think of (rotating before or after the step, counting the starting site) are "
    f"statistically identical or only affect the origin. I don't know the cause. "
    f"At 0.05% it doesn't touch any exponent, but it's the kind of thing to ask the authors about."
)
json.dump({"final": {"radius": main["pooled_ray"], "se": main["se"], "seeds": main["seeds"]},
           "alt": {"radius": alt["pooled_ray"], "se": alt["se"], "seeds": alt["seeds"]},
           "z": round(z, 2), "z_alt": round(z_alt, 2), "verdict": verdict},
          open("experiments/archive/2026-10-calib-instrument-calibration/results/calib_contour_page.json", "w"), indent=1)
print(verdict)
