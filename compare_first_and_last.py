from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np


# Directories containing the results

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


# Read generation 0 and final generation

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

            # Individual change
            "change_coverage":
                last["coverage"] - first["coverage"],

            "change_collisions":
                last["collisions"] - first["collisions"],
        })


# Print individual results

print("\n" + "=" * 100)
print("INDIVIDUAL RUNS: GENERATION 0 → FINAL")
print("=" * 100)

for r in results:

    print(
        f"{r['directory']:25}"
        f"{r['file']:28}"
        f" coverage: "
        f"{r['initial_coverage']:.3f}"
        f" → {r['final_coverage']:.3f}"
        f"  Δ={r['change_coverage']:+.3f}"
        f" | collisions: "
        f"{r['initial_collisions']:.3f}"
        f" → {r['final_collisions']:.3f}"
        f"  Δ={r['change_collisions']:+.3f}"
    )


# Mean ± SD by condition

print("\n" + "=" * 100)
print("SUMMARY BY CONDITION")
print("=" * 100)

print(
    "\nValues are mean ± standard deviation across runs.\n"
)

condition_stats = {}

for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    # ---------------------------------------------
    # Coverage
    # ---------------------------------------------

    initial_coverage = np.array([
        r["initial_coverage"]
        for r in condition_results
    ])

    final_coverage = np.array([
        r["final_coverage"]
        for r in condition_results
    ])

    change_coverage = np.array([
        r["change_coverage"]
        for r in condition_results
    ])

    # ---------------------------------------------
    # Collisions
    # ---------------------------------------------

    initial_collisions = np.array([
        r["initial_collisions"]
        for r in condition_results
    ])

    final_collisions = np.array([
        r["final_collisions"]
        for r in condition_results
    ])

    change_collisions = np.array([
        r["change_collisions"]
        for r in condition_results
    ])

    # ---------------------------------------------
    # Calculate statistics
    # ddof=1 gives sample standard deviation
    # ---------------------------------------------

    condition_stats[name] = {

        "n": len(condition_results),

        "initial_coverage_mean":
            np.mean(initial_coverage),

        "initial_coverage_sd":
            np.std(initial_coverage, ddof=1),

        "final_coverage_mean":
            np.mean(final_coverage),

        "final_coverage_sd":
            np.std(final_coverage, ddof=1),

        "change_coverage_mean":
            np.mean(change_coverage),

        "change_coverage_sd":
            np.std(change_coverage, ddof=1),

        "initial_collisions_mean":
            np.mean(initial_collisions),

        "initial_collisions_sd":
            np.std(initial_collisions, ddof=1),

        "final_collisions_mean":
            np.mean(final_collisions),

        "final_collisions_sd":
            np.std(final_collisions, ddof=1),

        "change_collisions_mean":
            np.mean(change_collisions),

        "change_collisions_sd":
            np.std(change_collisions, ddof=1),
    }


# Print summary

for name, stats in condition_stats.items():

    print(f"\n{name}  (n={stats['n']})")

    print(
        f"  Coverage:"
        f"  {stats['initial_coverage_mean']:.3f}"
        f" ± {stats['initial_coverage_sd']:.3f}"
        f" → "
        f"{stats['final_coverage_mean']:.3f}"
        f" ± {stats['final_coverage_sd']:.3f}"
        f" | Δ = "
        f"{stats['change_coverage_mean']:+.3f}"
        f" ± {stats['change_coverage_sd']:.3f}"
    )

    print(
        f"  Collisions:"
        f"  {stats['initial_collisions_mean']:.3f}"
        f" ± {stats['initial_collisions_sd']:.3f}"
        f" → "
        f"{stats['final_collisions_mean']:.3f}"
        f" ± {stats['final_collisions_sd']:.3f}"
        f" | Δ = "
        f"{stats['change_collisions_mean']:+.3f}"
        f" ± {stats['change_collisions_sd']:.3f}"
    )


# Plot 1:
# Coverage change vs collision change

plt.figure(figsize=(10, 8))

for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    x = np.array([
        r["change_coverage"]
        for r in condition_results
    ])

    y = np.array([
        r["change_collisions"]
        for r in condition_results
    ])

    # Individual runs
    plt.scatter(
        x,
        y,
        color=colours.get(name, "gray"),
        s=70,
        alpha=0.45,
        label=name,
    )

    stats = condition_stats[name]

    # Mean point
    mean_x = stats["change_coverage_mean"]
    mean_y = stats["change_collisions_mean"]

    plt.scatter(
        mean_x,
        mean_y,
        color=colours.get(name, "gray"),
        edgecolor="black",
        linewidth=2,
        s=180,
        marker="X",
        zorder=5,
    )

    # Horizontal SD error bar
    plt.errorbar(
        mean_x,
        mean_y,
        xerr=stats["change_coverage_sd"],
        yerr=stats["change_collisions_sd"],
        fmt="none",
        ecolor=colours.get(name, "gray"),
        elinewidth=2,
        capsize=5,
        alpha=0.8,
        zorder=4,
    )


# Reference lines

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
    "Change in coverage (final − initial)"
)

plt.ylabel(
    "Change in collisions (final − initial)"
)

plt.title(
    "Change in Coverage and Collisions\n"
    "Generation 0 → Final Generation"
)

plt.grid(
    True,
    alpha=0.3,
)

plt.legend()

plt.tight_layout()
plt.show()


# Plot 2:
# Coverage — initial vs final

condition_names = list(condition_stats.keys())

x = np.arange(len(condition_names))
width = 0.35

initial_means = [
    condition_stats[name]["initial_coverage_mean"]
    for name in condition_names
]

initial_sds = [
    condition_stats[name]["initial_coverage_sd"]
    for name in condition_names
]

final_means = [
    condition_stats[name]["final_coverage_mean"]
    for name in condition_names
]

final_sds = [
    condition_stats[name]["final_coverage_sd"]
    for name in condition_names
]


plt.figure(figsize=(11, 7))

plt.bar(
    x - width / 2,
    initial_means,
    width,
    yerr=initial_sds,
    capsize=5,
    label="Generation 0",
    color="lightgray",
)

plt.bar(
    x + width / 2,
    final_means,
    width,
    yerr=final_sds,
    capsize=5,
    label="Final generation",
    color=[
        colours[name]
        for name in condition_names
    ],
)


plt.xticks(
    x,
    condition_names,
)

plt.ylabel("Coverage")
plt.title(
    "Coverage: Generation 0 vs Final Generation"
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()
plt.show()


# Plot 3:
# Collisions — initial vs final

initial_means = [
    condition_stats[name]["initial_collisions_mean"]
    for name in condition_names
]

initial_sds = [
    condition_stats[name]["initial_collisions_sd"]
    for name in condition_names
]

final_means = [
    condition_stats[name]["final_collisions_mean"]
    for name in condition_names
]

final_sds = [
    condition_stats[name]["final_collisions_sd"]
    for name in condition_names
]


plt.figure(figsize=(11, 7))

plt.bar(
    x - width / 2,
    initial_means,
    width,
    yerr=initial_sds,
    capsize=5,
    label="Generation 0",
    color="lightgray",
)

plt.bar(
    x + width / 2,
    final_means,
    width,
    yerr=final_sds,
    capsize=5,
    label="Final generation",
    color=[
        colours[name]
        for name in condition_names
    ],
)


plt.xticks(
    x,
    condition_names,
)

plt.ylabel("Collisions")
plt.title(
    "Collisions: Generation 0 vs Final Generation"
)

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.legend()

plt.tight_layout()
plt.show()


# Plot 4:
# Change in coverage with SD

coverage_changes = [
    condition_stats[name]["change_coverage_mean"]
    for name in condition_names
]

coverage_change_sds = [
    condition_stats[name]["change_coverage_sd"]
    for name in condition_names
]


plt.figure(figsize=(11, 7))

bars = plt.bar(
    condition_names,
    coverage_changes,
    yerr=coverage_change_sds,
    capsize=6,
    color=[
        colours[name]
        for name in condition_names
    ],
)


plt.axhline(
    0,
    color="black",
    linewidth=1,
)


plt.ylabel(
    "Change in coverage (final − initial)"
)

plt.title(
    "Coverage Change: Generation 0 → Final\n"
    "Mean ± SD"
)


for bar, mean, sd in zip(
    bars,
    coverage_changes,
    coverage_change_sds,
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        mean,
        f"{mean:+.2f}\n± {sd:.2f}",
        ha="center",
        va="bottom" if mean >= 0 else "top",
    )


plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()


# Plot 5:
# Change in collisions with SD

collision_changes = [
    condition_stats[name]["change_collisions_mean"]
    for name in condition_names
]

collision_change_sds = [
    condition_stats[name]["change_collisions_sd"]
    for name in condition_names
]


plt.figure(figsize=(11, 7))

bars = plt.bar(
    condition_names,
    collision_changes,
    yerr=collision_change_sds,
    capsize=6,
    color=[
        colours[name]
        for name in condition_names
    ],
)


plt.axhline(
    0,
    color="black",
    linewidth=1,
)


plt.ylabel(
    "Change in collisions (final − initial)"
)

plt.title(
    "Collision Change: Generation 0 → Final\n"
    "Mean ± SD"
)


for bar, mean, sd in zip(
    bars,
    collision_changes,
    collision_change_sds,
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        mean,
        f"{mean:+.2f}\n± {sd:.2f}",
        ha="center",
        va="bottom" if mean >= 0 else "top",
    )


plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()
