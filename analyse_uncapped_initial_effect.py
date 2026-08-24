from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import pearsonr, spearmanr


# Configuration

DIRECTORY = Path("uncapped")


# Read generation 0 and final generation from every file

results = []

files = sorted(
    DIRECTORY.glob("population_winners_*.jsonl")
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
        "file": f.name,

        # Starting population
        "initial_coverage": first["coverage"],
        "initial_collisions": first["collisions"],

        # Final population
        "final_coverage": last["coverage"],
        "final_collisions": last["collisions"],
    })


# Check number of runs

print("=" * 70)
print("INITIAL POPULATION EFFECT — UNCAPPED RUNS")
print("=" * 70)

print(
    f"\nFound {len(results)} runs in '{DIRECTORY}'."
)

if len(results) < 3:
    raise RuntimeError(
        "Not enough runs for correlation analysis."
    )


# Print starting-population statistics

initial_coverage = np.array([
    r["initial_coverage"]
    for r in results
])

initial_collisions = np.array([
    r["initial_collisions"]
    for r in results
])

final_coverage = np.array([
    r["final_coverage"]
    for r in results
])

final_collisions = np.array([
    r["final_collisions"]
    for r in results
])


print("\nStarting population variation:")
print(
    f"Initial coverage:   "
    f"mean={np.mean(initial_coverage):.3f}, "
    f"SD={np.std(initial_coverage, ddof=1):.3f}, "
    f"min={np.min(initial_coverage):.3f}, "
    f"max={np.max(initial_coverage):.3f}"
)

print(
    f"Initial collisions: "
    f"mean={np.mean(initial_collisions):.3f}, "
    f"SD={np.std(initial_collisions, ddof=1):.3f}, "
    f"min={np.min(initial_collisions):.3f}, "
    f"max={np.max(initial_collisions):.3f}"
)


# Correlation analysis

relationships = [
    (
        "Initial coverage",
        "Final coverage",
        initial_coverage,
        final_coverage,
    ),
    (
        "Initial collisions",
        "Final collisions",
        initial_collisions,
        final_collisions,
    ),
    (
        "Initial coverage",
        "Final collisions",
        initial_coverage,
        final_collisions,
    ),
    (
        "Initial collisions",
        "Final coverage",
        initial_collisions,
        final_coverage,
    ),
]


print("\n")
print("=" * 70)
print("CORRELATION ANALYSIS")
print("=" * 70)


for x_name, y_name, x, y in relationships:

    pearson_r, pearson_p = pearsonr(x, y)

    spearman_rho, spearman_p = spearmanr(x, y)

    print(f"\n{x_name} -> {y_name}")
    print(
        f"  Pearson r  = {pearson_r:+.3f}"
        f"    p = {pearson_p:.4f}"
    )
    print(
        f"  Spearman ρ = {spearman_rho:+.3f}"
        f"    p = {spearman_p:.4f}"
    )


# Scatter plots

fig, axes = plt.subplots(
    2,
    2,
    figsize=(12, 10),
)


plot_pairs = [
    (
        "Initial coverage",
        "Final coverage",
        initial_coverage,
        final_coverage,
    ),
    (
        "Initial collisions",
        "Final collisions",
        initial_collisions,
        final_collisions,
    ),
    (
        "Initial coverage",
        "Final collisions",
        initial_coverage,
        final_collisions,
    ),
    (
        "Initial collisions",
        "Final coverage",
        initial_collisions,
        final_coverage,
    ),
]


for ax, (x_label, y_label, x, y) in zip(
    axes.flat,
    plot_pairs,
):

    pearson_r, pearson_p = pearsonr(x, y)

    # Individual runs
    ax.scatter(
        x,
        y,
        color="tab:blue",
        alpha=0.6,
        s=60,
    )

    # Regression line
    slope, intercept = np.polyfit(x, y, 1)

    x_line = np.linspace(
        np.min(x),
        np.max(x),
        100,
    )

    y_line = (
        slope * x_line
        + intercept
    )

    ax.plot(
        x_line,
        y_line,
        color="black",
        linewidth=2,
    )

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    ax.set_title(
        f"{x_label} vs {y_label}\n"
        f"Pearson r = {pearson_r:+.3f}, "
        f"p = {pearson_p:.4f}"
    )

    ax.grid(
        True,
        alpha=0.3,
    )


fig.suptitle(
    "Effect of Initial Population on Final Outcome\n"
    "Uncapped Runs",
    fontsize=15,
)


plt.tight_layout()
plt.show()


# Simple interpretation

print("\n")
print("=" * 70)
print("INTERPRETATION")
print("=" * 70)

print(
    """
These tests examine whether variation in the independently
generated initial populations predicts the final outcomes.

A small correlation indicates that runs which happened to
start with higher/lower coverage or collisions did not
systematically finish with higher/lower values.

A statistically significant correlation (p < 0.05) would
indicate evidence that the corresponding starting property
is related to the final outcome.

A non-significant result should not be described as proving
that the initial population has 'no effect'; it means that
no statistically significant relationship was detected.
"""
)
