from engine.location import Location
from engine.game_object import GameObject

# Board layout and art only. The mover's position is part of the current player state, so it lives in Player object
class Board(GameObject):
    def __init__(self, locations: list[Location], front_image_path: str, back_image_path: str, mover_image_path: str) -> None:
        super().__init__(front_image_path, back_image_path)
        self.locations: list[Location] = locations
        self.mover_image_path: str = mover_image_path

    def get_location(self, location: str) -> Location:
        for board_location in self.locations:
            if board_location.name == location:
                return board_location

        raise ValueError(f"Location not found: {location}")

    def contains(self, name: str) -> bool:
        for l in self.locations:
            if l.contains(name):
                return True
        return False

    def get_adjacent_locations(self, location: str) -> list[Location]:
        adjacent: list[Location] = []
        for i, board_location in enumerate(self.locations):
            if board_location.name == location:
                if i > 0:
                    adjacent.append(self.locations[i - 1])
                if i + 1 < len(self.locations):
                    adjacent.append(self.locations[i + 1])
                break
        return adjacent
