from pathlib import Path
import json

import matplotlib.pyplot as plt

# Directory containing the results
directory = Path("22_07_2026")

files = sorted(directory.glob("population_winners_*.jsonl"))

results = []

# Number of generations from the end to display
TAIL_GENERATIONS = 2000

plt.figure(figsize=(10, 7))

for f in files:
    history = []

    with f.open() as fp:
        for line in fp:
            line = line.strip()
            if line:
                history.append(json.loads(line))

    if not history:
        continue

    # Keep the final winner for later if desired
    last = history[-1]

    results.append({
        "file": f.name,
        "coverage": last["coverage"],
        "collisions": last["collisions"],
        "fitness": last.get("fitness"),
        "generation": last.get("generation"),
    })

    # Plot only the final N generations
    tail = history[-TAIL_GENERATIONS:]

    xs = [r["coverage"] for r in tail]
    ys = [r["collisions"] for r in tail]

    # Trail
    plt.plot(
        xs,
        ys,
        linewidth=1.5,
        alpha=0.5,
    )

    # Final point
    plt.scatter(
        xs[-1],
        ys[-1],
        s=35,
        zorder=3,
    )

    # Label with run number
    run_number = f.stem.split("_")[-1]
    plt.annotate(
        run_number,
        (xs[-1], ys[-1]),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8,
    )

plt.xlabel("Coverage (higher is better)")
plt.ylabel("Collisions (lower is better)")
plt.title(f"Final {TAIL_GENERATIONS} Generations of Each Run")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
