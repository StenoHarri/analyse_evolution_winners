from pathlib import Path
import json

import matplotlib.pyplot as plt

# Directories containing the results
directories = [
    Path("uncapped"),
    Path("one_cap"),
    Path("point_four_cap"),
    Path("point_seven_five_cap"),
]

results = []

TAIL_GENERATIONS = 200000

plt.figure(figsize=(10, 7))

colors = plt.cm.tab10.colors

for i, directory in enumerate(directories):
    files = sorted(directory.glob("population_winners_*.jsonl"))
    color = colors[i % len(colors)]

    for f in files:
        history = []

        with f.open() as fp:
            for line in fp:
                line = line.strip()
                if line:
                    history.append(json.loads(line))

        if not history:
            continue

        last = history[-1]

        run_number = f.stem.split("_")[-1]

        results.append({
            "run_number": run_number,
            "file": f.name,
            "coverage": last["coverage"],
            "collisions": last["collisions"],
            "fitness": last.get("fitness"),
            "generation": last.get("generation"),
        })

        tail = history[-TAIL_GENERATIONS:]

        xs = [r["coverage"] for r in tail]
        ys = [r["collisions"] for r in tail]

        plt.plot(
            xs,
            ys,
            color=color,
            linewidth=1.5,
            alpha=0.4,
        )

        plt.scatter(
            xs[-1],
            ys[-1],
            color=color,
            s=35,
            zorder=3,
        )

        # Label only with the number at the end of the filename,
        # e.g. population_winners_34.jsonl -> "34"
        plt.annotate(
            run_number,
            (xs[-1], ys[-1]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )

# Add one legend entry per directory/cap
for i, directory in enumerate(directories):
    plt.plot(
        [],
        [],
        color=colors[i % len(colors)],
        label=directory.name,
    )

plt.xlabel("Coverage (higher is better)")
plt.ylabel("Collisions (lower is better)")
plt.title("Phase Portraits of each run")
plt.grid(True, alpha=0.3)
plt.legend(title="Cap")
plt.tight_layout()
plt.show()
