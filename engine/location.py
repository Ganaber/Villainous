from engine.action import Action

class Location():
    def __init__(self, name: str, top_actions: list[Action], bottom_actions: list[Action]):
        self.name = name
        self.top_actions = top_actions
        self.bottom_actions = bottom_actions