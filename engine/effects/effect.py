from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, TypeAlias

if TYPE_CHECKING:
    from engine.game_state import GameState


EffectFunction: TypeAlias = Callable[["GameState"], None] | list["EffectFunction"]

class Effect:
    def __init__(self, name: str, description: str, function: EffectFunction) -> None:
        self.name = name
        self.description = description
        self.function = function

    def execute(self, game_state: GameState) -> None:

        # run effects in lists/sublists
        def run_effect(effect_function: EffectFunction) -> None:
            if isinstance(effect_function, list):
                for nested_item in effect_function:
                    run_effect(nested_item)
                return

            effect_function(game_state)

        # if list, run each item in list
        if isinstance(self.function, list):
            for item in self.function:
                run_effect(item)
            return

        self.function(game_state) # call the effect function