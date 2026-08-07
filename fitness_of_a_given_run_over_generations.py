import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

BURN_IN = 1
FADE_WINDOW = 500


def load_statistics(csv_path):
    df = pd.read_csv(csv_path)

    return (
        df["generation"].to_numpy(),
        df["fittest"].to_numpy(),
        df["upper_quartile"].to_numpy(),
        df["mean"].to_numpy(),
        df["lower_quartile"].to_numpy(),
        df["least_fit"].to_numpy(),
    )


def load_best_genomes(jsonl_path):
    genomes = []

    with open(jsonl_path) as f:
        for line in f:
            if not line.strip():
                continue

            obj = json.loads(line)

            left = obj["layout"]["left_chord_genes"]
            right = obj["layout"]["right_chord_genes"]

            # keep only the consonant cluster
            genome = [gene[0] for gene in left + right]

            genomes.append(genome)

    return genomes


def compute_gene_novelty_fade_matrix(genomes):
    num_generations = len(genomes)
    num_genes = len(genomes[0])

    matrix = np.zeros((num_genes, num_generations))

    seen = [set() for _ in range(num_genes)]
    last_novel = [None] * num_genes

    burn_end = min(BURN_IN, num_generations)

    # initialise seen genes
    for g in range(burn_end):
        for pos in range(num_genes):
            seen[pos].add(genomes[g][pos])

    for g in range(burn_end, num_generations):
        for pos in range(num_genes):

            gene = genomes[g][pos]

            if gene not in seen[pos]:
                seen[pos].add(gene)
                last_novel[pos] = g

            if last_novel[pos] is not None:
                age = g - last_novel[pos]
                matrix[pos, g] = max(0, 1 - age / FADE_WINDOW)

    return matrix


def plot_combined(stats_csv, winners_jsonl):

    generations, best, upper, mean, lower, worst = load_statistics(stats_csv)

    # clip fitnesses below 30
    best = np.maximum(best, 30)
    upper = np.maximum(upper, 30)
    mean = np.maximum(mean, 30)
    lower = np.maximum(lower, 30)
    worst = np.maximum(worst, 30)

    genomes = load_best_genomes(winners_jsonl)
    novelty = compute_gene_novelty_fade_matrix(genomes)

    # ------------------------------------------------------------------
    # Sort by the LAST generation a mutation occurred.
    # Genes that stopped mutating earliest are placed at the top.
    # Left and right halves are sorted independently.
    # ------------------------------------------------------------------
    last_mutation = np.full(novelty.shape[0], -1)

    for pos in range(novelty.shape[0]):
        mutated = np.where(novelty[pos] > 0)[0]
        if len(mutated):
            last_mutation[pos] = mutated[-1]

    left_gene_count = len(genomes[0]) // 2

    left_order = np.argsort(last_mutation[:left_gene_count])
    right_order = (
        np.argsort(last_mutation[left_gene_count:])
        + left_gene_count
    )

    order = np.concatenate([left_order, right_order])

    novelty = novelty[order]
    last_mutation = last_mutation[order]

    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(16, 10),
        sharex=True,
        gridspec_kw={"height_ratios": [1, 2]},
    )

    # -------------------------
    # Fitness
    # -------------------------

    ax1.fill_between(
        generations,
        lower,
        upper,
        alpha=0.25,
        color="tab:blue",
        label="Interquartile range",
    )

    ax1.plot(generations, best, color="tab:green", linewidth=2.5, label="Best")
    ax1.plot(generations, mean, "--", color="tab:orange", label="Mean")
    # Worst is always an outlier
    # ax1.plot(generations, worst, ":", color="tab:red", label="Worst")

    ax1.set_ylabel("Fitness")
    ax1.set_title("Evolutionary Fitness Over Generations")
    ax1.grid(alpha=0.3)
    ax1.legend()

    # -------------------------
    # Novelty heatmap
    # -------------------------

    ax2.imshow(
        novelty,
        aspect="auto",
        cmap="Greens",
        interpolation="nearest",
        origin="upper",
        vmin=0,
        vmax=1,
    )

    ax2.set_xlabel("Generation")
    ax2.set_ylabel("Gene Position")
    ax2.set_title(
        "Novel Gene Values Appearing in the Fittest Individual\n"
        "(sorted by last mutation generation within left/right halves)"
    )

    # Label rows with the original gene positions
    ax2.set_yticks(np.arange(len(order)))
    ax2.set_yticklabels(order)

    # Divider between left and right genes
    ax2.axhline(left_gene_count - 0.5, color="grey", alpha=0.5)

    plt.tight_layout()
    plt.savefig("graphs_of_evolution.png", dpi=200)
    plt.show()


def main():

    base = Path("27_07_2026")

    plot_combined(
        base / "population_statistics_202.csv",
        base / "population_winners_202.jsonl",
    )


if __name__ == "__main__":
    main()
