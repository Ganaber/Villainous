import random
from engine.cards.card import Card

# Both piles are stored bottom-first: index 0 is the bottom card, index -1 (end of list) is the top card. Drawing pops from end
class Deck:
    def __init__(self, cards: list[Card]):
        self.draw_pile = cards
        self.discard_pile = []

    # Remove top `amount` cards from draw pile. Automatically recycles the discard pile when the draw pile runs out mid-draw
    def draw(self, amount: int = 1) -> list[Card]:
        drawn_cards = []
        for _ in range(amount):
            if not self.draw_pile:
                self.recycle_discard()
            if not self.draw_pile:
                break # both piles are empty, nothing left to draw
            drawn_cards.append(self.draw_pile.pop())
        return drawn_cards

    # Add `cards` to discard pile
    def discard(self, cards: list[Card]) -> None:
        self.discard_pile.extend(cards)

    # Shuffle the draw pile in place
    def shuffle(self) -> None:
        random.shuffle(self.draw_pile)

    # Move the discard pile back into the draw pile and shuffle
    def recycle_discard(self) -> None:
        self.draw_pile.extend(self.discard_pile)
        self.discard_pile.clear()
        self.shuffle()

    # Removes card from draw pile or discard pile. No way to retrieve
    def delete(self, card: Card) -> None:
        if card in self.draw_pile:
            self.draw_pile.remove(card)
        elif card in self.discard_pile:
            self.discard_pile.remove(card)

    # Put card on top of the draw pile, where the next draw will take it
    def put_on_top(self, card: Card) -> None:
        self.draw_pile.append(card)

    # Put card on the bottom of the draw pile
    def put_on_bottom(self, card: Card) -> None:
        self.draw_pile.insert(0, card)

    # Insert card at a specific index in the draw pile (0 = bottom)
    def insert_card(self, card: Card, position: int) -> None:
        self.draw_pile.insert(position, card)

    # Find card by name in draw or discard pile
    def find(self, card_name: str) -> Card | None:
        # TODO: Verify order for this, as it's important for some villains
        return self.search_deck(card_name) or self.search_discard(card_name)

    # Find card by name in discard pile
    def search_discard(self, card_name: str) -> Card | None:
        for card in self.discard_pile:
            if card.name == card_name:
                return card
        return None

    def search_deck(self, card_name: str) -> Card | None:
        for card in self.draw_pile:
            if card.name == card_name:
                return card
        return None

    def get_all_cards(self) -> list[Card]:
        return self.draw_pile + self.discard_pile
