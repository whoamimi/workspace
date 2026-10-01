"""
MODULE 0e — Evaluation harness.

Run games and report the metrics each module is judged on. This one is
mostly written for you; the TODOs are extra metrics to add as you go.

Usage:
    python -m harness.evaluate                 # 10 games vs starter
    python -m harness.evaluate random 20
    python -m harness.evaluate self 5          # mirror match
"""
from __future__ import annotations

import os
import statistics
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def _is_plant(t):
    return isinstance(t, dict) and t.get("kind") == "PLANT"


def _has_animal(t):
    return isinstance(t, dict) and t.get("animal")


def game_metrics(env, me: int = 0) -> dict:
    """Per-game metrics from a finished env."""
    steps = env.steps
    final = steps[-1][me].observation["farms"]
    m = {
        "money": final[me]["money"],
        "opp_money": final[1 - me]["money"],
        "win": final[me]["money"] > final[1 - me]["money"],
        "plants_to_weed": 0,      # plant died (not watered, or decayed)
        "animals_escaped": 0,
        "idle_turns": 0,          # farmer PASS turns
    }
    for prev, cur in zip(steps, steps[1:]):
        a = prev[me].observation["farms"][me]["tiles"]
        b = cur[me].observation["farms"][me]["tiles"]
        for y, row in enumerate(a):
            for x, t in enumerate(row):
                nt = b[y][x]
                if _is_plant(t) and isinstance(nt, dict) and nt.get("kind") == "WEED":
                    m["plants_to_weed"] += 1
                if _has_animal(t) and not _has_animal(nt):
                    m["animals_escaped"] += 1
        act = cur[me].action or {}
        if (act.get("farmer") or ["PASS"])[0] == "PASS":
            m["idle_turns"] += 1
    # TODO: realised average sell price per product (Module 2 metric).
    #   Hint: diff shed + money between steps, or log SELL orders in your agent.
    # TODO: plants_to_weed split into "unwatered" vs "decayed after peak".
    return m


def run(opponent="starter", games: int = 10, agent_path: str | None = None):
    from kaggle_environments import make
    import main

    main.STRICT = False
    results = []
    for g in range(games):
        main._BRAIN = None
        env = make("kaggriculture")
        opp = main.agent if opponent == "self" else opponent
        env.run([main.agent, opp])
        m = game_metrics(env)
        results.append(m)
        print(f"game {g:3d}: money={m['money']:7.0f} opp={m['opp_money']:7.0f} "
              f"weeds={m['plants_to_weed']:3d} escaped={m['animals_escaped']} idle={m['idle_turns']}")

    print("-" * 70)
    print(f"win rate vs {opponent}: {sum(r['win'] for r in results)}/{games}")
    print(f"mean money: {statistics.mean(r['money'] for r in results):.0f}")
    if main.MISSING:
        print("unimplemented functions hit:", ", ".join(sorted(main.MISSING)))
    return results


if __name__ == "__main__":
    opp = sys.argv[1] if len(sys.argv) > 1 else "starter"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    run(opp, n)
