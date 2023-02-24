class Entity:
    def __init__(self, x, y, idx, team, alive=False):
        self.x = x
        self.y = y
        self.idx = idx
        self.team = team
        self.alive = alive

    def get_state(self):
        return {"x": self.x, "y": self.y, "id": self.idx, "team": self.team, "alive": self.alive}
