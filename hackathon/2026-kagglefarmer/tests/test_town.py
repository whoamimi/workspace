"""Module 0d."""
from kagri import town


def test_centre_only():
    d = town.drain_per_day([])
    assert d["WHEAT"] == 1 and d["MILK"] == 1 and d.get("FERTILIZER", 0) == 0


def test_bakery():
    d = town.drain_per_day(["BAKERY"])
    assert d["WHEAT"] == 7 and d["EGG"] == 7 and d["MILK"] == 1


def test_single_product_shop_doubles():
    assert town.drain_per_day(["PET_CAFE"])["CARROT"] == 13


def test_duplicates_stack():
    assert town.drain_per_day(["YARN_STORE", "YARN_STORE"])["WOOL"] == 25


def test_drain_between_matches_rate():
    assert town.drain_between(["BAKERY"], 0, 24)["WHEAT"] == 7
