from engine.location import Location
from engine.game_object import GameObject

# Board layout and art only. The mover's position is player state, so it lives on Player.
class Board(GameObject):
    def __init__(self, locations: list[Location], front_image_path: str, back_image_path: str, mover_image_path: str) -> None:
        super().__init__(front_image_path, back_image_path)
        self.locations: list[Location] = locations
        self.mover_image_path: str = mover_image_path
