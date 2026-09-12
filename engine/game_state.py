from engine.player import Player
from engine.turn_state import TurnState

class GameState:

    def __init__(self, players: list[Player]) -> None:
        self.players: list[Player] = players
        self.current_player_index: int = 0
        self.turn_stage: TurnState = TurnState.BEFORE_GAME

    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]

    def next_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def number_of_players(self) -> int:
        return len(self.players)

    def advance_turn_stage(self) -> None:
        if self.turn_stage == TurnState.BEFORE_GAME:
            self.turn_stage = TurnState.START_OF_TURN
        elif self.turn_stage == TurnState.START_OF_TURN:
            self.turn_stage = TurnState.BEFORE_MOVE
        elif self.turn_stage == TurnState.BEFORE_MOVE:
            self.turn_stage = TurnState.DURING_MOVE
        elif self.turn_stage == TurnState.DURING_MOVE:
            self.turn_stage = TurnState.PERFORMING_ACTION
        elif self.turn_stage == TurnState.PERFORMING_ACTION:
            self.turn_stage = TurnState.END_OF_TURN
        elif self.turn_stage == TurnState.END_OF_TURN:
            self.next_turn()
            self.turn_stage = TurnState.START_OF_TURN
        else:
            # TODO: Add logging error here
            pass
        # TODO: Add condition logic here for DURING_CONDITION state