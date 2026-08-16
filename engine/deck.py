import random

class Deck:
    def __init__(self, cards: list):
        self.draw_pile = cards
        self.discard_pile = []

    # Remove top `amount` cards from draw pile
    def draw(self, amount: int = 1):
        drawn_cards = []
        for _ in range(amount):
            if self.draw_pile:
                drawn_cards.append(self.draw_pile.pop())
        return drawn_cards

    # Add `cards` to discard pile
    def discard(self, cards: list):
        self.discard_pile.extend(cards)

    # Shuffle discard pile into draw pile
    def shuffle(self):
        self.draw_pile.extend(self.discard_pile)
        self.discard_pile.clear()
        random.shuffle(self.draw_pile)

    # Removes card from draw pile or discard pile
    def delete(self, card):
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        elif card in self.discard_pile:
            self.discard_pile.remove(card)

    # Insert card to certain position in draw pile
    def insert_card(self, card, position: int):
        self.draw_pile.insert(position, card)

    # Find card by name in draw or discard pile
    def find(self, card_name: str):
        for card in self.draw_pile:
            if card.name == card_name:
                return card
        for card in self.discard_pile:
            if card.name == card_name:
                return card
        return None

    # Find card by name in discard pile
    def search_discard(self, card_name: str):
        for card in self.discard_pile:
            if card.name == card_name:
                return card
        return None

    # Returns draw pile
    def get_draw(self):
        return self.draw_pile

    # Returns discard pile
    def get_discard(self):
        return self.discard_pile
