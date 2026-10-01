"""
Kaggriculture agent — entry point.

Kaggle calls the LAST function defined in this file, so `agent` must stay at
the bottom. Submit as a tar.gz with main.py and the kagri/ folder at the root:

    kaggle competitions submit kaggriculture -f submission.tar.gz -m "v1"

While modules are unfinished, any NotImplementedError is caught and the
agent PASSes, so games still run. Set STRICT = True to see the traceback.
"""

import os
import sys

# Kaggle may run this file from another working directory.
for _p in (
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "",
    "/kaggle_simulations/agent",
):
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

from kagri import state as S  # noqa: E402
from kagri.constants import CROPS  # noqa: E402
from kagri.executor import Executor, Priority, Task  # noqa: E402
from kagri.market import OrderBook, Seller  # noqa: E402

STRICT = False  # True: raise errors instead of PASSing
MISSING = set()  # names of unimplemented functions hit so far


# --------------------------------------------------------------------------
# TEMPORARY strategy stub (Module 3 replaces this).
# Plants one fixed crop on every empty tile so you can exercise Modules 0-2.
# --------------------------------------------------------------------------
STUB_CROP = "WHEAT"
LAST_PLANT_HOUR = 16


def strategy_stub(gs, book):
    tasks = []
    empty = sorted(gs.my_farm.empty)
    have = gs.seeds.get(STUB_CROP, 0)
    if gs.hour == 0 and len(empty) > have:
        book.add(
            ["BUY_SEED", STUB_CROP, len(empty) - have],
            priority=20,
            source="stub",
            cost_estimate=(len(empty) - have) * CROPS[STUB_CROP]["seed"],
        )
    if gs.hour <= LAST_PLANT_HOUR:
        for pos in empty[:have]:
            tasks.append(
                Task(
                    Priority.PLANT,
                    LAST_PLANT_HOUR,
                    pos,
                    ["PLANT", STUB_CROP],
                    source="stub",
                )
            )
    return tasks


# --------------------------------------------------------------------------
class Brain:
    def __init__(self):
        self.executor = Executor()
        self.seller = Seller()

    def reset(self):
        self.executor.reset()
        self.seller.reset()

    def act(self, obs):
        gs = S.parse(obs)  # Module 0
        if gs.step == 0:
            self.reset()
        book = OrderBook()
        extra = strategy_stub(gs, book)  # Module 3 later
        self.seller.orders(gs, book)  # Module 2
        units = self.executor.act(gs, extra)  # Module 1
        return {**units, "market": book.emit(gs.my_farm.money)}


_BRAIN = None


def agent(obs, config=None):
    global _BRAIN
    if _BRAIN is None:
        _BRAIN = Brain()
    try:
        return _BRAIN.act(obs)
    except NotImplementedError:
        if STRICT:
            raise
        import traceback

        MISSING.add(traceback.extract_tb(sys.exc_info()[2])[-1].name)
        return {"farmer": ["PASS"], "hands": [], "market": []}
