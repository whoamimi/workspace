# src/run_game.py
#
# starts
#
#


from kaggle_environments import make

# from kaggle_environments.envs.kaggriculture.kaggriculture import (
#     CROPS,
#     PRODUCTS,
#     ANIMALS,
#     # MARKET_I0,  # 10_000
#     # MARKET_PARAMS,  # SELL/BACK PRICE TICKER RANGE
#     # MAX_SHOP_INSTANCES,
#     # TOWN_CENTER_PRODUCTS,  # ['WHEAT', 'CARROT', 'TOMATO', 'STRAWBERRY', 'MELON', 'EGG', 'MILK', 'WOOL']
#     # FARM_HAND_COST_MULT,  # 1
#     # FARMER_MOVES,  # {'NORTH': (0, -1), 'SOUTH': (0, 1), 'EAST': (1, 0), 'WEST': (-1, 0)}
#     # LAND_PRICES,  # [1000, 2000, 4000]
#     # HINGE_GAIN,  # 8.0
#     # SHOPS,
#     # market_price,
#     # PRICE_FLOOR,  # 1.0
# )
# class FarmConfig(Enum):
#     crops = CROPS
#     products = PRODUCTS
#     animals = ANIMALS


def agent(obs):
    """my_agent. Hook like function to invoke during environment.

    Buy one wheat seed on the very first turn, then PASS forever after."""

    if obs.get("step", 0) == 0:
        return {"farmer": ["PASS"], "market": [["BUY_SEED", "WHEAT", 1]]}

    return {"farmer": ["PASS"], "market": []}


if __name__ == "__main__":
    import sys

    try:
        env = make("kaggriculture", configuration={"episodeSteps": 200})
        env.run([agent, "random"])
        env.render(mode="ipython", width=800, height=800)
    except Exception as e:
        print(str(e))
        sys.exit(1)
