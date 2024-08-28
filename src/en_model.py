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
                    state.encounters_updated = False

            # flight exit
            case ["The", "wild", *rest, "fled"]:
                dbg("PATTERN", f"The wild {" ".join(rest)} fled")
                state.foes_left += -1
                if state.foes_left == 0:
                    state.view_type = ViewType.OVERWORLD
                    state.encounters_updated = False

            # run exit
            case ["Got", "away", "safely"]:
                dbg("PATTERN", "Got away safely")
                state.foes_left = 0
                state.view_type = ViewType.OVERWORLD
                state.encounters_updated = False

            # bag exit
            case ["Gotcha", *rest, "was", "caught"]:
                dbg("PATTERN", f"Gotcha! {" ".join(rest)}was caught!")
                state.foes_left = 0
                state.view_type = ViewType.OVERWORLD
                state.encounters_updated = False

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
            state.encounters_updated = False
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

        # autotracking of encounter data
        if not state.encounters_updated and state.view_type == ViewType.WILD_SINGLE:
            spec = state.species[0]
            if state.encounters.get(state.location) is None:
                state.encounters[state.location] = dict(), None
            freqs = (state.encounters[state.location])[0]
            freqs[spec] = freqs[spec] + 1 if spec in freqs else 1
            state.encounters_updated = True

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

        # autotracking of encounter data
        if not state.encounters_updated and state.view_type == ViewType.WILD_DOUBLE:
            for spec in state.species:
                if state.encounters.get(state.location) is None:
                    state.encounters[state.location] = dict(), None
                freqs = (state.encounters[state.location])[0]
                freqs[spec] = freqs[spec] + 1 if spec in freqs else 1
            state.encounters_updated = True

        ## other
        pass

    # process others
    pass


def handle_event(state: TrackerState, event: str):
    """
    Handles user input events and mutates state accordingly
    Note: state will be mutated if the input is valid in-context
    """
    match event:
        case "UndoAction":
            if state.undo_history:
                action = state.undo_history.pop()
                dbg("UNDO", action)
                undo_action(state, action)
        case "RedoAction":
            if state.redo_history:
                action = state.redo_history.pop()
                dbg("REDO", action)
                redo_action(state, action)
        case _:
            action = decorate_event(state, event)
            dbg("ACTION", action)
            do_action(state, action)


def do_action(state: TrackerState, action: action_t):
    """perform an action -- clearing the redo stack"""
    # never accept a double append
    if not state.undo_history or action != state.undo_history[-1]:
        redo_action(state, action)  # where we actually perform the action
    # clear the redo stack (new action wipes redoable history)
    state.redo_history.clear()


def redo_action(state: TrackerState, action: action_t):
    """perform an action -- without clearing the redo stack"""
    match action:
        # moving around members
        case PartyToDead((location, species)):
            # TODO handle
            pass
        case ToParty((location, species), False):
            # TODO handle
            pass
        case ToBoxed((location, species), False):
            # TODO handle
            pass
        # encounters
        case ToParty((location, species), True):
            # mark canon if applicable (maybe we should err if canon was already set)
            _mark_canon_enc(state, location, species)
            # add the member to party
            state.party.add((location, species))
        case ToBoxed((location, species), True):
            # mark canon if applicable (maybe we should err if canon was already set)
            _mark_canon_enc(state, location, species)
            # add the member to boxed
            state.boxed.add((location, species))
        case FailCanonEnc((location, species)):
            # mark canon if applicable (less important if canon is already set)
            _mark_canon_enc(state, location, species)
        case EditEnc((old_location, old_species), (new_location, new_species)):
            # TODO handle
            pass
        case _:  # non-actions
            return  # do not affect the undo/redo stacks for non-actions
    # push the action to undo stack
    state.undo_history.append(action)


def undo_action(state: TrackerState, action: action_t):
    match action:
        # moving around members
        case PartyToDead((location, species)):
            # TODO handle
            pass
        case ToParty((location, species), False):
            # TODO handle
            pass
        case ToBoxed((location, species), False):
            # TODO handle
            pass
        # encounters
        case ToParty((location, species), True):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
            # not using discard because it shouldn't be possible to error
            state.party.remove((location, species))
        case ToBoxed((location, species), True):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
            # not using discard because it shouldn't be possible to error
            state.boxed.remove((location, species))
        case FailCanonEnc((location, species)):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
        case EditEnc((old_location, old_species), (new_location, new_species)):
            # TODO handle
            pass
        case _:  # non-actions
            return  # do not affect the undo/redo stacks for non-actions
    # push the action to redo stack
    state.redo_history.append(action)


def _mark_canon_enc(state: TrackerState, location: loc_t, species: spec_t) -> bool:
    """
    helper function to mark an encounter as canon
    -- does nothing if one is already set for that location
    -- returns success: bool
    """
    # get existing encounter table entry or create a new one
    enc_data = state.encounters.get(location)
    # enc_data probably isn't None, but safety check anyway
    freqs, canon_enc = enc_data if enc_data is not None else (dict(), None)
    # only set canon if it is not already set
    if canon_enc is None:
        canon_enc = species
    else:
        dbg(
            "WARN",
            "attempted to mark a canon encounter:"
            + f"{species} in {location}, but {canon_enc}"
            + "is already marked there.",
        )
        return False
    # reassign the encounter table entry
    state.encounters[location] = freqs, canon_enc
    return True


def _unmark_canon_enc(state: TrackerState, location: loc_t, species: spec_t):
    """
    helper function to unmark an encounter as canon
    -- only unsets it if the species match
    """
    # get existing encounter table entry or create a new one
    enc_data = state.encounters.get(location)
    # enc_data cannot be None at this point, but safety check anyway
    freqs, canon_enc = enc_data if enc_data is not None else (dict(), None)
    # only unset canon if species match
    if canon_enc is not None and canon_enc == species:
        canon_enc = None
    # reassign the encounter table entry
    state.encounters[location] = freqs, canon_enc
