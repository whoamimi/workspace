"""
Kaggriculture - contextual multi-armed bandit agent (starter).

Design
------
* The BANDIT decides WHAT to plant each morning (arm = crop), given a context
  (season phase). It learns from per-tile profit per day occupied.
* A scripted EXECUTOR decides HOW: which tile to walk to, and what to do there
  (harvest > water > plant > dig weeds).
* A rule-based SELLER drip-sells from the shed to limit price impact.

Verified against kaggle_environments source:
  - NORTH = (0, -1), so NORTH decreases y (tiles[y][x]).
  - SELL draws ONLY from the shed, so the farmer must DROP produce at the
    shed on the last day or it is lost.
"""

import json
import math
import os
import random

CROPS = {
    # harvest_age: age at which a one-time crop hits max yield when watered daily
    "WHEAT": {"seed": 10, "base": 25, "harvest_age": 4, "ongoing": False},
    "CARROT": {"seed": 20, "base": 35, "harvest_age": 3, "ongoing": False},
    "MELON": {"seed": 80, "base": 250, "harvest_age": 10, "ongoing": False},
    "TOMATO": {"seed": 50, "base": 60, "harvest_age": 8, "ongoing": True, "life": 12},
    "STRAWBERRY": {
        "seed": 100,
        "base": 120,
        "harvest_age": 10,
        "ongoing": True,
        "life": 17,
    },
}
PREMIUM = {"STRAWBERRY", "MELON", "MILK", "WOOL"}
DAYS = 30
SHED_TILE = (4, 4)  # shed-adjacent tile inside the NW quadrant
ENDGAME_HOUR = 18  # last day: stop farming, walk to shed, DROP, sell
MAX_TILES = 10  # what one farmer can water + walk in 24 turns
LAST_PLANT_HOUR = 16  # leave time to water fresh seeds the same day


def _state_path():
    """Find bandit_state.json next to main.py, wherever Kaggle runs it from."""

    candidates = ["bandit_state.json", "/kaggle_simulations/agent/bandit_state.json"]

    try:
        candidates.insert(
            0,
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "bandit_state.json"
            ),
        )
    except NameError:  # __file__ is undefined under exec()
        pass

    return next((p for p in candidates if os.path.exists(p)), candidates[0])


STATE_FILE = _state_path()


# Learned bandit stats, embedded so the submission needs no extra files.
# Regenerate with: python main.py embed
EMBEDDED_STATS = {
    "early|WHEAT": [9, 14.666666666666666, 4.160000000000003],
    "early|CARROT": [5, 12.7, 0.30000000000000027],
    "mid|WHEAT": [4, 18.700000000000003, 1.7999999999999925],
    "early|MELON": [1325, 112.64699828473411, 36453.44518945887],
    "mid|CARROT": [4, 18.875, 1.1874999999999987],
    "late|WHEAT": [313, 25.477316293929714, 1361.848945686903],
    "late|CARROT": [435, 25.174712643678152, 273988.72183908045],
    "early|TOMATO": [9, 10.297591297591298, 105.99551186963777],
    "mid|MELON": [883, 101.47791619479042, 6495.906142657915],
    "early|STRAWBERRY": [9, 26.67473884140551, 1300.759494646959],
    "mid|TOMATO": [2, 14.979020979020978, 55.16171939948163],
    "mid|STRAWBERRY": [3, 60.77777777777778, 1.5],
}


# ------------------------------------------------------------------- bandit
class GaussianThompson:
    """Thompson sampling with a Gaussian posterior per (context, arm)."""

    def __init__(self, stats=None, prior_sd=5.0):
        self.stats = stats or {}  # key -> [n, mean, M2]
        self.prior_sd = prior_sd

    @staticmethod
    def _key(ctx, arm):
        return f"{ctx}|{arm}"

    def select(self, ctx, arms):
        best_arm, best_sample = None, -math.inf
        for arm in arms:
            n, mean, m2 = self.stats.get(self._key(ctx, arm), [0, 0.0, 0.0])
            if n == 0:
                return arm  # try every arm once
            sd = math.sqrt(m2 / (n - 1)) if n > 1 else self.prior_sd
            sample = random.gauss(mean, sd / math.sqrt(n))
            if sample > best_sample:
                best_arm, best_sample = arm, sample
        return best_arm

    def update(self, ctx, arm, reward):
        key = self._key(ctx, arm)
        n, mean, m2 = self.stats.get(key, [0, 0.0, 0.0])
        n += 1  # Welford online mean/variance
        delta = reward - mean
        mean += delta / n
        m2 += delta * (reward - mean)
        self.stats[key] = [n, mean, m2]

    def save(self, path=STATE_FILE):
        with open(path, "w") as f:
            json.dump(self.stats, f, indent=1)

    @classmethod
    def load(cls, path=STATE_FILE):
        if os.path.exists(path):
            with open(path) as f:
                return cls(json.load(f))
        return cls(dict(EMBEDDED_STATS))


def context(day):
    """Keep context small: too many contexts = too little data per arm."""
    if day < 10:
        return "early"
    if day < 20:
        return "mid"
    return "late"


def feasible_arms(day):
    """Only crops that can be harvested before the season ends."""
    left = DAYS - day
    return [c for c, p in CROPS.items() if p["harvest_age"] + 1 < left]


# ------------------------------------------------------------------ helpers
def is_plant(t):
    return isinstance(t, dict) and t.get("kind") == "PLANT"


def ready_to_harvest(t, day):
    if not is_plant(t) or t["yield_units"] <= 0:
        return False
    if day == DAYS - 1:
        return True  # last day: take whatever is there
    spec = CROPS[t["crop"]]
    return spec["ongoing"] or (day - t["planted_day"]) >= spec["harvest_age"]


def step_toward(pos, target):
    (x, y), (tx, ty) = pos, target
    if x < tx:
        return "EAST"
    if x > tx:
        return "WEST"
    if y < ty:
        return "SOUTH"
    return "NORTH"


# -------------------------------------------------------------------- agent
def make_agent(bandit, learn=True):
    """Return an agent closure with its own per-episode state."""
    st = {}

    def reset():
        st.clear()
        st.update(arm=None, ctx=None, ledger={}, last_day=-1)

    def close_tile(key, day):
        rec = st["ledger"].pop(key)
        if learn and rec["seen"]:
            days_used = max(1, day - rec["day"] + 1)
            reward = (rec["value"] - rec["cost"]) / days_used
            bandit.update(rec["ctx"], rec["arm"], reward)

    def agent(obs, config=None):
        day, hour = obs["day"], obs["hour"]
        if day == 0 and hour == 0 or not st:
            reset()
        me = obs["player"]
        farm = obs["farms"][me]
        tiles = farm["tiles"]
        prices = obs["market"]["prices"]
        seeds = obs["private"]["seeds"]
        shed = obs["private"]["shed"]
        market = []

        # 1. Close finished tiles -> bandit reward -------------------------
        for key in list(st["ledger"]):
            x, y = map(int, key.split(","))
            t, rec = tiles[y][x], st["ledger"][key]
            if is_plant(t) and t["crop"] == rec["arm"]:
                rec["seen"] = True
            elif rec["seen"] or day > rec["day"]:
                close_tile(key, day)

        # 2. Morning decision: pick today's crop and buy seeds -------------
        planted = sum(is_plant(t) for row in tiles for t in row)
        empty = sum(t is None for row in tiles for t in row)
        if hour == 0:
            arms = feasible_arms(day)
            st["ctx"] = context(day)
            st["arm"] = bandit.select(st["ctx"], arms) if arms else None
            if st["arm"]:
                n = min(empty, MAX_TILES - planted)
                cost = CROPS[st["arm"]]["seed"]
                n = min(n, int(farm["money"] * 0.5) // cost)
                if n > 0:
                    market.append(["BUY_SEED", st["arm"], n])

        # 3. Executor: pick the best task, walk there, act -----------------
        arm = st["arm"]
        can_plant = arm and seeds.get(arm, 0) > 0 and hour <= LAST_PLANT_HOUR
        pos = tuple(farm["farmer"])
        best = None
        for y, row in enumerate(tiles):
            for x, t in enumerate(row):
                if t == "LOCKED":
                    continue
                if ready_to_harvest(t, day):
                    task = (0, ["HARVEST"])
                elif is_plant(t) and not t["watered_today"]:
                    task = (1, ["WATER"])
                elif t is None and can_plant:
                    task = (2, ["PLANT", arm])
                elif isinstance(t, dict) and t.get("kind") == "WEED":
                    task = (3, ["DIG"])
                else:
                    continue
                dist = abs(pos[0] - x) + abs(pos[1] - y)
                cand = (task[0], dist, (x, y), task[1])
                if best is None or cand[:2] < best[:2]:
                    best = cand

        final_day = day == DAYS - 1
        carrying = (
            sum(obs["private"]["inventories"][0].values())
            if obs["private"].get("inventories")
            else 0
        )
        endgame = final_day and hour >= ENDGAME_HOUR

        farmer = ["PASS"]
        if endgame:
            best = None
            if pos != SHED_TILE:
                farmer = [step_toward(pos, SHED_TILE)]
            elif carrying:
                farmer = ["DROP"]
        if best:
            _, dist, (x, y), action = best
            if dist > 0:
                farmer = [step_toward(pos, (x, y))]
            else:
                farmer = action
                key = f"{x},{y}"
                t = tiles[y][x]
                if action[0] == "PLANT":
                    st["ledger"][key] = dict(
                        arm=arm,
                        ctx=st["ctx"],
                        day=day,
                        cost=CROPS[arm]["seed"],
                        value=0.0,
                        seen=False,
                    )
                elif action[0] == "HARVEST" and key in st["ledger"]:
                    # mark-to-market value of the harvest
                    st["ledger"][key]["value"] += t["yield_units"] * prices[t["crop"]]

        # 4. Seller: drip-sell to limit price impact ------------------------
        for item, qty in shed.items():
            if qty <= 0 or len(market) >= 10:
                continue
            base = CROPS.get(item, {}).get("base", prices.get(item, 1))
            if not final_day and prices.get(item, 0) < 0.6 * base:
                continue  # hold through a glut
            chunk = qty if final_day else min(qty, 2 if item in PREMIUM else 5)
            market.append(["SELL", item, chunk])

        return {"farmer": farmer, "hands": [], "market": market[:10]}

    return agent


# ------------------------------------------------------------------ training
def train(episodes=200, opponent="random"):
    from kaggle_environments import make

    bandit = GaussianThompson.load()
    for ep in range(episodes):
        env = make("kaggriculture")
        me = make_agent(bandit, learn=True)
        other = make_agent(bandit, learn=True) if opponent == "self" else opponent
        steps = env.run([me, other])
        final = steps[-1]
        print(f"ep {ep:4d}  rewards={[s.reward for s in final]}")
        if ep % 10 == 0:
            bandit.save()
    bandit.save()
    return bandit


def embed_stats(src=STATE_FILE, dst=None):
    """Rewrite EMBEDDED_STATS in this file from bandit_state.json."""
    import re

    dst = dst or os.path.abspath(__file__)
    with open(src) as f:
        stats = json.load(f)

    code = open(dst).read()
    code = re.sub(
        r"^EMBEDDED_STATS = .*$",
        "EMBEDDED_STATS = " + json.dumps(stats),
        code,
        count=1,
        flags=re.M,
    )
    open(dst, "w").write(code)
    print(f"embedded {len(stats)} arms into {dst}")


def evaluate(opponent="starter", games=10):
    """Frozen-policy win rate against a named or callable opponent."""
    from kaggle_environments import make

    wins = 0
    for g in range(games):
        env = make("kaggriculture")
        env.run([make_agent(GaussianThompson.load(), learn=False), opponent])
        m = env.steps[-1][0].observation["farms"]
        wins += m[0]["money"] > m[1]["money"]
        print(f"game {g}: me={m[0]['money']:.0f}  opp={m[1]['money']:.0f}")
    print(f"win rate vs {opponent}: {wins}/{games}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "embed":
        embed_stats()
    elif len(sys.argv) > 1 and sys.argv[1] == "eval":
        evaluate(sys.argv[2] if len(sys.argv) > 2 else "starter")
    else:
        train(episodes=int(sys.argv[1]) if len(sys.argv) > 1 else 50)


# Kaggle submission entry point: frozen bandit, no learning.
# Must stay the LAST function in the file: Kaggle calls the last callable.
_SUBMIT_AGENT = None


def agent(obs, config=None):
    global _SUBMIT_AGENT
    if _SUBMIT_AGENT is None:
        _SUBMIT_AGENT = make_agent(GaussianThompson.load(), learn=False)
    return _SUBMIT_AGENT(obs, config)
