from .base import MapLoader
import os
import numpy as np


class PregeneratedMapLoader(MapLoader):
    def __init__(self, dir=""):
        self.dir = dir
        self.files = os.listdir(dir)
        self.i = 0

    def load_next(self, seed=None):
        map = np.load(f"{self.dir}/{self.files[self.i]}")
        self.i = (self.i + 1) % len(self.files)
        return map