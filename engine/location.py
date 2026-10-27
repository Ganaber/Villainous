from engine.actions.action import Action
from engine.cards.card import Card
from engine.token import Token

class Location():
    def __init__(self, name: str, top_actions: list[Action], bottom_actions: list[Action], top_cards: list[Card | Token], bottom_cards: list[Card | Token]) -> None:
        self.name: str = name
        self.top_actions: list[Action] = top_actions
        self.bottom_actions: list[Action] = bottom_actions
        self.top_cards: list[Card | Token] = top_cards
        self.bottom_cards: list[Card | Token] = bottom_cards


    # adding card to location
    def add(self, card: Card | Token, top: bool) -> None:
        if top:
            self.top_cards.append(card)
        else:
            self.bottom_cards.append(card)

    # removing card from location
    def remove(self, card: Card | Token, top: bool) -> None:
        cards = self.top_cards if top else self.bottom_cards
        if card in cards:
            cards.remove(card)

    # Checking if location has card name
    def contains(self, name: str) -> bool:
        for c in (self.top_cards, self.bottom_cards):
            if c.name == name:
                return True
        return False

