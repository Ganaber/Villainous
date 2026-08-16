from enum import Enum

# Used for determining what effects are done for a card for certain actions
class TriggerType(Enum):
    ON_PLAY = 1
    ON_DISCARD = 2
    ON_BOARD = 3
    ON_MOVE = 4
    ON_ACTIVATE = 5