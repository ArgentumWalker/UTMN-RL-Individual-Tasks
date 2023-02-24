import numpy as np
import copy
import cv2
import os


class RenderedEnvWrapper:
    def __init__(self, base_env):
        self.base_env = base_env
        self.realm = self.base_env.realm
        self.frames = []
        self.road_color = np.array((1., 1., 1.))
        self.stone_color = np.array((0.2, 0.2, 0.2))
        self.prey_color = np.array((0., 0.8, 0.))
        self.team_colors = [
            np.array((0.8, 0., 0.)),
            np.array((0., 0., 0.8)),
            np.array((0.8, 0., 0.8)),
            np.array((0., 0.8, 0.8)),
            np.array((0.8, 0.8, 0.))
        ]

    def step(self, *args, **kwargs):
        res = self.base_env.step(*args, **kwargs)
        self.frames.append(self._get_frame())
        return res

    def reset(self):
        res = self.base_env.reset()
        self.frames = [self._get_frame()]
        return res

    def _get_frame(self):
        map = copy.deepcopy(self.base_env.realm.world.map)
        frame = np.zeros(map.shape[:2])
        frame[np.logical_and(map[:, :, 0] == -1, map[:, :, 1] == 0)] = -1
        frame[np.logical_and(map[:, :, 0] == -1, map[:, :, 1] == -1)] = -2
        for i in range(self.base_env.realm.world.playable_teams_num + 1):
            frame[map[:, :, 0] == i] = i
        return frame

    def render(self, dir="render", resize_factor=8):
        os.makedirs(dir, exist_ok=True)
        for i in range(len(self.frames)):
            frame = self.frames[i]
            img = np.zeros((frame.shape[0], frame.shape[1], 3))
            img[frame == -1] = self.road_color
            img[frame == -2] = self.stone_color
            for j in range(self.base_env.realm.world.playable_teams_num):
                img[frame == j] = self.team_colors[j]
            img[frame == self.base_env.realm.world.playable_teams_num] = self.prey_color
            img = img * 255
            img = cv2.resize(img, (int(img.shape[1] * resize_factor), int(img.shape[0] * resize_factor)),
                             interpolation=cv2.INTER_NEAREST)
            cv2.imwrite(f"{dir}/{i}.png", img)