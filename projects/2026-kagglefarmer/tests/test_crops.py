"""Module 0c: values from the README Object Types table."""
import pytest

from kagri import crops


@pytest.mark.parametrize("crop,expected", [("WHEAT", 4), ("CARROT", 3), ("MELON", 6),
                                           ("TOMATO", 4), ("STRAWBERRY", 4)])
def test_peak_yield(crop, expected):
    assert crops.peak_yield(crop) == expected


@pytest.mark.parametrize("crop,expected", [("WHEAT", 6), ("CARROT", 4), ("MELON", 6)])
def test_peak_yield_fertilized(crop, expected):
    assert crops.peak_yield(crop, fertilized=True) == expected


@pytest.mark.parametrize("crop,expected", [("WHEAT", 4), ("CARROT", 3), ("MELON", 10)])
def test_best_harvest_age(crop, expected):
    assert crops.best_harvest_age(crop) == expected


def test_window_start():
    assert crops.window_start("WHEAT") == 2
    assert crops.window_start("CARROT") == 2
    assert crops.window_start("MELON") == 6


def test_can_mature():
    assert crops.can_mature("MELON", 19)
    assert not crops.can_mature("MELON", 20)
    assert crops.can_mature("WHEAT", 25)
