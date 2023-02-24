import numpy as np

from pybullet_envs.gym_locomotion_envs import AntBulletEnv


class AntMoveToEnv(AntBulletEnv):
    def __init__(self, render=False):
        super().__init__(render)
        self.target = None
        self.steps = None

    def step(self, a):
        self.steps += 1
        state, _, _, _ = super(AntMoveToEnv, self).step(a)
        dist = np.linalg.norm(self.target - np.array(self.robot.body_real_xyz[:2]))
        reached_target = dist < 1e-3
        r = 1. if reached_target else 0
        d = reached_target or self.steps >= 1000
        return self._get_observation(state), r, d, {}

    def reset(self):
        state = super(AntMoveToEnv, self).reset()
        dist, angle = 1 + 100 * np.random.rand(), np.random.rand() * 2 * np.pi
        self.target = dist * np.array([np.sin(angle), np.cos(angle)]) + np.array(self.robot.body_real_xyz[:2])
        self.steps = 0
        return self._get_observation(state)

    def _get_observation(self, state):
        return np.concatenate(([state[0]], state[3:], self.target, self.robot.body_real_xyz))
