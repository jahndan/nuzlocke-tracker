import numpy
from en_data import *
from common import *


def process_dialog(state: TrackerState, dialog: list[str]):
    pass


def process_frame(state: TrackerState, frame: numpy.ndarray):
    """
    The main function that drives the English tracker model -- should be called on every frame captured
    """
    # main dialog box
    main_dialog = parse_text(
        frame[152:184, 16:232, :],
        locations_chardata,  # update instead of reusing location chars
    )
    # dbg("DIALOG", " ".join(main_dialog))
    # there should be various side effects based on the output of process_text
    process_dialog(state, main_dialog)

    # locations (only applicable in overworld)
    if state.view_type == ViewType.OVERWORLD:
        # minor optimization to call process_text_row() when the input is known to be a single row
        location_data = parse_text_row(frame[16:32, 8:120, :], locations_chardata, True)
        # update current location in state
        locat = " ".join(location_data)
        if locat in valids.locations:
            state.location = locat
        # dbg("LOCATION", locat)

    # process others
    pass
