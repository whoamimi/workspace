"""Module 1: synthetic states, no env needed."""
from kagri import state as S
from kagri.executor import Priority, Task, planner, router


def make_state(plants=(), seeds=None, farmer=(4, 4), hour=5, day=3, hands=()):
    farm = S.FarmState(money=3000, farmer=farmer, hands=list(hands),
                       unlocked_quadrants=["NW"], hires_today=len(hands))
    for p in plants:
        farm.plants[p.pos] = p
    farm.empty = {(x, y) for x in range(5) for y in range(5)} - set(farm.plants)
    farm.locked = {(x, y) for x in range(10) for y in range(10)} - {(x, y) for x in range(5) for y in range(5)}
    opp = S.FarmState(3000, (4, 4), [], ["NW"], 0)
    return S.GameState(0, day, hour, day * 24 + hour, farm, opp, {}, {}, [], {},
                       seeds or {}, [{} for _ in range(1 + len(hands))])


def test_step_toward():
    assert router.step_toward((2, 2), (2, 0)) == "NORTH"     # NORTH = y - 1
    assert router.step_toward((2, 2), (2, 4)) == "SOUTH"
    assert router.step_toward((2, 2), (4, 2)) == "EAST"
    assert router.step_toward((2, 2), (2, 2)) == "PASS"


def test_nearest_shed_tile():
    assert router.nearest_shed_tile((0, 0)) == (4, 4)
    assert router.nearest_shed_tile((9, 9)) == (5, 5)


def test_fresh_seed_is_save_life():
    seed = S.PlantTile((1, 1), "WHEAT", 3, False, 1, 1, 200, -1)
    tasks = planner.water_tasks(make_state([seed]))
    assert len(tasks) == 1 and tasks[0].priority == Priority.SAVE_LIFE


def test_watered_plant_needs_no_task():
    p = S.PlantTile((1, 1), "WHEAT", 1, True, 0, 1, 200, -1)
    assert planner.water_tasks(make_state([p])) == []


def test_plant_conflict_rule():
    """Two units, one seed: never assign PLANT to both (both would fail)."""
    gs = make_state(seeds={"MELON": 1}, hands=[(4, 4)])
    tasks = [Task(Priority.PLANT, 16, (0, 0), ["PLANT", "MELON"]),
             Task(Priority.PLANT, 16, (1, 0), ["PLANT", "MELON"])]
    plants = [t for t in router.assign(gs, tasks).values() if t.op[0] == "PLANT"]
    assert len(plants) <= 1


def test_op_at_target_is_task_op():
    gs = make_state(farmer=(1, 1))
    t = Task(Priority.WATER, 23, (1, 1), ["WATER"])
    assert router.op_for(gs, 0, t) == ["WATER"]
