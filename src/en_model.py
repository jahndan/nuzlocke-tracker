from itertools import chain
import numpy
import cv2 as opencv
from en_fontmap import normal_fontmap, bold_fontmap
from font import palette_transfer, charset
from en_data import BattleType, valids, alphabet, lower_alpha, upper_alpha, numbers
from collections import deque

from en_model_types import *

# TODO serialize/deserialize tracker state to save progress between sessions


@dataclass
class TrackerState:
    """global tracker state maintained by model -- treat as zreadonly outside en_model"""

    ### stuff that doesn't need to be stored when saving

    # TODO actually determine battle type properly
    battle_type: BattleType = BattleType.NONE  # see BattleType enum for details
    """current battle type (NONE in overworld)"""

    # TODO handle double battles (later TODO support)
    # TODO validate with real values
    species: str = ""  # should be a member of valids.species
    """opposing species currently in battle"""

    location: loc_t = ""  # should be a member of valids.locations
    """current location"""

    ### stuff that needs to be stored on exit when saving state

    encounters: dict[loc_t, enc_t] = field(default_factory=dict, repr=False)
    """table of encounter data thus far -- stores canon encounter & frequencies"""
    # dict maintains insertion order as of Python 3.7, which is convenient for us because
    # we will only insert dict entries when a species is first encountered in that area
    # which makes it clear to the user which encounter was caught (or supposed to be)

    party: set[member_t] = field(default_factory=set, repr=False)
    """members currently in party -- should be constrained to 6 members"""

    boxed: set[member_t] = field(default_factory=set, repr=False)
    """members currently in box -- only include living members"""

    dead: set[member_t] = field(default_factory=set, repr=False)
    """members currently in cemetery -- members should only arrive from party"""

    undo_history: deque[action_t] = field(default_factory=deque, repr=False)
    """undo action stack - append/pop from right only"""

    redo_history: deque[action_t] = field(default_factory=deque, repr=False)
    """redo action stack -- cleared on new action"""


locations_palette = [
    numpy.array([0xFF, 0xFF, 0xFF], dtype=numpy.uint8),
    numpy.array([0xA3, 0x92, 0x92], dtype=numpy.uint8),
    numpy.array([0x01, 0x01, 0x01], dtype=numpy.uint8),
    numpy.array([0x00, 0x00, 0x00], dtype=numpy.uint8),
]
locations_charset: charset = palette_transfer(
    alphabet | numbers | set("’"),
    normal_fontmap,
    locations_palette,
)

# species_palette = [
#     numpy.array([0x?, 0x?, 0x?], dtype=numpy.uint8),
#     numpy.array([0x?, 0x?, 0x?], dtype=numpy.uint8),
#     numpy.array([0x?, 0x?, 0x?], dtype=numpy.uint8),
#     numpy.array([0x?, 0x?, 0x?], dtype=numpy.uint8),
# ]
# species: charset = palette_transfer(
#     alphabet | set("2♂♀’-"),
#     normal_fontmap,
#     species_palette,
# )

# something that uses bold_fontmap (like level, gender)
# etc ...


def process_text(region: numpy.ndarray, chardat: charset, threshold: float = 0.95):
    """
    Takes a cropped region of an image and parses it for text that matches the characters passed to it.

    `region` : a portion of a 3-channel image, whose height should be a multiple of 16\n
    `charset` : an iterable associating characters with their image/mask data\n
    `threshold` (optional) : a minimum correlation for it to match when parsed\n
    """
    ROW_HEIGHT = 16
    # set up rows and haystacks
    rows, leftover_region = divmod(region.shape[0], ROW_HEIGHT)
    assert leftover_region == 0  # full rows of text (should be aligned)
    assert region.ndim == 3  # 3-channel image
    # split by row (was supposed to be parallelized)
    haystacks = [region[ROW_HEIGHT * i : ROW_HEIGHT * (i + 1)] for i in range(rows)]
    results = [
        _process_text_row(haystack, chardat, threshold) for haystack in haystacks
    ]
    return list(chain(*results))


def _process_text_row(haystack: numpy.ndarray, chardat: charset, threshold: float):
    # negative indices don't show up naturally
    UNASSIGNED = -1
    OCCUPIED = -2

    chars, char_sizes, char_scores = [], [], []
    # iterate over characters in charset, associate them with match scores
    for _, char, needle, mask in chardat:
        chars.append(char)  # character being matched
        char_sizes.append(needle.shape[1])  # width of character (height is fixed)
        score = opencv.matchTemplate(
            haystack, needle, opencv.TM_CCOEFF_NORMED, None, mask
        ).flat  # vertical axis is unnecessary, row height is fixed
        char_scores.append(
            # fixing the size to be consistent (pad with lowest normed score)
            numpy.pad(score, (0, needle.shape[1] - 1), constant_values=-1)
        )
    char_scores = numpy.array(char_scores)

    # get indices of strongest char match in each position
    maxima, indices = char_scores.max(axis=0), char_scores.argmax(axis=0)
    # discount matches weaker than the threshold
    matches = numpy.where(maxima > threshold, indices, UNASSIGNED)

    # block out overlapping matches
    for (x,), i in numpy.ndenumerate(matches):
        # x is a horizontal position for char_matches
        # i is an index in char_data that (x,) corresponds to
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        char_width = char_sizes[i]
        # block out the full region, but leave the original pixel
        matches[x + 1 : x + char_width] = OCCUPIED
        # char_matches[x] = i

    # stringify from matches
    words = []
    current_word = ""
    for (x,), i in numpy.ndenumerate(matches):
        if i == UNASSIGNED and current_word != "":
            words.append(current_word)
            current_word = ""
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        current_word = current_word + chars[i]
    return words


def dialog_parse(state: TrackerState, dialog: list[str]):
    pass


def process(state: TrackerState, frame: numpy.ndarray):
    """The main function that drives the English tracker model -- should be called on every frame captured"""
    # main dialog box
    main_dialog = process_text(
        frame[152:184, 16:232, :],
        locations_charset,  # update instead of reusing location chars
    )
    # there should be various side effects based on the output of process_text
    dialog_parse(main_dialog)
    # print("DIALOG:", " ".join(main_dialog))  # debug

    # locations (only applicable in overworld)
    if state.battle_type == BattleType.NONE:
        loc_data = process_text(frame[16:32, 8:120, :], locations_charset)
        # there should be various side effects based on the output of process_text
        loc = " ".join(loc_data)
        if loc in valids.locations:
            state.location = loc
        # print("LOCATION:", loc)  # debug

    # process others
    pass
