from abc import ABC
from typing import Any

from engine.villain_extras import VillainExtras

class Villain(ABC):

    def __init__(self, name: str) -> None:
        self.name = name