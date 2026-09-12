from abc import ABC
from typing import Any

from engine.villain_extras import VillainExtras

class Villain(ABC):

    def __init__(self, name: str, extras: dict[VillainExtras, Any]) -> None:
        self.name = name
        self.extras = extras
