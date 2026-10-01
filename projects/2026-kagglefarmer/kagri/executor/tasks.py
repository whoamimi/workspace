"""
MODULE 1a — Task model.

A Task is one thing a unit must do on one tile. Strategy modules (crop
planner, livestock manager) will later ADD tasks; this module only defines
the shape and the default priorities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Optional

Pos = tuple[int, int]


class Priority(IntEnum):
    """Lower number = more urgent. Tune these."""

    SAVE_LIFE = 0  # water a plant / feed an animal that dies tonight otherwise
    HARVEST_DECAY = 1  # harvest a plant that is already decaying
    FEED = 2
    WATER = 3
    HARVEST = 4
    PLACE_ANIMAL = 5
    CARE = 6
    PLANT = 7
    FERTILIZE = 8
    COLLECT_FERT = 9
    BUILD = 10
    DIG_WEED = 11
    SHED_RUN = 12  # PICKUP / DROP at the shed
    IDLE = 99


@dataclass(order=True)
class Task:
    priority: int
    deadline_hour: int  # latest hour (0-23) it must be done today
    pos: Pos = field(compare=False)
    op: list = field(
        compare=False
    )  # e.g. ["WATER"], ["PLANT", "MELON"], ["PICKUP", "WHEAT", 3]
    needs_item: Optional[tuple[str, int]] = field(default=None, compare=False)
    #   ^ item the unit must carry first, e.g. ("WHEAT", 1) for FEED, ("GOOSE", 1) for PLACE
    source: str = field(default="core", compare=False)  # which module created it

    @property
    def is_shed_task(self) -> bool:
        """PICKUP / DROP / PLACE-into-shed can run on a LOCKED shed tile."""
        return self.op[0] in ("PICKUP", "DROP") or (
            self.op[0] == "PLACE" and self.pos in _shed()
        )


def _shed():
    from ..constants import SHED_TILES

    return SHED_TILES
