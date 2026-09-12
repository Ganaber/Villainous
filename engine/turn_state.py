from enum import Enum

# Used for determining what effects are done for a card for certain actions
class TurnState(Enum):
    BEFORE_GAME = -1

    START_OF_TURN = 1       # Checking conditions
    BEFORE_MOVE = 2         # Before player moves
    DURING_MOVE = 3         # While player selecting where to move
    PERFORMING_ACTION = 4   # After player moved
    END_OF_TURN = 5         # Player has ended turn

    # During another player's condition. Freezes current player's turn
    DURING_CONDITION = 10