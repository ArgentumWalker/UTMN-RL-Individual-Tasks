import numpy as np
from pybullet_envs.gym_locomotion_envs import AntBulletEnv


class AntMimicEnv(AntBulletEnv):
    def __init__(self, render=False):
        super().__init__(render)
        self.demonstrations = np.load("demonstrations.npz")
        self.demonstration_idx = None
        self.steps = None

    def step(self, a):
        self.steps += 1
        state, r, _, _ = super().step(a)
        d = self.steps >= 1000 or len(self.demonstrations[self.demonstration_idx]) <= self.steps
        return self._get_observation(state), r, d, {"target_demo": self.demonstrations[self.demonstration_idx][self.steps]}

    def reset(self):
        state = super().reset()
        self.steps = 0
        self.demonstration_idx = np.random.randint(0, len(self.demonstrations))
        return self._get_observation(state)

    def _get_observation(self, state):
        return np.concatenate(([state, self.demonstrations[self.demonstration_idx][self.steps]]))