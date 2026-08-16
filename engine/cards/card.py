from typing import Optional
from abc import ABC, abstractmethod
from engine.effect import Effect
from engine.cards.trigger_type import TriggerType

# Abstract class. Has subclasses for Ally, Hero, Item, Effect, Condition, and Custom. These are also subclasses, and each individual card will have their own class and own effects
class Card(ABC):

    def __init__(self, name: str, cost: int, front_image_path: str, back_image_path: str, effects: dict[TriggerType, Effect]) -> None:
        self.name = name
        self.cost = cost
        self.front_image_path = front_image_path
        self.back_image_path = back_image_path
        self.effects = effects

    def can_play(self) -> bool:
        pass

    def on_play(self):
        if TriggerType.ON_PLAY in self.effects:
            self.effects[TriggerType.ON_PLAY].execute()

    # when this card is discarded from the board, not from the hand
    def on_discard(self):
        if TriggerType.ON_DISCARD in self.effects:
            self.effects[TriggerType.ON_DISCARD].execute()

    def on_board(self):
        if TriggerType.ON_BOARD in self.effects:
            self.effects[TriggerType.ON_BOARD].execute()

    def on_move(self):
        if TriggerType.ON_MOVE in self.effects:
            self.effects[TriggerType.ON_MOVE].execute()

    def on_activate(self):
        if TriggerType.ON_ACTIVATE in self.effects:
            self.effects[TriggerType.ON_ACTIVATE].execute()