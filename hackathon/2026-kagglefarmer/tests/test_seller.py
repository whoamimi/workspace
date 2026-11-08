"""Module 2."""
from kagri.market import OrderBook, Seller
from tests.test_executor import make_state


def test_orderbook_caps_at_10():
    book = OrderBook()
    for i in range(15):
        book.add(["SELL", "WHEAT" if i % 2 else "CARROT", 1], priority=i)
        book.add(["BUY_SEED", "MELON", 1], priority=i, cost_estimate=80)
    assert len(book.emit(10_000)) <= 10


def test_orderbook_sells_before_buys():
    book = OrderBook()
    book.add(["BUY_SEED", "MELON", 1], priority=0, cost_estimate=80)
    book.add(["SELL", "WHEAT", 3], priority=90)
    assert book.emit(1000)[0][0] == "SELL"


def test_orderbook_respects_budget():
    book = OrderBook()
    book.add(["BUY_LAND"], priority=0, cost_estimate=1000)
    assert book.emit(500) == []


def _state_with_shed(day, hour, shed):
    gs = make_state(day=day, hour=hour)
    gs.shed = dict(shed)
    gs.market_inventory = {k: 10000 for k in ("WHEAT", "MELON", "MILK", "CARROT")}
    gs.prices = {"WHEAT": 25, "MELON": 250, "MILK": 160, "CARROT": 35}
    return gs


def test_last_day_sells_everything():
    gs = _state_with_shed(29, 21, {"MELON": 7, "WHEAT": 3})
    book = OrderBook()
    Seller().orders(gs, book)
    sold = {}
    for op in book.emit(0):
        if op[0] == "SELL":
            sold[op[1]] = sold.get(op[1], 0) + op[2]
    assert sold == {"MELON": 7, "WHEAT": 3}


def test_never_sells_more_than_shed():
    gs = _state_with_shed(10, 5, {"MILK": 4})
    book = OrderBook()
    Seller().orders(gs, book)
    assert sum(op[2] for op in book.emit(0) if op[0] == "SELL" and op[1] == "MILK") <= 4
