# Required Knowledge

> Authored by Claude Code 09-09-2026

Kaggriculture is a two-player farming economy, so it touches bandits, sequential decision-making, game theory, and classic operations research. Specifically, it runs 30 in-game days (720 turns at 24 per day), both agents start with $3,000 and a 10x10 grid with only a 5x5 quadrant active, and the goal is the highest bank balance at turn 720. Here are the topics that map to it, grouped by what they solve.

## 1. Multi-Bandits

- **Nonstationary bandits** – crop or market choices whose payoffs drift, since market prices react to supply and demand
- **Contextual bandits (LinUCB, contextual Thompson sampling)** – choose actions using state features like day, cash, and prices
- **Discounted / sliding-window UCB** – track shifting sale prices
- **Adversarial bandits (EXP3)** – rewards shaped by an opponent, not just randomness

## 2. Core reinforcement learning

- **MDP formulation** – defining state, actions, and reward from the observation
- **Reward shaping** – turning a final bank balance into useful per-turn signals
- **Temporal-difference learning (Q-learning, SARSA)** – learning action values over the 720 turns
- **Function approximation** – large state spaces need features or neural nets instead of tables
- **Policy gradient and PPO** – learning a direct policy via self-play
- **Credit assignment over long horizons** – linking early investments (land, animals) to late income

## 3. Planning and search

- **Monte Carlo Tree Search (MCTS)** – simulating future turns before committing
- **Model-based RL** – learning a forward model of prices and crop growth, then planning with it
- **Rollout policies and receding-horizon planning** – plan a few days ahead, replan every turn
- **Hierarchical RL / options** – a high-level strategy (expand, farm, trade) calling low-level actions

## 4. Multi-agent and game theory

- **Opponent modelling** – predicting the rival's selling, since both share one market
- **Self-play and population-based training** – training against past versions of your agent
- **Nash equilibria and best-response strategies** – avoiding being exploited in a zero-sum ranking
- **Fictitious play** – best-responding to the opponent's average behaviour

## 5. Optimization and operations research

- **Resource allocation / knapsack** – splitting limited cash across seeds, animals, land, and labour
- **Integer and linear programming** – optimal crop mix per plot under constraints
- **Scheduling** – ordering planting, harvesting, and feeding within a day's labour capacity
- **Capital investment and ROI / NPV analysis** – when an upgrade pays back before turn 720
- **Marginal cost analysis** – for example, hiring farm hands follows a Fibonacci cost curve, so each extra hand needs to justify its rising price
- **Dynamic programming** – backward induction over days for timing decisions like sell-now vs hold

## 6. Forecasting and market modelling

- **Price-impact modelling** – how your own sales move prices
- **Time-series forecasting** – predicting prices and demand
- **Optimal stopping** – choosing the best moment to sell stored produce
- **Inventory control** – how much produce or feed to hold

## 7. Imitation and offline learning

- **Behavioural cloning** – learning from top agents, since Kaggle publishes daily JSON replays of completed episodes ranked by average agent rating
- **Offline RL** – training value functions from those replays without live play

## Suggested learning path

Given your bandit start, a natural order is: nonstationary bandits → contextual bandits → MDPs and Q-learning → rollout-based planning → opponent modelling. Furthermore, top competitors often begin with strong heuristics. For example, one public roadmap puts RL experiments only after rule-based, economic, market, and labour stages, and only if the heuristic ceiling is actually hit. Therefore, a hybrid of optimisation-based rules plus bandit-tuned parameters is a strong, practical target.

Sources:
- [Kaggriculture – Kaggle](https://www.kaggle.com/competitions/kaggriculture)
- [Kaggriculture write-up – Amey-Thakur (GitHub)](https://github.com/Amey-Thakur/KAGGLE-COMPETITIONS/blob/main/Competitions/Kaggriculture/README.md)
- [Smartex-Dan/kaggriculture (GitHub)](https://github.com/Smartex-Dan/kaggriculture)
- [Kaggriculture Episodes dataset](https://www.kaggle.com/datasets/kaggle/kaggriculture-episodes-2026-08-21)
- [Kaggle on X](https://x.com/kaggle/status/2084326711248687165)