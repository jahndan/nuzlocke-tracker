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
                dbg("PATTERN", f"The Pokémon Storage System was accessed")
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

    # currently in nickname screen (or waiting on manual entry)
    if state.view_type == ViewType.NICKNAME:
        match dialog:
            case [*rest, "was", "transferred", "to", "BOX", _, "in", _, "PC"]:
                dbg("PATTERN", f"{" ".join(rest)} was transferred to BOX ? in <?>'s PC")
                if (
                    " ".join(rest) == state.last_species[0]
                    or " ".join(rest) == state.last_species[1]
                ):
                    state.last_nickname = None
                else:
                    state.last_nickname = " ".join(rest)

                # autotrack: send to box
                left, right = state.last_species
                species = left if left != "" else right
                action = ToBoxed((state.location, species, state.last_nickname), True)
                do_action(state, action)

                # resolve
                state.view_type = ViewType.OVERWORLD
                state.adding_encounter = False

            # TODO warn the user that the tracker can get trapped here
            # and make sure to show that on the tracker display window
            # -- adding to party requires manual user input

            # opened POKéMON menu -- should open a summary screen and manually mark
            case ["Choose", "a", "Pokémon"]:
                state.view_type = ViewType.PARTY_MENU

    if state.view_type == ViewType.PARTY_MENU and state.adding_encounter:
        match dialog:
            case ["Do", "what", "with", *rest]:
                # tentative guess (whatever the last selected pkmn was)
                if (
                    " ".join(rest) == state.last_species[0]
                    or " ".join(rest) == state.last_species[1]
                ):
                    state.last_nickname = None
                else:
                    state.last_nickname = " ".join(rest)

                # manual tracking
                state.view_type = ViewType.SUMMARY_PARTY
                # wait for user input (unset adding_encounter in handling)

                # # auto-tracking (assumed to be the first one)
                # # perform corresponding action here
                # state.view_type = ViewType.OVERWORLD
                # state.adding_encounter = False

    # currently in pkmn summary screen
    if state.view_type == ViewType.SUMMARY_PARTY:
        match dialog:
            # exiting summary screen
            case ["Choose", "a", "Pokémon"]:
                if state.adding_encounter:
                    state.view_type = ViewType.NICKNAME
                else:
                    state.view_type = ViewType.OVERWORLD

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
                    state.encounters_updated = False
                    state.view_type = ViewType.OVERWORLD
                # autotrack fail? -- configurable for user:
                # probably want to keep it on unless you expect
                # to use species clause a lot

            # flight exit
            case ["The", "wild", *rest, "fled"]:
                dbg("PATTERN", f"The wild {" ".join(rest)} fled")
                state.foes_left += -1
                if state.foes_left == 0:
                    state.encounters_updated = False
                    state.view_type = ViewType.OVERWORLD
                # autotrack fail? -- configurable for user:
                # probably want to keep it on unless you expect
                # to use species clause a lot

            # run exit
            case ["Got", "away", "safely"]:
                dbg("PATTERN", "Got away safely")
                state.foes_left = 0
                state.encounters_updated = False
                state.view_type = ViewType.OVERWORLD
                # autotrack fail? -- configurable for user:
                # probably want to keep it on unless you expect
                # to use species clause a lot

            # bag exit
            case ["Gotcha", *rest, "was", "caught"]:
                dbg("PATTERN", f"Gotcha! {" ".join(rest)} was caught!")
                state.foes_left = 0
                state.encounters_updated = False
                # TODO check state.view_type = ViewType.OVERWORLD
                state.view_type = ViewType.NICKNAME
                state.adding_encounter = True

            # TODO other edge cases
            # teleport?
            # run away?
            case _:
                pass

    # currently in trainer battle
    if (
        state.view_type == ViewType.TRAINER_SINGLE
        or state.view_type == ViewType.TRAINER_DOUBLE
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
    dialog_box = (
        frame[152:184, 16:120, :]  # adjusted width for
        if state.view_type == ViewType.PARTY_MENU
        else frame[152:184, 16:232, :]
    )
    main_dialog = parse_text(dialog_box, dialog_chardata)
    process_dialog(state, main_dialog)
    # dbg("DIALOG", " ".join(main_dialog))

    if state.view_type == ViewType.OVERWORLD:
        ## locations

        locat = " ".join(parse_text_row(frame[16:32, 8:120], locations_chardata, True))
        if locat in valids.locations:
            state.location = locat  # update location
            # clearing this ensures that no encounter can be marked with wrong location
            state.last_species = "", ""
            state.last_nickname = ""
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
                state.last_species = spec, ""  # clear right for singles
        # dbg("SPECIES", left)

        # TODO species tracking both sides for display reasons

        # autotracking of encounter data
        if not state.encounters_updated and state.view_type == ViewType.WILD_SINGLE:
            spec = state.last_species[0]
            if state.encounters.get(state.location) is None:
                state.encounters[state.location] = EncounterRegistry(dict(), None)
            freqs = state.encounters[state.location].frequencies
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
                state.last_species = l, r
        # dbg("SPECIES", state.last_species)

        # TODO species tracking both sides for display reasons

        # autotracking of encounter data
        if not state.encounters_updated and state.view_type == ViewType.WILD_DOUBLE:
            for spec in state.last_species:
                if state.encounters.get(state.location) is None:
                    state.encounters[state.location] = EncounterRegistry(dict(), None)
                freqs = state.encounters[state.location].frequencies
                freqs[spec] = freqs[spec] + 1 if spec in freqs else 1
            state.encounters_updated = True

        ## other
        pass

    # process others
    pass


## INPUT EVENT HANDLING


def handle_event(state: TrackerState, event: str):
    """
    Handles user input events and mutates state accordingly.
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
        # events that need to be decorated by context
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
        case PartyToDead(member):
            dbg("UNHANDLED", "not implemented yet")
            # TODO handle
            pass
        case ToParty(member, False):
            dbg("UNHANDLED", "not implemented yet")
            # TODO handle
            pass
        case ToBoxed(member, False):
            dbg("UNHANDLED", "not implemented yet")
            # TODO handle
            pass
        # encounters
        case ToParty((location, species, nickname), True):
            # mark canon if applicable (maybe we should err if canon was already set)
            _mark_canon_enc(state, location, species)
            # add the member to party
            state.party.add((location, species, nickname))
            # resolve the current status
            state.adding_encounter = False
        case ToBoxed((location, species, nickname), True):
            ## should be unreachable

            # mark canon if applicable (maybe we should err if canon was already set)
            _mark_canon_enc(state, location, species)
            # add the member to boxed
            state.boxed.add((location, species, nickname))
        case FailCanonEnc((location, species, _)):
            # mark canon if applicable (less important if canon is already set)
            _mark_canon_enc(state, location, species)
        # case EditEnc((old_location, old_species, old_nickname), (new_location, new_species, new_nickname)):
        case EditEnc(old_member, new_member):
            dbg("UNHANDLED", "not implemented yet")
            # TODO handle
            pass
        case _:  # non-actions
            # we probably shouldn't reach this
            # do not affect the undo/redo stacks
            return
    # push the action to undo stack
    state.undo_history.append(action)


def undo_action(state: TrackerState, action: action_t):
    match action:
        # moving around members
        case PartyToDead(member):
            # TODO handle
            pass
        case ToParty(member, False):
            # TODO handle
            pass
        case ToBoxed(member, False):
            # TODO handle
            pass
        # encounters
        case ToParty((location, species, nickname), True):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
            # not using discard because it shouldn't be possible to error
            state.party.remove((location, species, nickname))
        case ToBoxed((location, species, nickname), True):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
            # not using discard because it shouldn't be possible to error
            state.boxed.remove((location, species, nickname))
        case FailCanonEnc((location, species, _)):
            # unmark canon if applicable
            _unmark_canon_enc(state, location, species)
        case EditEnc(old_member, new_member):
            # case EditEnc((old_location, old_species, old_nickname), (new_location, new_species, new_nickname)):
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
    if enc_data is None:
        freqs, canon_enc = (dict(), None)
    else:
        freqs, canon_enc = (enc_data.frequencies, enc_data.canon)

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
    state.encounters[location] = EncounterRegistry(freqs, canon_enc)
    return True


def _unmark_canon_enc(state: TrackerState, location: loc_t, species: spec_t):
    """
    helper function to unmark an encounter as canon
    -- only unsets it if the species match
    """
    # get existing encounter table entry or create a new one
    enc_data = state.encounters.get(location)
    # enc_data cannot be None at this point, but safety check anyway
    if enc_data is None:
        freqs, canon_enc = (dict(), None)
    else:
        freqs, canon_enc = (enc_data.frequencies, enc_data.canon)
    # only unset canon if species match
    if canon_enc is not None and canon_enc == species:
        canon_enc = None
    # reassign the encounter table entry
    state.encounters[location] = EncounterRegistry(freqs, canon_enc)


### CANVAS MANAGEMENT


def draw_to_display(state: TrackerState, canvas: ndarray):
    """
    en_model's image representation of state -- mutates canvas but not state
    """
    # Location info
    location_cv = canvas[4:20, 4:-4]
    _draw_str(location_cv, state.location)

    # Battle + species info
    battle_cv = canvas[22:54, 4:-4]
    match state.view_type:
        case ViewType.OVERWORLD | ViewType.PC_BOX:
            _draw_str(battle_cv, "Not in battle")
        case ViewType.WILD_SINGLE:
            _draw_str(battle_cv[:16], "Wild battle (singles)")
            _draw_str(battle_cv[16:], _pad(state.last_species[0]))
        case ViewType.TRAINER_SINGLE:
            _draw_str(battle_cv[:16], "Trainer battle (singles)")
            _draw_str(battle_cv[16:], _pad(state.last_species[0]))
        case ViewType.WILD_DOUBLE:
            _draw_str(battle_cv[:16], "Wild battle (doubles)")
            _draw_str(
                battle_cv[16:],
                f"{_pad(state.last_species[0])}, {_pad(state.last_species[1])}",
            )
        case ViewType.TRAINER_DOUBLE:
            _draw_str(battle_cv[:16], "Trainer battle (doubles)")
            _draw_str(
                battle_cv[16:],
                f"{_pad(state.last_species[0])}, {_pad(state.last_species[1])}",
            )


def _draw_str(slice: ndarray, input: str):
    """
    Helper for draw_to_display()
    -- clears the slice of the canvas passed in
    -- uses the charset provided to draw the input string on the canvas (upper left)
    -- pass in a slice of the canvas to position the text (mutating the canvas)
    """
    slice[:, :, :] = display_palette[0]  # clear this slice of the canvas
    char_images = {char: img for _, char, img, _ in display_chardata}
    char_images[" "] = numpy.full((16, 5, 3), display_palette[0], dtype=numpy.uint8)
    for line in input.split("\n"):
        try:
            line_images = [char_images[char] for char in line]
        except:
            chars = list(zip(*display_chardata))[1]
            chars.append(" ")
            dbg("ERROR", f"'{line}' contains characters not found in display_chardata")
            print(
                "Consider adding the missing characters:",
                set(line) - set(chars),
                "to the charset.",
            )
            raise  # if this happens, it should be fixed immediately
        else:
            x = 0
            for img in line_images:
                w = img.shape[1]
                slice[:16, x : x + w] = img
                x += w


def _pad(s: str):
    if s == "":
        return "(none)"
    return s
