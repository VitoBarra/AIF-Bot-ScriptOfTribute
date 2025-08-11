import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from HeuristicLearning.EvolutionaryHeuristic import CalculateConvergenceMetrics, ReadAllCheckPoints


def plot_weight_convergence(all_generations_metrics, ax=None):
    """
    Plot mean ± std for weights per dimension across generations.
    If ax is provided, plot on that axis; otherwise create a new figure.
    """
    means = np.array([gen["mean_weights"] for gen in all_generations_metrics])
    stds = np.array([gen["std_weights"] for gen in all_generations_metrics])
    gens = np.arange(len(all_generations_metrics))
    dim_count = means.shape[1]

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 5))
        created_fig = True

    for dim in range(dim_count):
        ax.plot(gens, means[:, dim], label=f"Dim {dim+1}")
        ax.fill_between(
            gens,
            means[:, dim] - stds[:, dim],
            means[:, dim] + stds[:, dim],
            alpha=0.15
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Weight Value (Mean ± Std)")
    ax.set_title("Weight Convergence Across Generations")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", ncol=2, fontsize="small")

    if created_fig:
        plt.tight_layout()
        plt.show()


def plot_weight(all_generations_metrics, ax=None):
    """

    """
    means = np.array([gen["mean_weights"] for gen in all_generations_metrics])
    stds = np.array([gen["std_weights"] for gen in all_generations_metrics])
    gens = np.arange(len(all_generations_metrics))
    dim_count = means.shape[1]

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 5))
        created_fig = True

    for dim in range(dim_count):
        ax.plot(gens, means[:, dim], label=f"Dim {dim+1}")
        ax.fill_between(
            gens,
            means[:, dim] - stds[:, dim],
            means[:, dim] + stds[:, dim],
            alpha=0.15
        )

    ax.set_xlabel("Generation")
    ax.set_ylabel("Weight Value (Mean ± Std)")
    ax.set_title("Weight Convergence Across Generations")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", ncol=2, fontsize="small")

    if created_fig:
        plt.tight_layout()
        plt.show()

def plot_unique_activations_heatmap(all_generations_metrics, ax=None):
    """
    Plot a heatmap of unique activations per dimension and generation.
    Colorbar is placed with good spacing and aligned height.
    """
    unique_acts = np.array([gen["unique_activations"] for gen in all_generations_metrics])
    dim_count = unique_acts.shape[1]

    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 5))
        created_fig = True

    im = ax.imshow(unique_acts.T, aspect="auto", cmap="viridis", origin="lower")

    # Create a divider for colorbar spacing
    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="3%", pad=0.2)
    plt.colorbar(im, cax=cax, label="Unique Activations")

    ax.set_xlabel("Generation")
    ax.set_ylabel("Dimension")
    ax.set_yticks(range(dim_count))
    ax.set_yticklabels([f"Dim {i+1}" for i in range(dim_count)])
    ax.set_title("Unique Activations Heatmap Across Generations")

    if created_fig:
        plt.tight_layout()
        plt.show()


def plot_convergence_from_checkpoints(pop_size: int, param_num: int):
    """
    Reads checkpoints, calculates metrics, and plots both on the same figure.
    """
    all_generations = ReadAllCheckPoints(pop_size, param_num)

    all_metrics = [
        CalculateConvergenceMetrics(population)
        for population in all_generations
    ]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20, 10), sharex=True)

    plot_weight_convergence(all_metrics, ax=ax1)
    plot_unique_activations_heatmap(all_metrics, ax=ax2)

    plt.tight_layout()
    plt.show()


def plotSingleWeight_from_checkpoints(pop_size: int, param_num: int):
    """
    Reads checkpoints, calculates metrics, and plots both on the same figure.
    """
    import matplotlib.pyplot as plt

    all_generations = ReadAllCheckPoints(pop_size, param_num)

    PARAM = 2
    w_all = []
    for j in range(PARAM):
        wi = [[i.weights[j] for i in ind] for ind in all_generations]
        w_all.append(wi)

    fig, axes = plt.subplots(PARAM, 1, figsize=(8, 30))

    for j, ax in enumerate(axes):
        # Each wi is a list of lists (per generation)
        # Flatten or average depending on what you want
        for gen_idx, gen_weights in enumerate(w_all[j]):
            ax.plot(gen_weights, label=f"Gen {gen_idx}")

        ax.set_title(f"Weight {j}")
        ax.set_xlabel("Individual")
        ax.set_ylabel("Value")
        ax.legend()

    plt.tight_layout()
    plt.show()
