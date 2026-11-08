"""
MODULE 0d — Town demand model.

The town removes product from the market for free, which pushes prices back
UP over time. The seller uses this to decide whether waiting pays off.

Exact rules from the env source (with default config):
  - Every TOWN_SHOP_SELL_INTERVAL (4) turns, each unlocked shop INSTANCE
    removes 1 of each product it demands; single-product shops remove 2.
  - Every TOWN_CENTER_SELL_INTERVAL (24) turns, the town centre removes 1 of
    every product except FERTILIZER.
  - Consumption fires when step % interval == 0.
  - A new shop unlocks every 3 days (random, with replacement), max 8.

Test: tests/test_town.py.
"""
from __future__ import annotations

from .constants import (MAX_SHOP_INSTANCES, PRODUCTS, SHOPS,
                        TOWN_CENTER_PRODUCTS, TOWN_CENTER_SELL_INTERVAL,
                        TOWN_SHOP_SELL_INTERVAL, TOWN_SHOP_UNLOCK_INTERVAL,
                        TURNS_PER_DAY)


def drain_per_day(unlocked_shops: list[str]) -> dict[str, float]:
    """Units of each product the town removes per day, given current shops.

    Expected: one BAKERY -> WHEAT 7 (6 shop + 1 centre), EGG 7, others 1,
    FERTILIZER 0.  One PET_CAFE -> CARROT 13 (2 * 6 + 1).
    """
    # TODO
    raise NotImplementedError


def drain_between(unlocked_shops: list[str], step_from: int, step_to: int) -> dict[str, int]:
    """Exact units removed over steps (step_from, step_to], shops held fixed.

    Count how many multiples of each interval fall in the range.
    """
    # TODO
    raise NotImplementedError


def expected_future_drain(unlocked_shops: list[str], day: int, days_ahead: int) -> dict[str, float]:
    """Expected drain over the next `days_ahead` days, INCLUDING shops that
    are likely to unlock (each future unlock is uniform over SHOPS).

    Hint: expected extra drain of one random shop =
          mean over shops of drain_per_day([shop]) minus the centre's share.
    """
    # TODO
    raise NotImplementedError


def forecast_inventory(inventory: dict[str, int], unlocked_shops: list[str],
                       day: int, days_ahead: int,
                       my_sales: dict[str, int] | None = None,
                       opp_sales: dict[str, int] | None = None) -> dict[str, float]:
    """Market inventory `days_ahead` from now = now - drain + sales.

    Combine with prices.price() to get a price forecast per product.
    """
    # TODO
    raise NotImplementedError
