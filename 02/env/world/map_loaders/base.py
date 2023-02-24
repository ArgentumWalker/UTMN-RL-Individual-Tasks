import abc
import numpy as np


class MapLoader:
    @abc.abstractmethod
    def load_next(self, seed=None):
        pass


class MixedMapLoader(MapLoader):
    def __init__(self, loaders):
        self.loaders = loaders
        self.i = 0

    def load_next(self, seed=None):
        map = self.loaders[self.i].load_next(seed)
        self.i = (self.i + 1) % len(self.loaders)
        return map


class StochasticMapLoader(MapLoader):
    def load_next(self, seed=None):
        self.random = np.random.RandomState(seed)
        map = self._generate()
        while map is None or not self.check_reachability(map):
            map = self._generate()
        return map

    @abc.abstractmethod
    def _generate(self):
        pass

    @staticmethod
    def check_reachability(map):
        important_cells = np.logical_and(map != -1, map != 0)
        mask = map != -1
        reached_cells = np.zeros_like(important_cells)
        i = np.argmax(important_cells)
        x, y = i // len(important_cells), i % len(important_cells)
        reached_cells[x, y] = 1
        new_reached_cells = reached_cells
        while new_reached_cells.sum() > 0:
            new_reached_cells = np.logical_and(np.logical_or(
                np.logical_or(np.roll(reached_cells, 1, 0), np.roll(reached_cells, -1, 0)),
                np.logical_or(np.roll(reached_cells, 1, 1), np.roll(reached_cells, -1, 1))
            ), mask)
            new_reached_cells = np.logical_and(new_reached_cells, np.logical_not(reached_cells))
            reached_cells = np.logical_or(reached_cells, new_reached_cells)
        return np.logical_and(important_cells, np.logical_not(reached_cells)).sum() == 0