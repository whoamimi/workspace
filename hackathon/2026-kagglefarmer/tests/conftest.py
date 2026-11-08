import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture(scope="session")
def env_module():
    """The real game module, for ground-truth comparisons."""
    from kaggle_environments.envs.kaggriculture import kaggriculture
    return kaggriculture


@pytest.fixture
def real_obs():
    """A real observation from a few turns into a game (player 0)."""
    from kaggle_environments import make
    env = make("kaggriculture", configuration={"episodeSteps": 60})
    env.run(["starter", "starter"])
    return env.steps[-1][0].observation
