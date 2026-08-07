from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np

# Directory containing the results
directory = Path("22_07_2026")

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

    generation = last.get("generation")
    if generation is None:
        continue

    fitness = last.get(
        "fitness",
        last["coverage"] - 10.0 * last["collisions"],
    )

    results.append({
        "file": f.name,
        "generation": generation,
        "fitness": fitness,
    })

if not results:
    raise RuntimeError("No valid results found.")

# Sort by generation
results.sort(key=lambda r: r["generation"])

x = np.array([r["generation"] for r in results])
y = np.array([r["fitness"] for r in results])

# Linear regression
m, b = np.polyfit(x, y, 1)
xfit = np.linspace(x.min(), x.max(), 300)
yfit = m * xfit + b

plt.figure(figsize=(10, 6))

plt.scatter(
    x,
    y,
    s=60,
    color="steelblue",
)

plt.plot(
    xfit,
    yfit,
    color="crimson",
    linewidth=2,
    label=f"Best fit (slope={m:.6f})",
)

# Label each point with the run number
for r in results:
    run = r["file"].split("_")[-1].split(".")[0]
    plt.annotate(
        run,
        (r["generation"], r["fitness"]),
        xytext=(4, 4),
        textcoords="offset points",
        fontsize=8,
    )

corr = np.corrcoef(x, y)[0, 1]

plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.title(f"Generation vs Fitness (r = {corr:.3f})")
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()
plt.show()

print(f"Correlation: {corr:.4f}")
print(f"Slope: {m:.8f} fitness/generation")
