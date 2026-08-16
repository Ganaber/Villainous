from .effect import Effect

class Action():
    def __init__(self, name: str, effect: Effect):
        self.name = name
        self.effect = effect