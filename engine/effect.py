from __future__ import annotations
from contextvars import ContextVar
from typing import TYPE_CHECKING

if TYPE_CHECKING: # used since it's a circular dependency with GameState
    from engine.game_state import GameState


_current_game_state: ContextVar[GameState | None] = ContextVar(
    "current_game_state", default=None
)


class Effect:

    def __init__(self, name: str, description: str, effects: list[Effect] | None = None) -> None:
        self.name = name
        self.description = description
        self.effects = list(effects) if effects is not None else []

    @property
    def game_state(self) -> GameState:
        game_state = _current_game_state.get()
        if game_state is None:
            # TODO: Add logging error here
            raise RuntimeError("Effect must be executed by a GameState context")
        return game_state

    def execute(self, game_state: GameState | None = None) -> None:
        state_token = None
        if game_state is not None:
            state_token = _current_game_state.set(game_state)

        try:
            self._execute()
        finally:
            if state_token is not None:
                _current_game_state.reset(state_token)

    def _execute(self) -> None:
        for effect in self.effects:
            effect.execute()