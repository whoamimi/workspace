"""
MODULE 0b — Price model.

Reimplement the market's price curve exactly, then build the tools the seller
needs on top of it: "what will I earn if I sell n units now?"

Spec:
    price(inv) = base + sign * amp * f(|inv - I0|)
      sign = +1 if inv < I0 (scarcity), -1 if inv > I0 (glut)
      amp  = target * base / f(T)
      f in {linear, sq, sqrt, log (= ln(1+x)), log10 (= log10(1+x)), hinge}
      hinge: u = x / T;  f = u + HINGE_GAIN * max(0, u - 1)^2
    Floored at PRICE_FLOOR, rounded to nearest int.

Selling mechanics (one unit at a time):
    - You receive the price quoted at the PRE-sell inventory.
    - Then inventory += 1, EXCEPT when the price was at the $1 floor.
    - Both players' orders interleave unit by unit (ignore the opponent in
      v1; add them in `simulate_sell` later via `opp_units`).

Buying (WHEAT and FERTILIZER only):
    - Price is quoted at the POST-buy inventory, then inventory -= 1.

Test: tests/test_prices.py compares you to the real env at many inventories.
"""
from __future__ import annotations

from .constants import HINGE_GAIN, MARKET_PARAMS, PRICE_FLOOR


def shape(func: str, x: float, T: float | None = None) -> float:
    """Shape function f(x). Clamp x at 0 first. Unknown func -> linear."""
    # TODO
    raise NotImplementedError


def price(item: str, inventory: int, params: dict | None = None) -> int:
    """Market sale price for `item` at market `inventory`."""
    # TODO: choose below/above side, compute amp, apply sign, round, floor
    raise NotImplementedError


def simulate_sell(item: str, inventory: int, n: int, opp_units: int = 0,
                  params: dict | None = None) -> tuple[int, int]:
    """Sell n units one at a time. Return (total_revenue, new_inventory).

    v1: ignore opp_units.
    v2: interleave `opp_units` opponent sales (both get the same price per
        round, then inventory rises by 2 unless at the floor).
    """
    # TODO
    raise NotImplementedError


def marginal_revenue(item: str, inventory: int, n: int) -> list[int]:
    """Price received for each of the next n units, in order.

    Handy for the seller: stop selling once the next unit's price drops
    below what you expect to get tomorrow.
    """
    # TODO
    raise NotImplementedError


def buy_cost(item: str, inventory: int, n: int) -> tuple[int, int]:
    """Cost to BUY_PRODUCT n units (WHEAT or FERTILIZER). Return (cost, new_inv)."""
    # TODO: quote each unit at the post-buy inventory (inventory - 1)
    raise NotImplementedError


def glut_units_to_price(item: str, inventory: int, target_price: int) -> int:
    """How many units can be sold before the price falls below target_price.

    Useful as a quick cap on how much to sell in one go.
    """
    # TODO: simple loop, or binary search for speed
    raise NotImplementedError
