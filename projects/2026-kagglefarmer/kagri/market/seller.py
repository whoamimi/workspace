"""
MODULE 2b — Market seller (optimal liquidation with price impact).

Problem: you hold q units of item i in the shed, with H turns left. Each unit
sold moves the price against you (prices.py); the town slowly drains market
inventory, which moves the price back up (town.py). Unsold units at the end
are worth 0. Maximise total revenue.

Suggested versions:
  v1  threshold:  sell while the next unit's price >= reservation price.
  v2  DP:         V[t][q] = max_k ( rev(k units at t) + V[t+1][q-k] ),
                  with inventory evolving by +k (sales) - drain(t).
                  Solve once per day per item; q <= 100, t = remaining days
                  (daily granularity is enough). Execute today's k across
                  the day in small chunks.
  v3  opponent-aware: add forecast opponent sales to the inventory path
                  (Module 6 later).

Hard constraints:
  - SELL draws only from the SHED (not from what units carry).
  - Shed holds 100 non-seed items; holding stock blocks new harvests.
  - Last day: sell everything left (value 0 otherwise).
  - Keep WHEAT you need as animal feed (reserve), and FERTILIZER you plan
    to use.

Metric: realised average price / base price, per product.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import prices, town
from ..constants import DAYS, MARKET_PARAMS
from ..state import GameState
from .orderbook import OrderBook


@dataclass
class SellerConfig:
    chunk_premium: int = 2          # max units per order for premium goods
    chunk_staple: int = 5
    premium: set = field(default_factory=lambda: {"STRAWBERRY", "MELON", "MILK", "WOOL"})
    shed_pressure_at: int = 80      # start selling harder above this shed fill
    endgame_hour: int = 20          # last day: dump everything from this hour


def reservation_price(state: GameState, item: str) -> float:
    """Lowest price worth accepting NOW = expected price tomorrow (or later).

    v1: price at forecast inventory after one day of town drain
        (town.forecast_inventory + prices.price).
    Return 0 on the last day (anything beats 0).
    """
    # TODO
    raise NotImplementedError


def liquidation_dp(item: str, inventory: int, qty: int, days_left: int,
                   drain_per_day: float) -> list[int]:
    """Optimal units to sell on each remaining day (v2).

    Returns a list of length days_left + 1 (today first) summing to <= qty.
    Use prices.simulate_sell for revenue and model the inventory as
        inv_next = inv + sold - drain_per_day.
    """
    # TODO
    raise NotImplementedError


def reserves(state: GameState) -> dict[str, int]:
    """Units to keep, never sell: e.g. WHEAT for tomorrow's animal feed,
    FERTILIZER you plan to apply. Empty dict for a crops-only agent."""
    # TODO
    raise NotImplementedError


class Seller:
    def __init__(self, config: SellerConfig | None = None):
        self.cfg = config or SellerConfig()
        self.daily_plan: dict[str, int] = {}   # item -> units still to sell today
        self.plan_day = -1

    def reset(self):
        self.daily_plan.clear()
        self.plan_day = -1

    def plan_today(self, state: GameState) -> dict[str, int]:
        """Once per day: how many units of each item to sell today.
        v1: threshold rule.  v2: liquidation_dp()[0] per item."""
        # TODO
        raise NotImplementedError

    def orders(self, state: GameState, book: OrderBook) -> None:
        """Add this turn's SELL orders to the order book.

        TODO:
          1. if state.day != self.plan_day: self.daily_plan = plan_today(state)
          2. last day and hour >= endgame_hour: SELL everything (minus nothing)
          3. otherwise, for each item left in today's plan, sell a chunk
             if prices.price(...) >= reservation_price(...)
          4. sell harder when shed fill > shed_pressure_at
          5. decrement self.daily_plan by what you queued
        """
        # TODO
        raise NotImplementedError
