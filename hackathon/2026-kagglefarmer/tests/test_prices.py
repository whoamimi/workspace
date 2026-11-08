"""Module 0b: must match the env to the dollar."""
import pytest

from kagri import prices
from kagri.constants import PRODUCTS

INVENTORIES = [0, 5000, 9000, 9500, 9800, 9900, 9999, 10000, 10001,
               10050, 10100, 10300, 10500, 11000, 12000, 20000]


@pytest.mark.parametrize("item", PRODUCTS)
@pytest.mark.parametrize("inv", INVENTORIES)
def test_price_matches_env(env_module, item, inv):
    assert prices.price(item, inv) == env_module.market_price(item, inv)


@pytest.mark.parametrize("func", ["linear", "sq", "sqrt", "log", "log10", "hinge"])
def test_shape_matches_env(env_module, func):
    for x in (0, 1, 50, 200, 450, 900):
        assert prices.shape(func, x, 450) == pytest.approx(env_module._shape(func, x, 450))


def test_simulate_sell_is_sequential(env_module):
    inv, total = 10000, 0
    for _ in range(20):
        p = env_module.market_price("MELON", inv)
        total += p
        inv += 1 if p > 1 else 0
    assert prices.simulate_sell("MELON", 10000, 20) == (total, inv)


def test_floor_does_not_add_inventory():
    rev, inv = prices.simulate_sell("MELON", 12000, 5)   # deep glut -> $1
    assert rev == 5 and inv == 12000


def test_marginal_revenue_sums():
    mr = prices.marginal_revenue("MILK", 10000, 10)
    assert len(mr) == 10 and sum(mr) == prices.simulate_sell("MILK", 10000, 10)[0]
    assert mr == sorted(mr, reverse=True)                  # selling pushes price down


def test_buy_quoted_post_buy(env_module):
    cost, inv = prices.buy_cost("WHEAT", 10000, 1)
    assert cost == env_module.market_price("WHEAT", 9999) and inv == 9999
