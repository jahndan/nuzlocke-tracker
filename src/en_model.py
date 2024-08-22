import numpy
from en_data import *
from common import *


def dialog_parse(state: TrackerState, dialog: list[str]):
    pass


def process(state: TrackerState, frame: numpy.ndarray):
    """
    The main function that drives the English tracker model -- should be called on every frame captured
    """
    # main dialog box
    main_dialog = parse_text(
        frame[152:184, 16:232, :],
        locations_charset,  # update instead of reusing location chars
    )
    # dbg("DIALOG", " ".join(main_dialog))
    # there should be various side effects based on the output of process_text
    dialog_parse(state, main_dialog)

    # locations (only applicable in overworld)
    if state.battle_type == BattleType.NONE:
        # minor optimization to call process_text_row() when the input is known to be a single row
        location_data = parse_text_row(frame[16:32, 8:120, :], locations_charset)
        # update current location in state
        locat = " ".join(location_data)
        if locat in valids.locations:
            state.location = locat
        # dbg("LOCATION", locat)

    # process others
    pass
