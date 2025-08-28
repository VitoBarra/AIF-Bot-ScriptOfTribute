# Scripts of Tribute AI Bot

This repository contains our AI bot developed for the [Scripts of Tribute AI competition](https://github.com/ScriptsOfTribute), a re-adapted version of the card game *Tales of Tribute* from *The Elder Scrolls Online*.  

---

## The game

*Scripts of Tribute* is a two-player, competitive card game where each player builds and adapts their deck to outplay the opponent.  
Players manage three main resources:

- **Coins**: for purchasing cards  
- **Power & Prestige**:  for winning through score advantage  
- **Patron Favor** : for alternative win conditions  

A match ends when:
1. A player reaches **40 prestige** and maintains the lead until hitting **80 prestige**, or  
2. A player secures the **favor of all patrons**.

From an AI perspective, the game presents a **large and complex state space** with stochastic elements, strategic phases (early, mid, and late game), and the need for adaptive decision-making.

---

## Our Approach

We designed an AI bot based on **Monte Carlo Tree Search (MCTS)** enhanced with heuristics:
- **Prior move and Prior Choice heuristic** : to reduce the search space and improve performance.

- **MCTS**: Simulates possible moves within a player’s turn.  
- **Heuristic Evaluation**: A custom metric called **Min-Max Hand Value Rating (MMHVR)** evaluates game states by considering:  
  - Resources (prestige, power, coins, patron favor)  
  - Deck composition and quality  
  - Strategic potential across game phases  
- **Evolutionary Optimization**: Heuristics were refined automatically through evolutionary algorithms.  

**Results:** Our agent outperformed both a random bot and a simpler baseline strategy, demonstrating the effectiveness of MMHVR within MCTS.

---

## Usage

Install required packages:

```bash
pip install -r requirements.txt
```
Run a match between two bots:
```bash
python3 main.py
```

## Project Structure

- `BotCommon/`: Shared codebase (including heuristic implementation)
- `bots/`: Implementations of the different bots  
- `ExampleBot/`: example bots provided by the  documentation
- `HeuristicLearning/`: Evolutionary algorithm for heuristic optimization  
- `MCTS/`: Implementations of the varius version or MCTS algorithm  
- `helpers/`: Helper functions for logging and game management  

---

## Contact

- **Vito Barra** – v.barra1@studenti.unipi.it  
- **Alessio Iacullo** – a.iacullo@studenti.unipi.it  
