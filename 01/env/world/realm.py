from .grid_world import GridWorld
import copy


class Realm:
    def __init__(self, map_loader, playable_teams_num, bots={}, playable_team_size=5, step_limit=300):
        self.world = GridWorld(map_loader, playable_team_size, playable_teams_num)
        self.playable_teams_num = playable_teams_num
        self.bots = bots
        self.step_limit = step_limit
        self.step_num = 0
        self.done = False
        self.team_scores = None
        self.team_require_action = None
        self.team_acted = None
        self.actions = {}
        self.eaten = dict()

    def step(self):
        map = copy.deepcopy(self.world.map)
        for k, bot in self.bots.items():
            self.set_actions(bot.get_actions(map, k), k)
        if self.step_num < self.step_limit:
            self.step_num += 1
            self.world.set_actions(self.actions)
            self.eaten = self.world.step()
        else:
            self.done = True
            self.eaten.clear()
        self.actions.clear()
        self.update_score()
        self.team_acted = [False for _ in range(self.playable_teams_num)]

    def set_actions(self, actions, team):
        a = dict()
        for i in range(len(actions)):
            a[(team, i)] = actions[i]
        self.actions.update(a)
        if team not in self.bots:
            self.team_acted[team] = True
            for i in range(self.playable_teams_num):
                if not self.team_acted[i] and self.team_require_action[i]:
                    return
            self.step()

    def update_score(self):
        for key, value in self.eaten.items():
            if key[0] == self.world.playable_teams_num:
                s = 1
            else:
                s = 3 + int(max(0, self.team_scores[key[0]] - self.team_scores[value[0]])) * 0.25
            self.team_scores[value[0]] += s

    def reset(self, seed=None):
        self.world.reset(seed)
        self.eaten = dict()
        self.actions = dict()
        self.done = False
        self.team_scores = [0. for _ in range(self.playable_teams_num)]
        self.team_require_action = [(i not in self.bots) for i in range(self.playable_teams_num)]
        self.team_acted = [False for _ in range(self.playable_teams_num)]

        map = copy.deepcopy(self.world.map)
        for k, bot in self.bots.items():
            bot.reset(map, k)
        self.step_num = 0

    def render(self):
        pass