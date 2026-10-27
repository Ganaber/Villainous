from abc import ABC, abstractmethod
from typing import Any

from engine.villain_extras import VillainExtras

class Villain(ABC):

    def __init__(self, name: str, extras: dict[VillainExtras, Any]) -> None:
        self.name = name
        self.extras = extras

    @abstractmethod
    def win_condition(self) -> bool:
        # What game state this villain needs to win
        pass
