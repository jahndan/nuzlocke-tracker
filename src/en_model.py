import numpy
from en_data import *
from common import *


def process_dialog(state: TrackerState, dialog: list[str]):
    """
    Handling the following side-effects (setting the state accordingly):
    - Checks for battle start/exit (singles/doubles, wild/trainer)
    - Checks if the player is using the PC (accessing boxes)
    - TODO power point (PP) tracking of opponent movesets
    - TODO etc.
    Note: state will be mutated when appropriate
    """
    # dbg("DIALOG", " ".join(dialog))

    # currently using pc boxes
    if state.view_type == ViewType.PC_BOX:
        match dialog:
            # check for exit
            case ["Which", "PC", "should", "be", "accessed"]:
                dbg("PATTERN", f"Which PC should be accessed")
                state.view_type = ViewType.OVERWORLD

    # currently in overworld
    if state.view_type == ViewType.OVERWORLD:
        match dialog:
            # check for pc boxes
            case ["The", "Pokemon", "Storage", "System", "was", "accessed"]:
                dbg("PATTERN", f"The Pokemon Storage System was accessed")
                state.view_type = ViewType.PC_BOX

            # check for trainer battle start
            case ["You", "are", "challenged", "by", *rest]:
                # the "and" *should* always show up in the same frame--at least
                # for vanilla trainer classes/names--even if the second trainer
                # class/name doesn't
                # -- worst comes to worst, we can add a check to reassign singles
                # to doubles if no species is detected (via misalignment)
                dbg("PATTERN", f"You are challenged by {" ".join(rest)}")
                # we do not strictly need to update foes_left here because it is
                # less critical to knowing when the battle ends unlike for wild
                # battles -- also partly because we don't have a way to get it yet
                if "and" in rest or "&" in "".join(rest):
                    state.view_type = ViewType.TRAINER_DOUBLE
                else:
                    state.view_type = ViewType.TRAINER_SINGLE

            # check for wild battle start
            case ["A", "wild", *rest, "appeared"]:
                dbg("PATTERN", f"A wild {" ".join(rest)} appeared")
                if "and" in rest:
                    state.foes_left = 2
                    state.view_type = ViewType.WILD_DOUBLE
                else:
                    state.foes_left = 1
                    state.view_type = ViewType.WILD_SINGLE

            # other?
            case _:
                pass

    # currently in wild battle
    if (
        state.view_type == ViewType.WILD_SINGLE
        or state.view_type == ViewType.WILD_DOUBLE
    ):
        match dialog:

            # fight exit
            case ["The", "wild", *rest, "fainted"]:
                dbg("PATTERN", f"The wild {" ".join(rest)} fainted")
                state.foes_left += -1
                if state.foes_left == 0:
                    state.view_type = ViewType.OVERWORLD

            # flight exit
            case ["The", "wild", *rest, "fled"]:
                dbg("PATTERN", f"The wild {" ".join(rest)} fled")
                state.foes_left += -1
                if state.foes_left == 0:
                    state.view_type = ViewType.OVERWORLD

            # run exit
            case ["Got", "away", "safely"]:
                dbg("PATTERN", "Got away safely")
                state.foes_left = 0
                state.view_type = ViewType.OVERWORLD

            # bag exit
            case ["Gotcha", *rest, "was", "caught"]:
                dbg("PATTERN", f"Gotcha! {" ".join(rest)}was caught!")
                state.foes_left = 0
                state.view_type = ViewType.OVERWORLD

            # TODO other edge cases
            # teleport?
            # run away?
            case _:
                pass

    # currently in trainer battle
    if (
        state.view_type == ViewType.TRAINER_SINGLE  # currently assumed this is true
        or state.view_type == ViewType.TRAINER_DOUBLE  # TODO properly handle
    ):
        # check for battle exit
        if "defeated" in dialog or "beat" in dialog:
            dbg("PATTERN", " ".join(dialog))
            state.view_type = ViewType.OVERWORLD
        pass

    # other checks?
    pass


def process_frame(state: TrackerState, frame: numpy.ndarray):
    """
    The main function that drives the English tracker model -- should be called on every frame captured
    Note: state will be mutated when appropriate
    """
    # main dialog box
    main_dialog = parse_text(frame[152:184, 16:232, :], dialog_chardata)
    process_dialog(state, main_dialog)
    # dbg("DIALOG", " ".join(main_dialog))

    if state.view_type == ViewType.OVERWORLD:
        ## locations

        locat = " ".join(parse_text_row(frame[16:32, 8:120], locations_chardata, True))
        if locat in valids.locations:
            state.location = locat
        # dbg("LOCATION", locat)

    # process others
    pass
