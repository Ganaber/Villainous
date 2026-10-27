from ..effects.effect import Effect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..game_state import GameState

class Action():
    def __init__(self, name: str, effect: Effect):
        self.name: str = name
        self.effect: Effect = effect

    def do_action(self, game_state: "GameState") -> None:
        self.effect.execute(game_state)