"""
MODULE 2a — Order book.

Every module wants market orders (seller, crop planner buying seeds, hiring,
land). Only MAX_MARKET_ORDERS (10) per turn are processed; extras are
silently dropped. The order book collects requests with priorities and
emits at most 10, in a sensible order.

Ordering matters: orders run in list order, one unit at a time, interleaved
with the opponent. SELL before BUY frees cash for purchases in the same turn.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..constants import MAX_MARKET_ORDERS


@dataclass(order=True)
class Order:
    priority: int                         # lower = more important
    op: list = field(compare=False)       # e.g. ["SELL", "MELON", 3], ["HIRE"], ["BUY_LAND"]
    source: str = field(default="", compare=False)
    cost_estimate: float = field(default=0.0, compare=False)   # >0 spends money, <0 earns


class OrderBook:
    def __init__(self):
        self.orders: list[Order] = []

    def add(self, op: list, priority: int = 50, source: str = "", cost_estimate: float = 0.0):
        self.orders.append(Order(priority, op, source, cost_estimate))

    def emit(self, money: float) -> list[list]:
        """Return at most MAX_MARKET_ORDERS ops.

        TODO:
          1. merge duplicate SELL/BUY orders for the same item (sum quantities)
          2. put SELLs first, then spending orders by priority
          3. drop spending orders whose running cost exceeds `money`
             (+ expected sale revenue if you want to be bold)
          4. truncate to MAX_MARKET_ORDERS
        """
        # TODO
        raise NotImplementedError

    def clear(self):
        self.orders.clear()
