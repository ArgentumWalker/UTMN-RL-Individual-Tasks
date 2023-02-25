import copy

import numpy as np


class OnePlayerEnv:
    def __init__(self, realm):
        self.realm = realm

    def step(self, actions):
        self.realm.set_actions(actions, 0)
        state = copy.deepcopy(self.realm.world.map)
        info = {
            "eaten": copy.deepcopy(self.realm.eaten),
            "preys": copy.deepcopy([prey.get_state() for prey in self.realm.world.preys]),
            "predators": copy.deepcopy([predator.get_state() for predator in self.realm.world.teams[0].values()]),
            "scores": copy.deepcopy(self.realm.team_scores)
        }
        done = self.realm.done or len(self.realm.world.eaten_preys) == len(self.realm.world.preys)
        return state, done, info

    def reset(self, seed=None):
        self.realm.reset(seed)
        state = copy.deepcopy(self.realm.world.map)
        info = {
            "eaten": copy.deepcopy(self.realm.eaten),
            "preys": copy.deepcopy([prey.get_state() for prey in self.realm.world.preys]),
            "predators": copy.deepcopy([predator.get_state() for predator in self.realm.world.teams[0].values()]),
            "scores": copy.deepcopy(self.realm.team_scores)
        }
        return state, info