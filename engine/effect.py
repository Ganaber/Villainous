from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from engine.game_state import GameState


class Effect():

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    # Do the effect
    def execute(self, game_state: GameState) -> None:
        pass