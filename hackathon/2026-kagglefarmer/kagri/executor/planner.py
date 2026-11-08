"""
MODULE 1b — Maintenance task generator.

Scan the farm and list the upkeep work that must happen today. Strategy
modules add their own tasks (what to plant, which animal to place) on top.

Rules to encode:
  - Every plant must be watered once per day. A plant with
    consecutive_unwatered == 1 and watered_today == False dies tonight.
  - A fresh seed starts at consecutive_unwatered = 1, so it must be watered
    the SAME day it is planted.
  - Every animal must be fed daily with WHEAT the unit carries.
    consecutive_unfed == 1 and not fed_today -> escapes tonight.
  - A newly placed animal starts at consecutive_unfed = 0 (safe on day 1).
  - Weeds block planting; DIG them.
  - Last day: all carried produce must be DROPped at a shed tile before the
    final turn, or it can't be sold.
"""
from __future__ import annotations

from ..state import GameState
from .tasks import Priority, Task


def water_tasks(state: GameState) -> list[Task]:
    """One WATER task per unwatered plant. Use Priority.SAVE_LIFE when the
    plant dies tonight otherwise, else Priority.WATER."""
    # TODO
    raise NotImplementedError


def harvest_tasks(state: GameState) -> list[Task]:
    """HARVEST tasks for plants where crops.should_harvest_now() is True,
    and for animals with yield_units > 0 (urgent when at max_held)."""
    # TODO
    raise NotImplementedError


def animal_care_tasks(state: GameState) -> list[Task]:
    """FEED (needs_item=("WHEAT", 1)), CARE and COLLECT_FERTILIZER per animal.

    Skip this until you build Module 4, but keep FEED from day one if you
    buy any animal — escapes are permanent.
    """
    # TODO
    raise NotImplementedError


def weed_tasks(state: GameState) -> list[Task]:
    """DIG tasks for weeds. Low priority unless the tile is needed for planting."""
    # TODO
    raise NotImplementedError


def endgame_tasks(state: GameState) -> list[Task]:
    """On the last day after ENDGAME_HOUR: a DROP task at the nearest
    shed tile for every unit carrying items."""
    # TODO
    raise NotImplementedError


def generate(state: GameState, extra: list[Task] | None = None) -> list[Task]:
    """All tasks for today, sorted by (priority, deadline).

    `extra` = tasks from strategy modules (e.g. PLANT tasks from the crop
    planner). Remove duplicates on the same tile (keep the most urgent).
    """
    # TODO
    raise NotImplementedError
