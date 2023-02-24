from .base import StochasticMapLoader
import numpy as np
import abc
from queue import PriorityQueue


class SingleTeamMapLoader(StochasticMapLoader):
    def __init__(self, size=40, spawn_radius=8, preys_num=100, spawn_points=15, spawn_attempts=30):
        self.size = size
        self.spawn_radius = spawn_radius
        self.spawn_points = spawn_points
        self.preys_num = preys_num
        self.spawn_attempts = spawn_attempts

    def _generate(self):
        generated = False
        map = np.zeros((self.size, self.size), int)
        while not generated:
            map = np.zeros((self.size, self.size), int)
            self._generate_rocks(map)
            generated = self._generate_entities(map)
        return map

    @abc.abstractmethod
    def _generate_rocks(self, map):
        pass

    def _generate_entities(self, map):
        spawn_shift = (self.size - self.spawn_radius) // 2
        for _ in range(self.spawn_points):
            attempt = 0
            x, y = self.random.randint(0, self.spawn_radius), self.random.randint(0, self.spawn_radius)
            while ((map[spawn_shift + x + 1][spawn_shift + y] == -1 and map[spawn_shift + x][
                spawn_shift + y + 1] == -1 and
                    map[spawn_shift + x - 1][spawn_shift + y] == -1 and map[spawn_shift + x][
                        spawn_shift + y - 1] == -1) or
                   map[spawn_shift + x][spawn_shift + y] != 0) and not attempt > self.spawn_attempts:
                attempt += 1
                x, y = self.random.randint(0, self.spawn_radius), self.random.randint(0, self.spawn_radius)
            if attempt > self.spawn_attempts:
                return False
            map[spawn_shift + x, spawn_shift + y] = 1

        for _ in range(self.preys_num):
            x, y = self.random.randint(0, self.size), self.random.randint(0, self.size)
            attempt = 0
            while ((map[(x + 1) % self.size][y] == -1 and map[x][(y + 1) % self.size] == -1
                    and map[x - 1][y] == -1 and map[x][y - 1] == -1) or
                   map[x][y] != 0) and not attempt > self.spawn_attempts:
                attempt += 1
                x, y = self.random.randint(0, self.size), self.random.randint(0, self.size)
            if attempt > self.spawn_attempts:
                return False
            map[x, y] = -2
        return True


class SingleTeamRocksMapLoader(SingleTeamMapLoader):
    def __init__(self, size=40, spawn_radius=8, preys_num=100, spawn_points=10, rock_spawn_proba=0.1,
                 additional_rock_spawn_proba=0.2, spawn_attempts=30):
        super().__init__(size, spawn_radius, preys_num, spawn_points, spawn_attempts)
        self.rock_spawn_proba = rock_spawn_proba
        self.additional_rock_spawn_proba = additional_rock_spawn_proba

    def _generate_rocks(self, map):
        prev_rocks = np.zeros((self.size, self.size))
        rocks = self.random.rand(self.size, self.size) < self.rock_spawn_proba
        new_rocks = rocks
        attempts = 0
        while (prev_rocks != rocks).sum() > 0 and attempts < self.spawn_attempts:
            candidates = np.logical_or(np.logical_or(np.roll(new_rocks, 1, 0), np.roll(new_rocks, -1, 0)),
                                       np.logical_or(np.roll(new_rocks, 1, 1), np.roll(new_rocks, -1, 1)))
            new_rocks = np.logical_and(candidates,
                                       self.random.rand(self.size, self.size) < self.additional_rock_spawn_proba)
            prev_rocks = rocks
            rocks = np.logical_or(rocks, new_rocks)
            attempts += 1

        map[rocks] = -1


class SingleTeamLabyrinthMapLoader(SingleTeamMapLoader):
    def __init__(self, size=40, spawn_radius=8, preys_num=100, spawn_points=10, additional_links_max=20,
                 additional_links_min=0, spawn_attempts=30):
        super().__init__(size, spawn_radius, preys_num, spawn_points, spawn_attempts)
        self.additional_links_max = additional_links_max
        self.additional_links_min = additional_links_min

    def _generate_rocks(self, map):
        cells = np.zeros((self.size // 4, self.size // 4, 4))
        expandable_cells = PriorityQueue()
        expandable_cells.put((self.random.rand(), (self.random.randint(0, self.size // 4), self.random.randint(0, self.size // 4))))
        direction_helper = np.array([[1, 0], [0, 1], [0, -1], [-1, 0]])

        while expandable_cells.qsize() > 0:
            _, (x, y) = expandable_cells.get()
            directions = (self.size + direction_helper + np.array([[x, y] for _ in range(4)])) % (self.size // 4)
            available_directions = []
            for i, (tx, ty) in enumerate(directions):
                if cells[tx, ty].sum() == 0:
                    available_directions.append(i)
            if len(available_directions) == 0:
                continue
            i = available_directions[self.random.randint(0, len(available_directions))]
            tx, ty = directions[i]
            cells[x, y, i] = 1
            cells[tx, ty, 3 - i] = 1
            expandable_cells.put((self.random.rand(), (tx, ty)))
            if len(available_directions) > 1:
                expandable_cells.put((self.random.rand(), (x, y)))

        for _ in range(self.random.randint(self.additional_links_min, self.additional_links_max+1)):
            x, y, i = self.random.randint(0, self.size // 4), self.random.randint(0, self.size // 4), self.random.randint(0, 4)
            while cells[x, y, i] > 0:
                x, y = self.random.randint(0, self.size // 4), self.random.randint(0, self.size // 4),
                i = self.random.randint(0, 4)
            cells[x, y, i] = 1
            tx, ty = (self.size + direction_helper[i] + np.array([x, y])) % (self.size // 4)
            cells[tx, ty, 3-i] = 1

        for x in range(self.size // 4):
            for y in range(self.size // 4):
                map[4 * x:4 * (x+1), 4 * y:4 * (y+1)] = -1
                map[4 * x + 1:4 * (x+1) - 1, 4 * y + 1:4 * (y+1) - 1] = 0
                if cells[x, y, 3] > 0:
                    map[4 * x, 4 * y + 1:4 * (y + 1) - 1] = 0
                if cells[x, y, 0] > 0:
                    map[4 * (x+1)-1, 4 * y + 1:4 * (y + 1) - 1] = 0
                if cells[x, y, 2] > 0:
                    map[4 * x + 1:4 * (x+1) - 1, 4 * y] = 0
                if cells[x, y, 1] > 0:
                    map[4 * x + 1:4 * (x+1) - 1, 4 * (y + 1) - 1] = 0