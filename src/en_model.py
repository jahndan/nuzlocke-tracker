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
            case ["The", "Pokémon", "Storage", "System", "was", "accessed"]:
                dbg("PATTERN", f"The Pokemon Storage System was accessed")
                state.view_type = ViewType.PC_BOX

            # check for trainer battle start
            case ["You", "are", "challenged", "by", *rest]:
                dbg("PATTERN", f"You are challenged by {" ".join(rest)}")
                # if needed, we can add a check to reassign singles to
                # doubles if no species is detected (via misalignment)
                if "and" in rest or "&" in "".join(rest):
                    state.view_type = ViewType.TRAINER_DOUBLE
                else:
                    state.view_type = ViewType.TRAINER_SINGLE
                # we do not strictly need to update foes_left here because it is
                # less critical to knowing when the battle ends unlike for wild
                # battles -- also partly because we don't have a way to get it yet

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
            state.location = locat  # update location
            # clearing this ensures that no encounter can be marked with wrong location
            state.species = "", ""
        # dbg("LOCATION", locat)

        ## other
        pass

    if (
        state.view_type == ViewType.WILD_SINGLE
        or state.view_type == ViewType.TRAINER_SINGLE
    ):
        ## species (singles alignment)

        # we consider the left member of tuple to be the singles position
        left = " ".join(parse_text_row(frame[24:40, 2:62], species_chardata))
        match left:
            case "":
                pass  # shouldn't be changed during animations
            case spec if spec in valids.species:
                state.species = spec, ""  # clear right for singles
        # dbg("SPECIES", left)

        ## other
        pass

    if (
        state.view_type == ViewType.WILD_DOUBLE
        or state.view_type == ViewType.TRAINER_DOUBLE
    ):
        ## species (doubles alignment)

        left, right = (
            " ".join(parse_text_row(frame[33:49, 2:62], species_chardata)),
            " ".join(parse_text_row(frame[4:20, 8:68], species_chardata)),
        )
        match left, right:
            case "", "":
                pass  # shouldn't be changed during animations
            case (
                l,  # only one of these can be "" at a time because
                r,  # we hold on to the last species seen in-battle
            ) if (l in valids.species or l == "") and (r in valids.species or r == ""):
                state.species = l, r
        # dbg("SPECIES", state.species)

        ## other
        pass

    # process others
    pass


def handle_event(state: TrackerState, event: str):
    """
    Handles user input events and mutates state accordingly
    Note: state will be mutated if the input is valid in-context
    """
    action = decorate_event(state, event)
    dbg("ACTION", action)
    # actually handle them in-model
    pass


def decorate_event(state: TrackerState, event: str):
    """
    Decorates user input events with state-based context
    Note: state is readonly in this context (no mutation)
    """
    match (event, state.view_type):

        # catching a member right now (singles)
        case ("ToParty", ViewType.WILD_SINGLE) if state.foes_left == 1:  # redundant if
            spec = state.species[0]
            if spec != "":
                return ToParty((state.location, spec), True)
        case ("ToBoxed", ViewType.WILD_SINGLE) if state.foes_left == 1:  # redundant if
            spec = state.species[0]
            if spec != "":
                return ToBoxed((state.location, spec), True)

        # not catching a member--mark canon (singles)
        case "FailEnc", ViewType.WILD_SINGLE if state.foes_left == 1:  # redundant if
            spec = state.species[0]
            if spec != "":
                return FailCanonEnc((state.location, spec))

        # catching a member right now (doubles)
        case ("ToParty", ViewType.WILD_DOUBLE) if state.foes_left == 1:
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return ToParty((state.location, spec), True)
        case ("ToBoxed", ViewType.WILD_DOUBLE) if state.foes_left == 1:
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return ToBoxed((state.location, spec), True)

        # not catching a member--mark canon (doubles)
        case "FailEnc", ViewType.WILD_DOUBLE if state.foes_left == 1:
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return FailCanonEnc((state.location, spec))

        # just caught a member in the last battle
        case ("ToParty", ViewType.OVERWORLD):
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return ToParty((state.location, spec), True)
        case ("ToBoxed", ViewType.OVERWORLD):
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return ToBoxed((state.location, spec), True)

        # not catching a member--mark canon (last battle)
        case ("FailEnc", ViewType.OVERWORLD):
            left, right = state.species
            spec = left if left != "" else right
            if spec != "":
                return FailCanonEnc((state.location, spec))

        # moving members around between party/box
        case ("ToParty", ViewType.PC_BOX):
            pass  # not ready for handling yet
        case ("ToBoxed", ViewType.PC_BOX):
            pass  # not ready for handling yet

        # member just died (in-battle)
        case ("ToDead", _):
            pass  # not ready for handling yet

        # replace an encounter info (trade/token)
        case ("EditEnc", ViewType.PC_BOX):
            pass  # not ready for handling yet
