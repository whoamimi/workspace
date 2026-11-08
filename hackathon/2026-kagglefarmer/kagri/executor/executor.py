"""
MODULE 1 — Field executor (public interface).

Input:  GameState + extra tasks from strategy modules.
Output: {"farmer": op, "hands": [op, ...]}  for this turn.

The glue is written; the logic lives in planner.py and router.py.

Metrics to track (log them in the harness):
  - plants lost to weeds (target: 0)
  - animals escaped (target: 0)
  - idle unit-turns per day
"""
from __future__ import annotations

from ..state import GameState
from . import planner, router
from .tasks import Task


class Executor:
    def __init__(self):
        # Unit index -> task it committed to on a previous turn.
        # TODO (v2): keep units on their task until done, so they don't
        # zig-zag when a slightly better task appears mid-walk.
        self.commitments: dict[int, Task] = {}

    def reset(self):
        self.commitments.clear()

    def act(self, state: GameState, extra_tasks: list[Task] | None = None) -> dict:
        tasks = planner.generate(state, extra_tasks)
        assignment = router.assign(state, tasks)
        n_units = 1 + len(state.my_farm.hands)
        ops = [router.op_for(state, i, assignment[i]) if i in assignment else ["PASS"]
               for i in range(n_units)]
        return {"farmer": ops[0], "hands": ops[1:]}
