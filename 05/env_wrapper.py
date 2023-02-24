import numpy as np

from pybullet_envs.gym_locomotion_envs import AntBulletEnv
from pybullet_envs.robot_locomotors import Ant


class AntSkillsEnv(AntBulletEnv):
    def __init__(self, render=False):
        super().__init__(render)
        self.steps = None

    def step(self, a):
        self.steps += 1
        state, _, _, _ = super().step(a)
        rewards = [
            np.linalg.norm(self.robot.robot_body.speed()[:2]) * 0.3,  # Just move as fast as you can
            self.robot.body_real_xyz[2],  # Stay as high as possible
            self.robot.joints_at_limit,  # Bring joints to their limit
            -np.sum(self.robot.feet_contact),  # Floor is Lava
            -np.abs(self.robot.body_rpy[0] - np.pi / 4),
            -np.abs(self.robot.body_rpy[0] + np.pi / 4),
            -np.sum(self.robot.feet_contact) - np.abs(self.robot.body_rpy[0] + np.pi / 4),  # Dance 1
            -np.sum(self.robot.feet_contact) - np.abs(self.robot.body_rpy[0] - np.pi / 4),  # Dance 2
            -np.sum(self.robot.feet_contact) - np.abs(self.robot.body_rpy[0] + np.sin(self.steps / 10) * np.pi / 4),  # Dance 3
            -np.sum(self.robot.feet_contact) - np.abs(self.robot.body_rpy[1] + np.sin(self.steps / 10) * np.pi / 4),  # Dance 4
            np.linalg.norm(self.robot.robot_body.speed()[:2]) - 0.25 * np.mean(self.robot.feet_contact),  # Floor is hot
            np.linalg.norm(self.robot.robot_body.speed()[:2]) + 0.25 * np.mean(self.robot.feet_contact),  # Floor is nice

        ]
        d = self.steps >= 1000
        return self._get_observation(state), np.array(rewards), d, {}

    def reset(self):
        state = super().reset()
        self.steps = 0
        return self._get_observation(state)

    def _get_observation(self, state):
        return np.concatenate(([state[0], np.sin(self.steps / 10)], state[3:], self.robot.body_real_xyz))