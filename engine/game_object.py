from abc import ABC

# Abstract base class for all game objects that are shown in the UI
class GameObject(ABC):
    def __init__(self, front_image_path:str, back_image_path:str) -> None:
        self.front_image_path = front_image_path
        self.back_image_path = back_image_path