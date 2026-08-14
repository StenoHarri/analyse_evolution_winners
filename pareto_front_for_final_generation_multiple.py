from pathlib import Path
import json

import numpy as np
import matplotlib.pyplot as plt


# Directories containing the results
directories = [
    Path("uncapped"),
    Path("one_cap"),
    Path("point_four_cap"),
    Path("point_seven_five_cap"),
]

results = []


# Read the final (last) winner from each file in each directory
for directory in directories:
    files = sorted(directory.glob("population_winners_*.jsonl"))

    for f in files:
        last = None

        with f.open() as fp:
            for line in fp:
                line = line.strip()
                if line:
                    last = json.loads(line)

        if last is None:
            continue

        results.append({
            "directory": directory.name,
            "file": f.name,
            "coverage": last["coverage"],
            "collisions": last["collisions"],
            "fitness": last.get(
                "fitness",
                last["coverage"] - 10.0 * last["collisions"],
            ),
            "generation": last.get("generation"),
        })


# Print results

print("\nFinal generation winners:\n")

for r in results:
    print(
        f"{r['directory']:25}"
        f"{r['file']:28}"
        f" coverage={r['coverage']:.3f}"
        f" collisions={r['collisions']:.3f}"
        f" fitness={r['fitness']:.3f}"
    )


# Fitness

fitness_values = [
    r["coverage"] - 10.0 * r["collisions"]
    for r in results
]

best_fitness = max(fitness_values)


# Plot

plt.figure(figsize=(11, 8))


# One colour per directory
colours = {
    "uncapped": "tab:blue",
    "one_cap": "tab:orange",
    "point_four_cap": "tab:green",
    "point_seven_five_cap": "tab:red",
}


# Plot runs grouped by directory
for directory in directories:
    name = directory.name

    directory_results = [
        r for r in results
        if r["directory"] == name
    ]

    if not directory_results:
        continue

    plt.scatter(
        [r["coverage"] for r in directory_results],
        [r["collisions"] for r in directory_results],
        color=colours.get(name, "gray"),
        s=50,
        alpha=0.7,
        label=name,
    )


# Label every point

for r in results:
    # population_winners_47.jsonl -> 47
    number = r["file"].split("_")[-1].split(".")[0]

    plt.annotate(
        number,
        (r["coverage"], r["collisions"]),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8,
    )


# Fitness contours

x = np.array([r["coverage"] for r in results])
xfit = np.linspace(x.min(), x.max(), 300)


# Draw several iso-fitness lines
for fitness in np.linspace(
    min(fitness_values),
    max(fitness_values),
    6,
):
    plt.plot(
        xfit,
        (xfit - fitness) / 10.0,
        "--",
        color="purple",
        alpha=0.2,
    )


# Highlight the best fitness contour
plt.plot(
    xfit,
    (xfit - best_fitness) / 10.0,
    "--",
    color="purple",
    linewidth=2.5,
    label=f"Best fitness contour ({best_fitness:.2f})",
)


# Formatting

plt.xlabel("Coverage (higher is better)")
plt.ylabel("Collisions (lower is better)")
plt.title("Final Generation Winners")
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()
