from typing import Optional

from engine.board import Board
from engine.cards.card import Card
from engine.constants import HAND_SIZE
from engine.deck import Deck
from engine.resource import Resource
from engine.villain import Villain

# A seat in the game: which villain is being played, plus all of that realm's live state.
class Player:

    def __init__(self, username: str, villain: Villain, villain_deck: Deck, fate_deck: Deck, board: Board) -> None:
        self.username: str = username
        self.villain: Villain = villain
        self.villain_deck: Deck = villain_deck
        self.fate_deck: Deck = fate_deck
        self.board: Board = board
        self.power: Resource = Resource(0, "Power")
        self.hand: list[Card] = []
        self.mover_location: int = -1  # starts off the board (portrait)

    # Shuffle both decks, take starting power, draw opening hand. Call once at start of game
    def setup(self, starting_power: int = 0) -> None:
        self.villain_deck.shuffle()
        self.fate_deck.shuffle()
        self.power: Resource = Resource(starting_power, "Power")
        self.hand: list[Card] = []
        self.refill_hand()

    def gain_power(self, amount: int) -> int:
        return self.power.gain_resource(amount)

    def spend_power(self, amount: int) -> int:
        return self.power.spend_resource(amount)

    def draw_cards(self, amount: int = 1) -> list[Card]:
        drawn_cards = self.villain_deck.draw(amount)
        self.hand.extend(drawn_cards)
        return drawn_cards

    # Top the hand back up to HAND_SIZE, at the end of a turn
    def refill_hand(self) -> list[Card]:
        missing = HAND_SIZE - len(self.hand)
        if missing <= 0:
            return []
        return self.draw_cards(missing)

    def discard_card(self, card: Card) -> bool:
        if card not in self.hand:
            return False

        self.hand.remove(card)
        self.villain_deck.discard([card])
        return True

    def discard_cards(self, cards: list[Card]) -> list[Card]:
        discarded_cards = []
        for card in cards:
            if self.discard_card(card):
                discarded_cards.append(card)
        return discarded_cards

    # The mover may go to any location except the one it's already on
    def move_mover(self, new_location: int) -> bool:
        # TODO: Account for Maleficent's and Syndrome's stay at current location
        if not 0 <= new_location < len(self.board.locations):
            return False
        if new_location == self.mover_location:
            return False
        self.mover_location = new_location
        return True
