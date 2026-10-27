from engine.player import Player
from engine.turn_state import TurnState

class GameState:

    def __init__(self, players: list[Player]) -> None:
        self.players: list[Player] = players
        self.current_player_index: int = 0
        self.turn_stage: TurnState = TurnState.BEFORE_GAME

    def get_current_player(self) -> Player:
        return self.players[self.current_player_index]

    def get_player_by_villain(self, villain_name: str) -> Player | None:
        for i in self.players:
            if i.villain.name == villain_name:
                return i
        return None

    def get_player_by_username(self, username: str) -> Player | None:
        for i in self.players:
            if i.username == username:
                return i

        return None

    def next_turn(self) -> None:
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def number_of_players(self) -> int:
        return len(self.players)

    def advance_turn_stage(self) -> None:
        pass