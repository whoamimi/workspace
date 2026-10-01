"""
MODULE 0a — State parser.

Turn the raw observation dict into typed objects, so every other module works
with named fields instead of nested dict lookups.

Build order: implement this first; every other module takes a `GameState`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

Pos = tuple[int, int]   # (x, y); tiles are indexed tiles[y][x]


# --------------------------------------------------------------- tile types
@dataclass
class PlantTile:
    pos: Pos
    crop: str
    planted_day: int
    watered_today: bool
    consecutive_unwatered: int
    yield_units: int
    max_lifespan_step: int        # -1 for ongoing crops until they finish producing
    fertilized_until_day: int     # -1 if never fertilized

    def age(self, day: int) -> int:
        """Days since planting."""
        # TODO: return day - planted_day
        raise NotImplementedError

    def dies_tonight_if_unwatered(self) -> bool:
        """True if skipping water today turns this plant into a weed tonight.

        Rule: a plant becomes a weed when consecutive_unwatered reaches 2 at
        end-of-day. A new seed starts at 1, so it MUST be watered on its
        planting day.
        """
        # TODO
        raise NotImplementedError


@dataclass
class AnimalTile:
    pos: Pos
    kind: str                     # "COOP" | "PASTURE"
    animal: Optional[str]         # None = empty structure, ready for PLACE
    placed_day: int = -1
    yield_units: int = 0
    fed_today: bool = False
    consecutive_unfed: int = 0
    cared_today: bool = False
    fertilizer_available: bool = False
    pending_care_bonus: int = 0


@dataclass
class WeedTile:
    pos: Pos


# --------------------------------------------------------------- farm/state
@dataclass
class FarmState:
    money: float
    farmer: Pos
    hands: list[Pos]
    unlocked_quadrants: list[str]
    hires_today: int
    plants: dict[Pos, PlantTile] = field(default_factory=dict)
    animals: dict[Pos, AnimalTile] = field(default_factory=dict)
    weeds: set[Pos] = field(default_factory=set)
    empty: set[Pos] = field(default_factory=set)      # unlocked and free
    locked: set[Pos] = field(default_factory=set)

    def units(self) -> list[Pos]:
        """Positions of all units: farmer first, then hands in order."""
        # TODO
        raise NotImplementedError


@dataclass
class GameState:
    me: int
    day: int
    hour: int
    step: int
    my_farm: FarmState
    opp_farm: FarmState
    market_inventory: dict[str, int]
    prices: dict[str, int]
    unlocked_shops: list[str]
    shed: dict[str, int]
    seeds: dict[str, int]
    inventories: list[dict[str, int]]   # [0] = farmer, then hands

    @property
    def days_left(self) -> int:
        """Whole days remaining AFTER today."""
        # TODO: use constants.DAYS
        raise NotImplementedError

    @property
    def shed_free(self) -> int:
        """Free shed slots (seeds excluded)."""
        # TODO: constants.SHED_CAPACITY - sum(shed.values())
        raise NotImplementedError


# ------------------------------------------------------------------- parse
def parse_tile(tile, pos: Pos):
    """Return PlantTile | AnimalTile | WeedTile | "EMPTY" | "LOCKED".

    Raw tile values:  None -> empty,  "LOCKED",  {"kind": "PLANT", ...},
    {"kind": "WEED"},  {"kind": "COOP"|"PASTURE", "animal": ...}.
    Note: an empty structure dict may lack most keys (e.g. {"kind": "COOP"}),
    so use .get() with defaults for AnimalTile fields.
    """
    # TODO
    raise NotImplementedError


def parse_farm(raw: dict) -> FarmState:
    """Build a FarmState from obs["farms"][i]. Fill plants/animals/weeds/empty/locked."""
    # TODO: loop tiles[y][x], call parse_tile((x, y)), bucket results
    raise NotImplementedError


def parse(obs: dict) -> GameState:
    """Build a GameState from the raw observation.

    obs may be a dict or a kaggle Struct; both support obs["key"].
    'step' is supplied by the framework; fall back to day*24 + hour.
    """
    # TODO
    raise NotImplementedError
