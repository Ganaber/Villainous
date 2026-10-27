from typing import TYPE_CHECKING

from engine.actions.action import Action
from engine.cards.card import Card
import engine.effects.common as effects
from engine.location import Location
from engine.player import Player

if TYPE_CHECKING:
    from engine.game_state import GameState

# ===== Common actions on boards =====

def gain_power(amount: int) -> Action:
    return Action(
        name=f"Gain {amount} Power",
        effect=effects.common.create_gain_power_effect(amount),
    )

def play_card(card: Card) -> Action:
    return Action(
        name=f"Play {card.name}",
        effect=effects.common.create_play_card_effect(card),
    )

def activate(activated_effect: effects.Effect) -> Action:
    return Action(
        name=f"Activate {activated_effect.name}",
        effect=effects.common.create_activate_effect(activated_effect),
    )

def fate(fated_player: "Player") -> Action:
    return Action(
        name=f"Fate {fated_player.name}",
        effect=effects.common.create_fate_effect(fated_player),
    )

def move_ally_or_item(moved_card: Card, new_location: "Location") -> Action:
    return Action(
        name=f"Move {moved_card.name} to {new_location.name}",
        effect=effects.common.create_move_ally_or_item_effect(moved_card, new_location),
    )

def move_hero(moved_card: Card, new_location: "Location") -> Action:
    return Action(
        name=f"Move Hero to {new_location.name}",
        effect=effects.common.create_move_hero_effect(moved_card, new_location),
    )

def vanquish(vanquished_card: Card) -> Action:
    return Action(
        name=f"Vanquish {vanquished_card.name}",
        effect=effects.common.create_vanquish_effect(vanquished_card),
    )

# ===== End of common actions on boards =====