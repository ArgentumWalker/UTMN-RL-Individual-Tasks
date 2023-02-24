import numpy as np

from .world.envs import OnePlayerEnv
from .world.realm import Realm
from .world.map_loaders.single_team import SingleTeamLabyrinthMapLoader


class QMixEnv:
    def __init__(self):
        self.env = OnePlayerEnv(Realm(
            SingleTeamLabyrinthMapLoader(40, 8, 120, additional_links_max=30, additional_links_min=10),
            1, {}, playable_team_size=15, step_limit=300
        ))

    def step(self, actions):
        return self.env.step(actions)

    def reset(self):
        return self.env.reset()


class SACEnv:
    def __init__(self):
        self.env = OnePlayerEnv(Realm(
            SingleTeamLabyrinthMapLoader(40, 8, 100, additional_links_max=5, additional_links_min=0),
            1, {}, playable_team_size=5, step_limit=300
        ))

    def step(self, actions):
        return self.env.step(actions)

    def reset(self):
        return self.env.reset()


class ExploreEnv:
    def __init__(self):
        self.env = OnePlayerEnv(Realm(
            SingleTeamLabyrinthMapLoader(40, 10, 25, additional_links_min=0, additional_links_max=5),
            1, {}, playable_team_size=1, step_limit=300
        ))

    def step(self, action):
        return self.env.step([action])

    def reset(self):
        return self.env.reset()