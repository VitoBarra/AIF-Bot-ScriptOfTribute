import csv
import os
import random
from typing import Callable, List

import numpy as np
from tqdm import tqdm

from Helper.GameManager import RunGames
from HeuristicLerning.ActivationFunctions import ACTIVATION_NAMES, Linear
from bots.AIFBot_MMHVR import AIFBot_MMHVR

### ===============INTERFACE================
def GetWeight(paramNum: int, version: int) -> np.ndarray:
    try:
        weight = Individual.load("weights",version)
    except FileNotFoundError:
        weight = np.ones(paramNum)

    if weight.size != paramNum:
        raise ValueError(f"Weight size {weight.size} does not match parameter number {paramNum}")

    return weight

def GetActivationFunction(paramNUnm: int) -> List[Callable[[np.ndarray], np.ndarray]]:
    return [Linear for _ in range(paramNUnm)]




#====================Evolutionary Algorithm Implementation================
class Individual:
    def __init__(self, weights: np.ndarray, activations: list[str]):
        self.weights = weights
        self.activations = activations
        self.WinTime = 0
        self.NumOfGames = 0
        self.ID = random.getrandbits(128)

    # ===========================IO======================
    def save(self, filename: str, version: int) -> None:
        np.save(f"{filename}_weights_V{version}.npy", self.weights)
        np.save(f"{filename}_activations_V{version}.npy", np.array(self.activations))

    @staticmethod
    def load(filename: str, version: int) -> "Individual":
        weights = np.load(f"{filename}_weights_V{version}.npy")
        activations = np.load(f"{filename}_activations_V{version}.npy").tolist()
        return Individual(weights, activations)

def initialize_population(pop_size: int, param_num: int) -> List[Individual]:
    population: List[Individual] = []
    for _ in range(pop_size):
        weights = np.random.randn(param_num)
        activations = [np.random.choice(ACTIVATION_NAMES) for _ in range(param_num)]
        population.append(Individual(weights, activations))
    return population


def tournament_selection(population: List[Individual], fitnesses: List[float], k: int = 3) -> List[Individual]:
    selected: List[Individual] = []
    for _ in range(2):  # select two parents
        contenders = np.random.choice(len(population), k, replace=False)
        best_idx = contenders[np.argmax([fitnesses[i] for i in contenders])]
        selected.append(population[best_idx])
    return selected


def crossover(parent1: Individual, parent2: Individual) -> Individual:
    w1, a1 = parent1.weights, parent1.activations
    w2, a2 = parent2.weights, parent2.activations
    point = np.random.randint(1, len(w1))
    child_weights = np.concatenate([w1[:point], w2[point:]])
    child_activations = a1[:point] + a2[point:]
    return Individual(child_weights, child_activations)


def mutate(individual: Individual, mutation_rate: float = 0.1, activation_mutation_rate: float = 0.1) -> Individual:
    weights, activations = individual.weights, individual.activations
    new_weights = weights + np.random.randn(*weights.shape) * mutation_rate
    new_activations: List[str] = []
    for a in activations:
        if np.random.rand() < activation_mutation_rate:
            new_activations.append(np.random.choice(ACTIVATION_NAMES))
        else:
            new_activations.append(a)
    return Individual(new_weights, new_activations)



def SaveCheckPoint(pop: list[Individual], gen: int, pop_size: int, param: int):
    os.makedirs("CheckPoint", exist_ok=True)
    filename = f"CheckPoint/checkpoint_pop{pop_size}_par{param}_gen{gen}.npz"
    weights = [ind.weights for ind in pop]
    activations = [ind.activations for ind in pop]
    win_times = [ind.WinTime for ind in pop]
    num_games_list = [ind.NumOfGames for ind in pop]
    ids = [ind.ID for ind in pop]
    np.savez(filename, weights=weights, activations=activations, win_times=win_times, num_games=num_games_list, ids=ids)

def LoadCheckPoint(gen: int, pop_size: int, param: int) -> list[Individual]:
    filename = f"CheckPoint/checkpoint_pop{pop_size}_par{param}_gen{gen}.npz"
    data = np.load(filename, allow_pickle=True)
    weights_list = data["weights"]
    activations_list = data["activations"]
    win_times = data["win_times"]
    num_games_list = data["num_games"]
    ids = data["ids"]
    pop = []
    for weights, activations, win_time, num_game, id_ in zip(weights_list, activations_list, win_times, num_games_list, ids):
        ind = Individual(weights, activations.tolist())
        ind.WinTime = win_time
        ind.NumOfGames = num_game
        ind.ID = id_
        pop.append(ind)
    return pop

def UpdateIndividualStat(individue: Individual, botname:str) :
    # Read game results from CSV
    results_file = os.path.join('temp', f'{botname}_res.csv')
    if os.path.exists(results_file):
        with open(results_file, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                _, won = row
                won = int(won)
                individue.WinTime += won
                individue.NumOfGames += 1

def RemoveTempResults(botname:str):
    # Remove temporary results file
    results_file = os.path.join('temp', f'{botname}_res.csv')
    if os.path.exists(results_file):
        os.remove(results_file)


def PlayGames(population : List[Individual], run_n: int, num_games: int):
    depth = 2
    aif_MMHVR_name_collect = f"AIFBOT_MMHVR_collect"
    aif_MMHVR_name_Adversary = f"AIFBOT_MMHVR_adv"

    num_cores = os.cpu_count() or 1
    max_supported_thread = max([i for i in range(1, num_cores+1) if run_n % i == 0])

    for idx, selected in enumerate(tqdm(population, desc="Individuals", colour="green", leave=True, ncols=80, position=0)):
        pop_filtered = [adv for adv in population if adv != selected]
        pop_filtered_temp = pop_filtered.copy()
        bot_MMHVR_aif_col = AIFBot_MMHVR(aif_MMHVR_name_collect, depth, selected.weights, selected.activations,None)
        for _ in tqdm(range(1, num_games + 1), desc=f"   Games for current Individual", leave=False, ncols=80, position=1):
            if len(pop_filtered_temp) <= 0:
                pop_filtered_temp =  pop_filtered.copy()
            adv:Individual = random.choice(pop_filtered_temp)
            pop_filtered_temp.remove(adv)
            bot_MMHVR_aif_adv = AIFBot_MMHVR(aif_MMHVR_name_Adversary,depth,adv.weights,adv.activations,None)
            RunGames(bot_MMHVR_aif_col, aif_MMHVR_name_collect, bot_MMHVR_aif_adv, aif_MMHVR_name_Adversary,
                     runs=run_n, threads=max_supported_thread, hide_print=True)
            UpdateIndividualStat(adv, aif_MMHVR_name_Adversary)
            RemoveTempResults(aif_MMHVR_name_Adversary)
        UpdateIndividualStat(selected, aif_MMHVR_name_collect)
        RemoveTempResults(aif_MMHVR_name_collect)


def ReadCheckPointNum(pop_size: int, param_num: int) -> List[int]:
    return [int(f.split('gen')[-1].split(".")[0]) for f in os.listdir("CheckPoint")
            if f.startswith(f"checkpoint_pop{pop_size}_par{param_num}")]

def evolutionary_algorithm(
    pop_size: int,
    generations: int,
    n_elite: int = 2,
    tournament_k: int = 3,
    runs_for_each_game:int = 5,
    param_num: int = 13,
    recover_from_checkpoint:bool = True,
    mutation_seed:int = None ) -> Individual:

    if n_elite<= 0:
        raise ValueError("n_elite should be at least 1")

    if mutation_seed is not None:
        random.seed(mutation_seed)

    GAME_NUM = pop_size - 1
    last_saved_gen = 0
    population = None

    if recover_from_checkpoint:
        try:
            last_saved_gen = max(ReadCheckPointNum(pop_size, param_num))
            if  last_saved_gen > generations:
                raise ValueError("last checkpoint saved gen should be lower than max generations")
            population = LoadCheckPoint(last_saved_gen, pop_size, param_num)
            print(f"Recovering from checkpoint: gen {last_saved_gen} with population size {len(population)} and param num {param_num}")
        except Exception as e:
            print(e)


    if population is None:
        population = initialize_population(pop_size, param_num)

    print(f"Training started with: pop: {pop_size} for {generations} generation starting from gen {last_saved_gen+1}")

    elites =[]
    for gen in range(last_saved_gen,generations):
        PlayGames(population,runs_for_each_game, GAME_NUM)

        fitnesses = [ind.WinTime / ind.NumOfGames for ind in population]

        elite_indices = np.argsort(fitnesses)[-n_elite:]
        elites = [population[i] for i in elite_indices]

        if gen == generations-1:
            break

        offspring = elites.copy()
        while len(offspring) < pop_size:
            parent1, parent2 = tournament_selection(population, fitnesses, k=tournament_k)
            child = crossover(parent1, parent2)
            child = mutate(child)
            offspring.append(child)

        population = offspring
        SaveCheckPoint(population, gen+1, pop_size, param_num)
    return elites[0]