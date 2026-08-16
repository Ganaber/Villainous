from engine.cards.card import Card
from engine.effect import Effect
from engine.cards.trigger_type import TriggerType


# Shared by AllyCard and HeroCard
class CombatantCard(Card):

    def __init__(self, name: str, cost: int, front_image_path: str, back_image_path: str, effects: dict[TriggerType, Effect], strength: int) -> None:
        super().__init__(name, cost, front_image_path, back_image_path, effects)
        self.strength = strength
