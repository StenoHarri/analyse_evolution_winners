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

            # Change
            "change_coverage":
                last["coverage"] - first["coverage"],

            "change_collisions":
                last["collisions"] - first["collisions"],
        })


# Print individual changes

print("\nGeneration 0 → Final Generation\n")

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


# Mean change by condition

print("\nMean change by condition\n")

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

    print(
        f"{name:25}"
        f" Δ coverage = {mean_coverage:+.3f}"
        f" | Δ collisions = {mean_collisions:+.3f}"
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

    x = [
        r["change_coverage"]
        for r in condition_results
    ]

    y = [
        r["change_collisions"]
        for r in condition_results
    ]

    plt.scatter(
        x,
        y,
        color=colours.get(name, "gray"),
        s=70,
        alpha=0.65,
        label=name,
    )

    # Mean point
    mean_x = np.mean(x)
    mean_y = np.mean(y)

    plt.scatter(
        mean_x,
        mean_y,
        color=colours.get(name, "gray"),
        edgecolor="black",
        linewidth=2,
        s=180,
        marker="X",
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


plt.xlabel("Change in coverage (final − initial)")
plt.ylabel("Change in collisions (final − initial)")

plt.title(
    "Change in Coverage and Collisions\n"
    "Generation 0 → Final Generation"
)

plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()


# Plot 2:
# Mean coverage change

condition_names = []
coverage_changes = []

for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    condition_names.append(name)

    coverage_changes.append(
        np.mean([
            r["change_coverage"]
            for r in condition_results
        ])
    )


plt.figure(figsize=(10, 6))

bars = plt.bar(
    condition_names,
    coverage_changes,
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
plt.title("Change in Coverage: Generation 0 → Final")

for bar, value in zip(bars, coverage_changes):

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


# Plot 3:
# Mean collision change

collision_changes = []

for directory in directories:

    name = directory.name

    condition_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not condition_results:
        continue

    collision_changes.append(
        np.mean([
            r["change_collisions"]
            for r in condition_results
        ])
    )


plt.figure(figsize=(10, 6))

bars = plt.bar(
    condition_names,
    collision_changes,
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
plt.title("Change in Collisions: Generation 0 → Final")

for bar, value in zip(bars, collision_changes):

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
