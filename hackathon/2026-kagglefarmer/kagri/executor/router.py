"""
MODULE 1c — Router: assign tasks to units and move them.

This is a scheduling problem: several units, many tasks with priorities and
deadlines, travel cost = Manhattan distance, one action per unit per turn.

v1 (greedy):   each unit takes the best (priority, distance) unclaimed task.
v2 (lookahead): check every SAVE_LIFE task is still reachable before its
                deadline; if not, re-assign units.
v3 (optional):  solve as a small vehicle-routing problem each morning.

Rules to encode:
  - Units may share a tile, and may walk across LOCKED tiles.
  - Tile actions on LOCKED tiles do nothing (except shed PICKUP/DROP/PLACE).
  - PLANT conflict: if more units PLANT the same crop this turn than you
    hold seeds, NONE succeed. Never assign more PLANT <crop> than seeds.
  - A task with needs_item requires the unit to carry that item first; if
    it doesn't, insert a PICKUP at the nearest shed tile.
"""

from __future__ import annotations

from ..state import GameState
from .tasks import Pos, Task


def manhattan(a: Pos, b: Pos) -> int:
    # TODO
    raise NotImplementedError


def step_toward(pos: Pos, target: Pos) -> str:
    """One move op from pos toward target. Remember: NORTH is y - 1.
    Return "PASS" if already there."""
    # TODO
    raise NotImplementedError


def nearest_shed_tile(pos: Pos) -> Pos:
    """Closest of constants.SHED_TILES. Any of them works, even when locked."""
    # TODO
    raise NotImplementedError


def carrying(state: GameState, unit_idx: int, item: str) -> int:
    """How many of `item` unit `unit_idx` is carrying (0 = farmer)."""
    # TODO
    raise NotImplementedError


def assign(state: GameState, tasks: list[Task]) -> dict[int, Task]:
    """Map unit index -> task. Each task goes to at most one unit.

    Respect the PLANT seed-count conflict rule. Leave a unit out of the
    dict if nothing is worth doing.
    """
    # TODO
    raise NotImplementedError


def op_for(state: GameState, unit_idx: int, task: Task) -> list:
    """The op this unit should send this turn for its task:
    - not at task.pos      -> a move toward it
    - needs an item it lacks -> go to shed / PICKUP first
    - at task.pos          -> task.op
    """
    # TODO
    raise NotImplementedError
