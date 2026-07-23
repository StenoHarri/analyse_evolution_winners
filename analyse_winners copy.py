from pathlib import Path
import json

import numpy as np
import matplotlib.pyplot as plt

# Directory containing the results
directory = Path("21_07_2026")

files = sorted(directory.glob("population_winners_*.jsonl"))

results = []

# Read the final (last) winner from each file
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
        "file": f.name,
        "coverage": last["coverage"],
        "collisions": last["collisions"],
        "fitness": last.get("fitness"),
        "generation": last.get("generation"),
    })


def is_dominated(a, others):
    """True if another run has >= coverage and <= collisions."""
    for b in others:
        if b is a:
            continue

        if (
            b["coverage"] >= a["coverage"]
            and b["collisions"] <= a["collisions"]
            and (
                b["coverage"] > a["coverage"]
                or b["collisions"] < a["collisions"]
            )
        ):
            return True

    return False


pareto = [r for r in results if not is_dominated(r, results)]

print("\nPareto-optimal runs:\n")

for r in sorted(pareto, key=lambda x: (-x["coverage"], x["collisions"])):
    print(
        f"{r['file']:28}"
        f" coverage={r['coverage']:.3f}"
        f" collisions={r['collisions']:.3f}"
        f" fitness={r['fitness']:.3f}"
    )

# Best-fit line and residuals

x = np.array([r["coverage"] for r in results])
y = np.array([r["collisions"] for r in results])

# Linear regression: collisions = m * coverage + b
m, b = np.polyfit(x, y, 1)

for r in results:
    expected = m * r["coverage"] + b
    residual = r["collisions"] - expected  # negative = better than expected

    r["expected_collisions"] = expected
    r["residual"] = residual

print("\nMost better-than-expected runs:\n")

for r in sorted(results, key=lambda r: r["residual"])[:10]:
    print(
        f"{r['file']:28}"
        f" residual={r['residual']:.4f}"
        f" actual={r['collisions']:.4f}"
        f" expected={r['expected_collisions']:.4f}"
    )

best = min(results, key=lambda r: r["residual"])

# Plot

plt.figure(figsize=(10, 7))

# All runs
plt.scatter(
    x,
    y,
    color="lightgray",
    s=40,
    label="All runs",
)

# Pareto front
plt.scatter(
    [r["coverage"] for r in pareto],
    [r["collisions"] for r in pareto],
    color="red",
    s=80,
    label="Pareto-optimal",
)

# Best-fit line
xfit = np.linspace(x.min(), x.max(), 200)
yfit = m * xfit + b

plt.plot(
    xfit,
    yfit,
    color="blue",
    linewidth=2,
    label="Best-fit line",
)

# Highlight best residual
plt.scatter(
    best["coverage"],
    best["collisions"],
    color="limegreen",
    edgecolor="black",
    s=180,
    zorder=5,
    label="Most better than expected",
)

# Label every point with its file number
for r in results:
    number = r["file"].split("_")[-1].split(".")[0]

    plt.annotate(
        number,
        (r["coverage"], r["collisions"]),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8,
    )

plt.xlabel("Coverage (higher is better)")
plt.ylabel("Collisions (lower is better)")
plt.title("Final Generation Winners")
plt.grid(True, alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()
