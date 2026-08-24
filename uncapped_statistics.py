from pathlib import Path
import json

import numpy as np
from scipy.stats import pearsonr, spearmanr


# CONFIGURATION

DIRECTORY = Path("uncapped")


# READ FIRST AND LAST GENERATION FROM EACH RUN

results = []

files = sorted(DIRECTORY.glob("population_winners_*.jsonl"))

for f in files:

    first = None
    last = None
    n_generations = 0

    with f.open() as fp:

        for line in fp:

            line = line.strip()

            if not line:
                continue

            data = json.loads(line)

            if first is None:
                first = data

            last = data
            n_generations += 1

    if first is None or last is None:
        continue

    results.append({
        "file": f.name,

        "initial_coverage": first["coverage"],
        "initial_collisions": first["collisions"],

        "final_coverage": last["coverage"],
        "final_collisions": last["collisions"],

        "coverage_change": (
            last["coverage"] - first["coverage"]
        ),

        "collision_change": (
            last["collisions"] - first["collisions"]
        ),

        "generations": n_generations,
    })


# BASIC CHECK

print("=" * 80)
print("INITIAL-CONDITION SENSITIVITY ANALYSIS")
print("=" * 80)

print(f"\nDirectory: {DIRECTORY}")
print(f"Runs found: {len(results)}")

if len(results) < 3:
    raise RuntimeError("Not enough runs for analysis.")


# ARRAYS

initial_coverage = np.array([
    r["initial_coverage"] for r in results
])

initial_collisions = np.array([
    r["initial_collisions"] for r in results
])

final_coverage = np.array([
    r["final_coverage"] for r in results
])

final_collisions = np.array([
    r["final_collisions"] for r in results
])

coverage_change = np.array([
    r["coverage_change"] for r in results
])

collision_change = np.array([
    r["collision_change"] for r in results
])


# 1. RAW DATA — THIS IS THE MOST IMPORTANT PART

print("\n")
print("=" * 80)
print("PER-RUN DATA")
print("=" * 80)

print(
    "\n"
    "Run | Initial coverage | Initial collisions | "
    "Final coverage | Final collisions | "
    "Coverage change | Collision change | Generations"
)

print("-" * 80)

for i, r in enumerate(results, start=1):

    print(
        f"{i:3d} | "
        f"{r['initial_coverage']:16.6f} | "
        f"{r['initial_collisions']:18.6f} | "
        f"{r['final_coverage']:14.6f} | "
        f"{r['final_collisions']:16.6f} | "
        f"{r['coverage_change']:+15.6f} | "
        f"{r['collision_change']:+16.6f} | "
        f"{r['generations']:11d}"
    )


# 2. INITIAL-CONDITION VARIATION

print("\n")
print("=" * 80)
print("INITIAL-CONDITION VARIATION")
print("=" * 80)


def describe(name, x):

    print(f"\n{name}")

    print(f"  Mean:   {np.mean(x):.6f}")
    print(f"  SD:     {np.std(x, ddof=1):.6f}")
    print(f"  Min:    {np.min(x):.6f}")
    print(f"  Max:    {np.max(x):.6f}")
    print(f"  Range:  {np.ptp(x):.6f}")

    if np.mean(x) != 0:
        print(
            f"  CV:     "
            f"{np.std(x, ddof=1) / abs(np.mean(x)):.6f}"
        )


describe(
    "Initial coverage",
    initial_coverage,
)

describe(
    "Initial collisions",
    initial_collisions,
)


# 3. FINAL-OUTCOME VARIATION

print("\n")
print("=" * 80)
print("FINAL-OUTCOME VARIATION")
print("=" * 80)

describe(
    "Final coverage",
    final_coverage,
)

describe(
    "Final collisions",
    final_collisions,
)


# 4. HOW MUCH DID THE POPULATIONS CHANGE?

print("\n")
print("=" * 80)
print("CHANGE FROM INITIAL TO FINAL")
print("=" * 80)

describe(
    "Coverage change (final - initial)",
    coverage_change,
)

describe(
    "Collision change (final - initial)",
    collision_change,
)


# 5. CORRELATIONS

print("\n")
print("=" * 80)
print("INITIAL CONDITIONS -> FINAL OUTCOMES")
print("=" * 80)


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


for x_name, y_name, x, y in relationships:

    pearson_r, pearson_p = pearsonr(x, y)
    spearman_rho, spearman_p = spearmanr(x, y)

    print(f"\n{x_name} -> {y_name}")

    print(
        f"  Pearson:   r = {pearson_r:+.6f}, "
        f"p = {pearson_p:.6f}"
    )

    print(
        f"  Spearman:  ρ = {spearman_rho:+.6f}, "
        f"p = {spearman_p:.6f}"
    )


# 6. CORRELATION WITH THE AMOUNT OF IMPROVEMENT

print("\n")
print("=" * 80)
print("INITIAL CONDITIONS -> AMOUNT OF CHANGE")
print("=" * 80)

change_relationships = [
    (
        "Initial coverage",
        "Coverage change",
        initial_coverage,
        coverage_change,
    ),
    (
        "Initial coverage",
        "Collision change",
        initial_coverage,
        collision_change,
    ),
    (
        "Initial collisions",
        "Coverage change",
        initial_collisions,
        coverage_change,
    ),
    (
        "Initial collisions",
        "Collision change",
        initial_collisions,
        collision_change,
    ),
]


for x_name, y_name, x, y in change_relationships:

    pearson_r, pearson_p = pearsonr(x, y)
    spearman_rho, spearman_p = spearmanr(x, y)

    print(f"\n{x_name} -> {y_name}")

    print(
        f"  Pearson:   r = {pearson_r:+.6f}, "
        f"p = {pearson_p:.6f}"
    )

    print(
        f"  Spearman:  ρ = {spearman_rho:+.6f}, "
        f"p = {spearman_p:.6f}"
    )


# 7. STANDARDISED EFFECT SIZE

print("\n")
print("=" * 80)
print("INITIAL VS FINAL VARIABILITY")
print("=" * 80)

initial_cov_sd = np.std(initial_coverage, ddof=1)
final_cov_sd = np.std(final_coverage, ddof=1)

initial_col_sd = np.std(initial_collisions, ddof=1)
final_col_sd = np.std(final_collisions, ddof=1)

print(
    f"\nCoverage:"
    f"\n  Initial SD = {initial_cov_sd:.6f}"
    f"\n  Final SD   = {final_cov_sd:.6f}"
)

if initial_cov_sd > 0:
    print(
        f"  Final/initial SD ratio = "
        f"{final_cov_sd / initial_cov_sd:.6f}"
    )

print(
    f"\nCollisions:"
    f"\n  Initial SD = {initial_col_sd:.6f}"
    f"\n  Final SD   = {final_col_sd:.6f}"
)

if initial_col_sd > 0:
    print(
        f"  Final/initial SD ratio = "
        f"{final_col_sd / initial_col_sd:.6f}"
    )


# 8. EXTREME-RUN CHECK

print("\n")
print("=" * 80)
print("EXTREME INITIAL CONDITIONS")
print("=" * 80)

best_initial_coverage = np.argmax(initial_coverage)
worst_initial_coverage = np.argmin(initial_coverage)

best_initial_collisions = np.argmin(initial_collisions)
worst_initial_collisions = np.argmax(initial_collisions)

print(
    "\nHighest initial coverage:"
)
print(
    f"  {results[best_initial_coverage]['file']}"
)
print(
    f"  initial coverage = "
    f"{initial_coverage[best_initial_coverage]:.6f}"
)
print(
    f"  final coverage   = "
    f"{final_coverage[best_initial_coverage]:.6f}"
)

print(
    "\nLowest initial coverage:"
)
print(
    f"  {results[worst_initial_coverage]['file']}"
)
print(
    f"  initial coverage = "
    f"{initial_coverage[worst_initial_coverage]:.6f}"
)
print(
    f"  final coverage   = "
    f"{final_coverage[worst_initial_coverage]:.6f}"
)

print(
    "\nLowest initial collisions:"
)
print(
    f"  {results[best_initial_collisions]['file']}"
)
print(
    f"  initial collisions = "
    f"{initial_collisions[best_initial_collisions]:.6f}"
)
print(
    f"  final collisions   = "
    f"{final_collisions[best_initial_collisions]:.6f}"
)

print(
    "\nHighest initial collisions:"
)
print(
    f"  {results[worst_initial_collisions]['file']}"
)
print(
    f"  initial collisions = "
    f"{initial_collisions[worst_initial_collisions]:.6f}"
)
print(
    f"  final collisions   = "
    f"{final_collisions[worst_initial_collisions]:.6f}"
)


# 9. SUMMARY

print("\n")
print("=" * 80)
print("SUMMARY")
print("=" * 80)

print(
    f"""
Number of runs: {len(results)}

Initial coverage:
  mean = {np.mean(initial_coverage):.6f}
  SD   = {np.std(initial_coverage, ddof=1):.6f}
  range = {np.min(initial_coverage):.6f}
          to
          {np.max(initial_coverage):.6f}

Initial collisions:
  mean = {np.mean(initial_collisions):.6f}
  SD   = {np.std(initial_collisions, ddof=1):.6f}
  range = {np.min(initial_collisions):.6f}
          to
          {np.max(initial_collisions):.6f}

Final coverage:
  mean = {np.mean(final_coverage):.6f}
  SD   = {np.std(final_coverage, ddof=1):.6f}

Final collisions:
  mean = {np.mean(final_collisions):.6f}
  SD   = {np.std(final_collisions, ddof=1):.6f}

Mean coverage change:
  {np.mean(coverage_change):+.6f}

Mean collision change:
  {np.mean(collision_change):+.6f}
"""
)

print("=" * 80)
print("END OF DATA")
print("=" * 80)
