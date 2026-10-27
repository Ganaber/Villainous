from typing import TYPE_CHECKING, Callable

from engine.effects.effect import Effect
from engine.cards.trigger_type import TriggerType
from engine.game_object import GameObject
import engine.constants as const

if TYPE_CHECKING:
    from engine.game_state import GameState

# Abstract class. Has subclasses for Ally, Hero, Item, Effect, Condition, and Custom
class Card(GameObject):

    def __init__(self, name: str, cost: int, 
                 front_image_path: str, 
                 back_image_path: str, 
                 type: str, deck_type: str, 
                 can_play: Callable,
                 effects: dict[TriggerType, Effect]) -> None:
        super().__init__(front_image_path, back_image_path)
        self.name = name
        self.cost = cost
        self.effects = effects
        self.type = type # Ally, Item, Effect, Hero, Condition, etc
        self.deck_type = deck_type # Villain or Fate usuallys
        self.attached_items = []
        self.play = can_play

    # each card will have their own can play method
    def can_play(self, game_state: "GameState") -> bool:
        can = self.play()
        if isinstance(can, bool):
            return can
        return False # TODO: Add error function here

    # when this card is played to the board
    def on_play(self, game_state: "GameState") -> None:
        if TriggerType.ON_PLAY in self.effects:
            self.effects[TriggerType.ON_PLAY].execute(game_state)

    # when this card is discarded from the board, not from the hand
    def on_discard(self, game_state: "GameState") -> None:
        if TriggerType.ON_DISCARD in self.effects:
            self.effects[TriggerType.ON_DISCARD].execute(game_state)

    # while this card is on the board
    def on_board(self, game_state: "GameState") -> None:
        if TriggerType.ON_BOARD in self.effects:
            self.effects[TriggerType.ON_BOARD].execute(game_state)

    # when this card is moved from one location to another
    def on_move(self, game_state: "GameState") -> None:
        if TriggerType.ON_MOVE in self.effects:
            self.effects[TriggerType.ON_MOVE].execute(game_state)

    # when this card is activated (if it can be activated)
    def on_activate(self, game_state: "GameState") -> None:
        if TriggerType.ON_ACTIVATE in self.effects:
            self.effects[TriggerType.ON_ACTIVATE].execute(game_state)