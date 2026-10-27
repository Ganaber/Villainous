from typing import Any

from engine.actions.action import Action
from engine.board import Board
from engine.cards.card import Card
from engine.deck import Deck
from engine.location import Location
from villain import Villain
from villain_extras import VillainExtras

import engine.cards.common as card_functions


import engine.actions.common as actions
from engine.villains.prince_john import const
from engine import constants as g_const
from engine.cards import trigger_type as trigger

class PrinceJohn(Villain):
    def __init__(self, extras: dict[VillainExtras, Any]) -> None:
        super().__init__(g_const.WTIA_PRINCE_JOHN, extras)


    def win_condition(self) -> bool:
        # Implement Prince John's specific win condition
        pass


    def get_villain_deck(self) -> Deck:
        card_list = list[Card]()

        # 3 of these cards
        beautiful_lovely_taxes = Card(const.BEAUTIFUL_LOVELY_TAXES, 0, const.BEAUTIFUL_LOVELY_TAXES_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, g_const.EFFECT, g_const.VILLAIN, 
                                     card_functions.prince_john_can_pay_cost, {trigger.ON_PLAY: } )
        imprison = Card(const.IMPRISON, 2, const.IMPRISON_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        rhino_guards = Card(const.RHINO_GUARDS, 3, const.RHINO_GUARDS_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        warrant = Card(const.WARRANT, 1, const.WARRANT_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        wolf_archers = Card(const.WOLF_ARCHERS, 2, const.WOLF_ARCHERS_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})

        # 2 of these cards
        bow_and_arrows = Card(const.BOW_AND_ARROWS, 1, const.BOW_AND_ARROWS_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        cowardice = Card(const.COWARDICE, 0, const.COWARDICE_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        greed = Card(const.GREED, 0, const.GREED_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        set_a_trap = Card(const.SET_A_TRAP, 1, const.SET_A_TRAP_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})

        # 1 of these cards
        golden_arrow = Card(const.GOLDEN_ARROW, 0, const.GOLDEN_ARROW_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        intimidation = Card(const.INTIMIDATION, 2, const.INTIMIDATION_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        king_richards_crown = Card(const.KING_RICHARDS_CROWN, 1, const.KING_RICHARDS_CROWN_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        nutsy = Card(const.NUTSY, 2, const.NUTSY_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        sheriff_of_nottingham = Card(const.SHERIFF_OF_NOTTINGHAM, 3, const.SHERIFF_OF_NOTTINGHAM_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        sir_hiss = Card(const.SIR_HISS, 2, const.SIR_HISS_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})
        trigger = Card(const.TRIGGER, 2, const.TRIGGER_FRONT_IMAGE_PATH, const.VILLAIN_CARD_BACK_IMAGE_PATH, effects={})

        # adding cards to card_list
        for _ in range(3):
            card_list.append(beautiful_lovely_taxes)
            card_list.append(imprison)
            card_list.append(rhino_guards)
            card_list.append(warrant)
            card_list.append(wolf_archers)

        for _ in range(2):
            card_list.append(bow_and_arrows)
            card_list.append(cowardice)
            card_list.append(greed)
            card_list.append(set_a_trap)

        card_list.append(golden_arrow)
        card_list.append(intimidation)
        card_list.append(king_richards_crown)
        card_list.append(nutsy)
        card_list.append(sheriff_of_nottingham)
        card_list.append(sir_hiss)
        card_list.append(trigger)

        return Deck(card_list)

    def get_fate_deck(self) -> Deck:
        card_list = list[Card]()

        # 3 of these cards
        clever_disguise = Card(const.CLEVER_DISGUISE, 0, const.CLEVER_DISGUISE_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        steal_from_the_rich = Card(const.STEAL_FROM_THE_RICH, 0, const.STEAL_FROM_THE_RICH_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})

        # 1 of these cards
        alan_a_dale = Card(const.ALAN_A_DALE, 0, const.ALAN_A_DALE_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        friar_tuck = Card(const.FRIAR_TUCK, 0, const.FRIAR_TUCK_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        king_richard = Card(const.KING_RICHARD, 0, const.KING_RICHARD_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        lady_kluck = Card(const.LADY_KLUCK, 0, const.LADY_KLUCK_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        little_john = Card(const.LITTLE_JOHN, 0, const.LITTLE_JOHN_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        maid_marian = Card(const.MAID_MARIAN, 0, const.MAID_MARIAN_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        robin_hood = Card(const.ROBIN_HOOD, 0, const.ROBIN_HOOD_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        skippy = Card(const.SKIPPY, 0, const.SKIPPY_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})
        toby = Card(const.TOBY, 0, const.TOBY_FRONT_IMAGE_PATH, const.FATE_CARD_BACK_IMAGE_PATH, effects={})

        # adding cards to card_list
        for _ in range(3):
            card_list.append(clever_disguise)
            card_list.append(steal_from_the_rich)

        card_list.append(alan_a_dale)
        card_list.append(friar_tuck)
        card_list.append(king_richard)
        card_list.append(lady_kluck)
        card_list.append(little_john)
        card_list.append(maid_marian)
        card_list.append(robin_hood)
        card_list.append(skippy)
        card_list.append(toby)

        return Deck(card_list)

    def get_board(self) -> Board:
        sherwood_forest = Location(const.SHERWOOD_FOREST, 
            Action[Action(actions.gain_power(1)), actions.discard_cards()],
            Action[Action(actions.play_card), Action(actions.fate)]
        )
        friar_tucks_church = Location(const.FRIAR_TUCKS_CHURCH, 
            Action[Action(actions.gain_power(2)), actions.play_card()],
            Action[Action(actions.play_card), Action(actions.move_ally_or_item())]
        )
        nottingham = Location(const.NOTTINGHAM, 
            Action[Action(actions.fate()), actions.gain_power(1)],
            Action[Action(actions.vanquish()), Action(actions.play_card())]
        )
        the_jail = Location(const.THE_JAIL,
            [],
            Action[Action(actions.gain_power(3), Action(actions.play_card()), Action(actions.discard()))]
        )

        board = Board([sherwood_forest, friar_tucks_church, nottingham, the_jail])# TODO: add paths
        return board