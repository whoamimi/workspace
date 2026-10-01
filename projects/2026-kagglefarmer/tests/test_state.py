"""Module 0a."""
from kagri import state as S


def test_parse_real_obs(real_obs):
    gs = S.parse(real_obs)
    assert gs.day == real_obs["day"] and gs.hour == real_obs["hour"]
    f = gs.my_farm
    assert len(f.locked) == 75                     # only NW unlocked
    assert len(f.plants) + len(f.animals) + len(f.weeds) + len(f.empty) == 25
    assert f.farmer == tuple(real_obs["farms"][0]["farmer"])


def test_new_seed_dies_if_unwatered():
    p = S.PlantTile((0, 0), "WHEAT", 3, False, 1, 1, 200, -1)
    assert p.dies_tonight_if_unwatered()
    p.watered_today = True
    assert not p.dies_tonight_if_unwatered()
