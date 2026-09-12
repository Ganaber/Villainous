from .game_object import GameObject


class Token(GameObject):

    def __init__(self, front_image_path: str, back_image_path: str) -> None:
        super().__init__(front_image_path, back_image_path)