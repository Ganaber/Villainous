
from typing import Callable

from engine.player import Player
from engine.game_state import GameState
import engine.constants as const


# ===== Used for can_play =====

def can_pay_cost(game_state: "GameState", cost: int) -> Callable [[], bool]:
    return lambda: (game_state.get_current_player().power.amount >= cost)

# prevents player from playing effects while king richard is on the board
def king_richard_stopper(game_state: "GameState") -> Callable [[], bool]:
    return lambda: game_state.get_current_player().board.contains(const.wtia_prince_john.KING_RICHARD)

def prince_john_can_pay_cost(game_state: "GameState", cost:int) -> Callable[[], bool]:
    return lambda: can_pay_cost(game_state, cost)() and king_richard_stopper(game_state)()