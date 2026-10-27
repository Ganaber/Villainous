from __future__ import annotations

from typing import TYPE_CHECKING

from engine.cards.card import Card
from engine.effects.effect import Effect

if TYPE_CHECKING:
    from engine.game_state import GameState
    from engine.location import Location
    from engine.player import Player
    from engine.resource import Resource
    from engine.token import Token


def _get_player(player_username: str, game_state: "GameState") -> Player:
    player = game_state.get_player_by_username(player_username)
    if player is None:
        raise ValueError(f"Player {player_username!r} was not found")
    return player


def _get_location(player: Player, location: Location) -> Location:
    return player.board.get_location(location.name)


def _move_card(
    player: Player,
    card: Card,
    new_location: Location,
    adjacent: bool,
    game_state: "GameState",
) -> None:
    if adjacent:
        # TODO: Needs Human Review: Board currently has no path/adjacency data.
        raise NotImplementedError("Adjacent movement requires board path data")

    destination = _get_location(player, new_location)
    source_cards: list[Card | Token] | None = None
    destination_cards: list[Card | Token] | None = None

    for location in player.board.locations:
        if card in location.top_cards:
            source_cards = location.top_cards
            destination_cards = destination.top_cards
            if location is destination:
                raise ValueError(f"{card.name} is already at {destination.name}")
            break
        if card in location.bottom_cards:
            source_cards = location.bottom_cards
            destination_cards = destination.bottom_cards
            if location is destination:
                raise ValueError(f"{card.name} is already at {destination.name}")
            break

    if source_cards is None or destination_cards is None:
        raise ValueError(f"{card.name} was not found on {player.username}'s board")

    source_cards.remove(card)
    destination_cards.append(card)
    card.on_move(game_state)


# ===== Base Effects. Used as building blocks for other effects =====
def add_card_to_discard_pile(player_username: str, card: Card) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        player.villain_deck.discard([card])

    return Effect(
        name="Add card to discard pile",
        description=f"Added {card.name} to discard pile.",
        function=do_effect,
    )


def add_card_to_location(player_username: str, card: Card, location: Location, top: bool) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        player.add_card_to_location(card, _get_location(player, location), top)

    return Effect(
        name="Add card to location",
        description=f"Added {card.name} to {location.name}.",
        function=do_effect,
    )


def remove_card_from_location(player_username: str, card: Card, location: Location, top: bool) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        resolved_location = _get_location(player, location)
        cards = resolved_location.top_cards if top else resolved_location.bottom_cards
        if card not in cards:
            raise ValueError(f"{card.name} was not at {resolved_location.name}")
        player.remove_card_from_location(card, resolved_location, top)

    return Effect(
        name="Remove card from location",
        description=f"Removed {card.name} from {location.name}.",
        function=do_effect,
    )


def change_resource_amount(resource: Resource, amount: int) -> Effect:
    action = "Gain" if amount >= 0 else "Lose"
    actual_amount = abs(amount)

    def do_effect(game_state: "GameState") -> None:
        if amount >= 0:
            resource.gain_resource(actual_amount)
        else:
            resource.spend_resource(actual_amount)

    return Effect(
        name=f"{action} {resource.name}",
        description=f"{action} {actual_amount} {resource.name}.",
        function=do_effect,
    )


def remove_card_from_hand(player_username: str, card: Card) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        if not player.remove_card_from_hand(card):
            raise ValueError(f"{card.name} was not in {player_username}'s hand")

    return Effect(
        name="Remove card from hand",
        description=f"Removed {card.name} from {player_username}'s hand.",
        function=do_effect,
    )


# ===== Board Effects =====
def gain_power(player_username: str, amount: int) -> Effect:
    action = "Gain" if amount >= 0 else "Lose"
    actual_amount = abs(amount)

    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        if amount >= 0:
            player.gain_power(actual_amount)
        else:
            player.spend_power(actual_amount)

    return Effect(
        name=f"{action} Power",
        description=f"{action} {actual_amount} Power for {player_username}.",
        function=do_effect,
    )


def play_card(player_username: str, card: Card, location: Location, top: bool) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        if card not in player.hand:
            raise ValueError(f"{card.name} was not in {player_username}'s hand")
        if not card.can_play(game_state):
            raise ValueError(f"{card.name} cannot be played")
        if player.power.amount < card.cost:
            raise ValueError(f"{player_username} cannot afford {card.name}")

        resolved_location = _get_location(player, location)
        player.remove_card_from_hand(card)
        player.spend_power(card.cost)
        player.add_card_to_location(card, resolved_location, top)
        card.on_play(game_state)

    return Effect(
        name="Play a card",
        description=f"Play {card.name} at {location.name}.",
        function=do_effect,
    )


def activate(activated_effect: Effect | Card) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        if isinstance(activated_effect, Card):
            activated_effect.on_activate(game_state)
        else:
            activated_effect.execute(game_state)

    return Effect(
        name="Activate",
        description=f"Activate {activated_effect.name}.",
        function=do_effect,
    )


def fate(fated_player: Player) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(fated_player.username, game_state)
        player.fate_on_this() # TODO: Write this function

    return Effect(
        name="Fate",
        description=f"Fate {fated_player.username} as {fated_player.villain.name}.",
        function=do_effect,
    )


def move_ally_or_item(
    player_username: str,
    moved_card: Card,
    new_location: Location,
    adjacent: bool,
) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        _move_card(player, moved_card, new_location, adjacent, game_state)

    return Effect(
        name="Move ally or item",
        description=f"Move {moved_card.name} to {new_location.name}.",
        function=do_effect,
    )


def move_hero(
    player_username: str,
    moved_card: Card,
    new_location: Location,
    adjacent: bool,
) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        _move_card(player, moved_card, new_location, adjacent, game_state)

    return Effect(
        name="Move hero",
        description=f"Move {moved_card.name} to {new_location.name}.",
        function=do_effect,
    )


def vanquish(player_username: str, defeated_hero: Card, used_allies: list[Card]) -> Effect:
    allies_used = ", ".join(ally.name for ally in used_allies) if used_allies else "nothing"

    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        # TODO: Write this function

    return Effect(
        name="Vanquish",
        description=f"Vanquish {defeated_hero.name} with {allies_used}.",
        function=do_effect,
    )


def discard_cards(player_username: str, cards: list[Card]) -> Effect:
    def do_effect(game_state: "GameState") -> None:
        player = _get_player(player_username, game_state)
        remaining_hand = player.hand.copy()
        for card in cards:
            if card not in remaining_hand:
                raise ValueError(f"One or more cards were not in {player_username}'s hand")
            remaining_hand.remove(card)
        discarded = player.discard_cards(cards)
        if len(discarded) != len(cards):
            raise ValueError(f"One or more cards were not in {player_username}'s hand")

    return Effect(
        name=f"Discard {len(cards)} Cards",
        description=f"Discard {len(cards)} Cards.",
        function=do_effect,
    )
