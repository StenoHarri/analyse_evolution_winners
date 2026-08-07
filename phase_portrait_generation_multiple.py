from pathlib import Path
import json

import matplotlib.pyplot as plt

# Directories containing the results
directories = [
    #Path("15_07_2026"),
    Path("21_07_2026"),
    Path("22_07_2026"),
    Path("26_07_2026"),
    Path("27_07_2026"),
]

results = []

TAIL_GENERATIONS = 200000

plt.figure(figsize=(10, 7))

colors = plt.cm.tab10.colors

for i, directory in enumerate(directories):
    files = sorted(directory.glob("population_winners_*.jsonl"))
    color = colors[i % len(colors)]
    date = directory.name

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

        results.append({
            "date": date,
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

        run_number = f.stem.split("_")[-1]
        plt.annotate(
            f"{date}-{run_number}",
            (xs[-1], ys[-1]),
            xytext=(4, 4),
            textcoords="offset points",
            fontsize=8,
        )

# Add one legend entry per date
for i, directory in enumerate(directories):
    plt.plot([], [], color=colors[i % len(colors)], label=directory.name)

plt.xlabel("Coverage (higher is better)")
plt.ylabel("Collisions (lower is better)")
plt.title(f"Final {TAIL_GENERATIONS} Generations of Each Run")
plt.grid(True, alpha=0.3)
plt.legend(title="Date")
plt.tight_layout()
plt.show()