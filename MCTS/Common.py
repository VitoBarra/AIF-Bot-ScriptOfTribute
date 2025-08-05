import numpy as np

def calculate_ucb(total_utility, number_of_playouts, parents_number_of_playouts) -> float:
    if number_of_playouts == 0:
        raise ValueError("Node must have at least one playout before it can be calculated")

    exploitation_term = total_utility / number_of_playouts
    c = np.sqrt(2)
    exploration_term = np.log(parents_number_of_playouts) / number_of_playouts

    return exploitation_term + c * np.sqrt(exploration_term)