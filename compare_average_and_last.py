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
# Mean change by condition
# ---------------------------------------------------------

print("\nMean change by condition:\n")

condition_means = {}

for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    mean_coverage = np.mean([
        r["change_coverage"]
        for r in condition_results
    ])

    mean_collisions = np.mean([
        r["change_collisions"]
        for r in condition_results
    ])

    condition_means[name] = {
        "coverage": mean_coverage,
        "collisions": mean_collisions,
    }

    print(
        f"{name:25}"
        f" Δcoverage={mean_coverage:+.3f}"
        f" | Δcollisions={mean_collisions:+.3f}"
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

    # Individual runs
    plt.scatter(
        x,
        y,
        color=colours[name],
        s=70,
        alpha=0.5,
        label=name,
    )

    # Mean for condition
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
# Plot: Mean change in coverage
# ---------------------------------------------------------

condition_names = list(condition_means.keys())

mean_coverage_changes = [
    condition_means[name]["coverage"]
    for name in condition_names
]


plt.figure(figsize=(10, 6))

bars = plt.bar(
    condition_names,
    mean_coverage_changes,
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

plt.ylabel("Change in coverage")
plt.title(
    "Mean Coverage Change from Common Generation-0 Baseline"
)

for bar, value in zip(
    bars,
    mean_coverage_changes,
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:+.3f}",
        ha="center",
        va="bottom" if value >= 0 else "top",
    )

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()


# ---------------------------------------------------------
# Plot: Mean change in collisions
# ---------------------------------------------------------

mean_collision_changes = [
    condition_means[name]["collisions"]
    for name in condition_names
]


plt.figure(figsize=(10, 6))

bars = plt.bar(
    condition_names,
    mean_collision_changes,
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

plt.ylabel("Change in collisions")
plt.title(
    "Mean Collision Change from Common Generation-0 Baseline"
)

for bar, value in zip(
    bars,
    mean_collision_changes,
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value,
        f"{value:+.3f}",
        ha="center",
        va="bottom" if value >= 0 else "top",
    )

plt.grid(
    axis="y",
    alpha=0.3,
)

plt.tight_layout()
plt.show()
