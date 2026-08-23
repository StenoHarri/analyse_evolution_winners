from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np


# ---------------------------------------------------------
# Directories containing the results
# ---------------------------------------------------------

directories = [
    Path("uncapped"),
    Path("one_cap"),
    Path("point_four_cap"),
    Path("point_seven_five_cap"),
]


colours = {
    "uncapped": "tab:blue",
    "one_cap": "tab:orange",
    "point_four_cap": "tab:green",
    "point_seven_five_cap": "tab:red",
}


# ---------------------------------------------------------
# Read generation 0 and final generation from every file
# ---------------------------------------------------------

results = []

for directory in directories:

    files = sorted(
        directory.glob("population_winners_*.jsonl")
    )

    for f in files:

        first = None
        last = None

        with f.open() as fp:

            for line in fp:

                line = line.strip()

                if not line:
                    continue

                data = json.loads(line)

                if first is None:
                    first = data

                last = data

        if first is None or last is None:
            continue

        results.append({
            "directory": directory.name,
            "file": f.name,

            # Generation 0
            "initial_coverage": first["coverage"],
            "initial_collisions": first["collisions"],

            # Final generation
            "final_coverage": last["coverage"],
            "final_collisions": last["collisions"],
        })


# ---------------------------------------------------------
# Calculate ONE common baseline
# ---------------------------------------------------------

baseline_coverage = np.mean([
    r["initial_coverage"]
    for r in results
])

baseline_collisions = np.mean([
    r["initial_collisions"]
    for r in results
])


print("\nCommon generation-0 baseline:")
print(f"Coverage   = {baseline_coverage:.3f}")
print(f"Collisions = {baseline_collisions:.3f}")


# ---------------------------------------------------------
# Calculate change relative to common baseline
# ---------------------------------------------------------

for r in results:

    r["change_coverage"] = (
        r["final_coverage"]
        - baseline_coverage
    )

    r["change_collisions"] = (
        r["final_collisions"]
        - baseline_collisions
    )


# ---------------------------------------------------------
# Print individual results
# ---------------------------------------------------------

print("\nChange from common generation-0 baseline:\n")

for r in results:

    print(
        f"{r['directory']:25}"
        f"{r['file']:28}"
        f" coverage={r['final_coverage']:.3f}"
        f"  Δcoverage={r['change_coverage']:+.3f}"
        f" | collisions={r['final_collisions']:.3f}"
        f"  Δcollisions={r['change_collisions']:+.3f}"
    )


# ---------------------------------------------------------
# Calculate mean AND standard deviation by condition
# ---------------------------------------------------------

print("\nMean change by condition (± SD):\n")

condition_stats = {}


for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    coverage_changes = np.array([
        r["change_coverage"]
        for r in condition_results
    ])

    collision_changes = np.array([
        r["change_collisions"]
        for r in condition_results
    ])

    # Mean
    mean_coverage = np.mean(coverage_changes)
    mean_collisions = np.mean(collision_changes)

    # Sample standard deviation
    #
    # ddof=1 means this is the sample SD rather than
    # the population SD.
    #
    # If there is only one run, SD is undefined.
    if len(coverage_changes) > 1:
        sd_coverage = np.std(
            coverage_changes,
            ddof=1,
        )
    else:
        sd_coverage = 0.0

    if len(collision_changes) > 1:
        sd_collisions = np.std(
            collision_changes,
            ddof=1,
        )
    else:
        sd_collisions = 0.0

    condition_stats[name] = {
        "n": len(condition_results),

        "coverage_mean": mean_coverage,
        "coverage_sd": sd_coverage,

        "collisions_mean": mean_collisions,
        "collisions_sd": sd_collisions,
    }

    print(
        f"{name:25}"
        f" n={len(condition_results):2d}"
        f" | Δcoverage={mean_coverage:+.3f}"
        f" ± {sd_coverage:.3f}"
        f" | Δcollisions={mean_collisions:+.3f}"
        f" ± {sd_collisions:.3f}"
    )


# ---------------------------------------------------------
# More compact table for copying into report
# ---------------------------------------------------------

print("\n\nResults table:\n")

print(
    f"{'Condition':25}"
    f"{'n':>5}"
    f"{'Δ Coverage':>18}"
    f"{'Δ Collisions':>20}"
)

print("-" * 68)


for name in condition_stats:

    stats = condition_stats[name]

    print(
        f"{name:25}"
        f"{stats['n']:>5}"
        f"{stats['coverage_mean']:>8.3f} ± "
        f"{stats['coverage_sd']:<7.3f}"
        f"{stats['collisions_mean']:>8.3f} ± "
        f"{stats['collisions_sd']:<7.3f}"
    )


# ---------------------------------------------------------
# Plot: Coverage change vs collision change
# ---------------------------------------------------------

plt.figure(figsize=(10, 8))


for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    x = [
        r["change_coverage"]
        for r in condition_results
    ]

    y = [
        r["change_collisions"]
        for r in condition_results
    ]

    # -----------------------------------------------------
    # Individual runs
    # -----------------------------------------------------

    plt.scatter(
        x,
        y,
        color=colours[name],
        s=70,
        alpha=0.5,
        label=name,
    )

    # -----------------------------------------------------
    # Mean for condition
    # -----------------------------------------------------

    mean_x = np.mean(x)
    mean_y = np.mean(y)

    plt.scatter(
        mean_x,
        mean_y,
        color=colours[name],
        edgecolor="black",
        linewidth=2,
        s=200,
        marker="X",
        zorder=5,
    )

    # -----------------------------------------------------
    # Standard deviation error bars
    # -----------------------------------------------------

    sd_x = (
        np.std(x, ddof=1)
        if len(x) > 1
        else 0
    )

    sd_y = (
        np.std(y, ddof=1)
        if len(y) > 1
        else 0
    )

    plt.errorbar(
        mean_x,
        mean_y,
        xerr=sd_x,
        yerr=sd_y,
        color=colours[name],
        linewidth=2,
        capsize=5,
        zorder=4,
    )


# Zero-change reference lines

plt.axhline(
    0,
    color="black",
    linewidth=1,
    alpha=0.5,
)

plt.axvline(
    0,
    color="black",
    linewidth=1,
    alpha=0.5,
)


plt.xlabel(
    "Change in coverage from common baseline"
)

plt.ylabel(
    "Change in collisions from common baseline"
)

plt.title(
    "Final Generation Relative to Common Generation-0 Baseline"
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()
plt.show()


# ---------------------------------------------------------
# Plot: Mean change in coverage ± SD
# ---------------------------------------------------------

condition_names = list(condition_stats.keys())


mean_coverage_changes = [
    condition_stats[name]["coverage_mean"]
    for name in condition_names
]

sd_coverage_changes = [
    condition_stats[name]["coverage_sd"]
    for name in condition_names
]


plt.figure(figsize=(10, 6))


bars = plt.bar(
    condition_names,
    mean_coverage_changes,
    yerr=sd_coverage_changes,
    capsize=6,
    color=[
        colours[name]
        for name in condition_names
    ],
    alpha=0.8,
)


plt.axhline(
    0,
    color="black",
    linewidth=1,
)


plt.ylabel(
    "Change in coverage"
)

plt.title(
    "Mean Coverage Change from Common Generation-0 Baseline\n"
    "Error bars = ±1 SD"
)


# Add mean values above bars

for bar, value, sd in zip(
    bars,
    mean_coverage_changes,
    sd_coverage_changes,
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + sd,
        f"{value:+.2f}",
        ha="center",
        va="bottom",
    )


plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()


# ---------------------------------------------------------
# Plot: Mean change in collisions ± SD
# ---------------------------------------------------------

mean_collision_changes = [
    condition_stats[name]["collisions_mean"]
    for name in condition_names
]

sd_collision_changes = [
    condition_stats[name]["collisions_sd"]
    for name in condition_names
]


plt.figure(figsize=(10, 6))


bars = plt.bar(
    condition_names,
    mean_collision_changes,
    yerr=sd_collision_changes,
    capsize=6,
    color=[
        colours[name]
        for name in condition_names
    ],
    alpha=0.8,
)


plt.axhline(
    0,
    color="black",
    linewidth=1,
)


plt.ylabel(
    "Change in collisions"
)

plt.title(
    "Mean Collision Change from Common Generation-0 Baseline\n"
    "Error bars = ±1 SD"
)


# Add mean values above/below bars

for bar, value, sd in zip(
    bars,
    mean_collision_changes,
    sd_collision_changes,
):

    if value >= 0:

        y_position = value + sd
        vertical_alignment = "bottom"

    else:

        y_position = value - sd
        vertical_alignment = "top"

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        y_position,
        f"{value:+.2f}",
        ha="center",
        va=vertical_alignment,
    )


plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()
