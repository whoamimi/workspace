"""
MODULE 0c — Crop model.

Predict what a plant will yield, and when to harvest it. Both the executor
(harvest timing) and later the crop planner (profit per tile-day) use this.

Exact rules from the env source:

ONE-TIME crops (WHEAT, CARROT, MELON)
  - New plant starts with yield_units = 1.
  - Each WATER action adds a bonus if  window_start <= age <= max_yield_day,
    where window_start = (max_yield_day + 1) // 2  (i.e. ceil(max_yield_day/2)).
    Bonus = 2 if fertilized_until_day >= today else 1.  Capped at max_yield.
  - HARVEST allowed once age >= first_yield_day. Harvest removes the plant.
  - max_lifespan_step = (planted_day + max_yield_day + 1) * TURNS_PER_DAY.
    From that step, yield drops by 1 every other turn; at 0 it becomes a weed.

ONGOING crops (TOMATO, STRAWBERRY)
  - Start with yield_units = 0.
  - Production happens at END of day d (i.e. for next_day = d + 1) when
    days_since_first = next_day - planted_day - first_yield_day >= 0 and
    days_since_first % interval == 0, up to max_yield productions.
  - Each production adds 1, or 2 if watered that day AND fertilized.
  - After the last production, decay starts at (next_day + 1) * TURNS_PER_DAY.
  - Harvest does NOT remove the plant.

Test: tests/test_crops.py checks peak yields from the README table.
"""

from __future__ import annotations

from .constants import CROPS, TURNS_PER_DAY
from .state import PlantTile


def window_start(crop: str) -> int:
    """First age (days) at which watering adds bonus yield (one-time crops)."""
    # TODO
    raise NotImplementedError


def peak_yield(crop: str, fertilized: bool = False) -> int:
    """Max yield with daily watering from planting.

    Expected (README): WHEAT 4 (6 fert), CARROT 3 (4 fert), MELON 6,
    TOMATO 4, STRAWBERRY 4. With fertilizer, ongoing crops give 2 per
    production (8 total over 4 productions), but held yield_units is capped
    at max_yield (4), so you must harvest between productions to get all 8.
    """
    # TODO
    raise NotImplementedError


def best_harvest_age(crop: str) -> int:
    """Age at which a one-time crop reaches peak yield under daily watering.

    Expected: WHEAT 4, CARROT 3, MELON 10 (cap 6 hit before max_yield_day 12).
    For ongoing crops, return the age of the last scheduled production.
    """
    # TODO
    raise NotImplementedError


def forecast_yield(tile: PlantTile, day: int, water_every_day: bool = True) -> int:
    """Predicted yield_units if left to grow until its best harvest age.

    Start from tile.yield_units and add the bonuses still to come.
    """
    # TODO
    raise NotImplementedError


def should_harvest_now(tile: PlantTile, day: int, step: int) -> bool:
    """Harvest decision.

    Suggested rules:
      - one-time crop: age >= best_harvest_age, OR decay has started
        (step >= max_lifespan_step), OR it is the last day and yield > 0.
      - ongoing crop: yield_units > 0 (collect as produced).
    Never harvest before first_yield_day (the env ignores it anyway).
    """
    # TODO
    raise NotImplementedError


def decay_step(tile: PlantTile) -> int:
    """Turn step at which yield starts decaying (-1 if not yet scheduled)."""
    # TODO
    raise NotImplementedError


def can_mature(crop: str, planted_day: int, days_total: int = 30) -> bool:
    """True if a crop planted today can be harvested before the season ends."""
    # TODO: planted_day + best_harvest_age(crop) <= days_total - 1
    raise NotImplementedError
