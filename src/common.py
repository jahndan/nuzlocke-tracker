from itertools import chain
from collections import deque
import cv2 as opencv
import numpy
from numpy import ndarray  # to keep annotations shorter
from enum import Enum
from dataclasses import dataclass, field  # dataclasses are effectively structs
from font import charset


### MODEL-AGNOSTIC TEXT PARSING


def parse_text(region: ndarray, chardat: charset):
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
    stacks = [region[ROW_HEIGHT * i : ROW_HEIGHT * (i + 1)] for i in range(rows)]
    results = [parse_text_row(haystack, chardat) for haystack in stacks]
    return list(chain(*results))


def parse_text_row(haystack: ndarray, chardat: charset):
    """
    Processes a single row of text -- process_text() calls this function under the hood
    see `process_text()` for parameters
    """
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
    matches = numpy.where(maxima > 0.95, indices, UNASSIGNED)

    # block out overlapping matches
    for (x,), i in numpy.ndenumerate(matches):
        # x is a horizontal position for char_matches
        # i is an index in char_data that (x,) corresponds to
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        char_width = char_sizes[i]
        # block out the full region, but leave the original pixel
        matches[x + 1 : x + char_width] = OCCUPIED

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


### MODEL TYPES


class BattleType(Enum):
    NONE = -1
    """not in battle"""
    TRAINER_SINGLE = 0
    """singles trainer battle"""
    WILD_SINGLE = 1
    """singles wild encounter"""
    TRAINER_DOUBLE = 2
    """doubles trainer battle"""
    WILD_DOUBLE = 3
    """doubles wild encounter (only in specific locations)"""


# typedef vomit
loc_t = str
spec_t = str
enc_t = tuple[
    dict[spec_t, int],  # per-location mapping from species to encounter frequency
    spec_t | None,  # per-location canon encounter (if caught)
]
member_t = tuple[loc_t, spec_t]


# actions are scuffed (functional-style enums would make this much simpler)
@dataclass
class ToParty:
    """change status for some member to party (either new or from boxed)"""

    member: member_t
    """who is being placed in party"""
    is_new: bool  # should never be true when party is full
    """true if new, false if moved --> true should also set the canon encounter"""

    # straightforward recovery (move back to boxed/unmark catch)


@dataclass
class ToBoxed:
    """change status for some member to boxed (either new or from party)"""

    member: member_t
    """who is being placed in box"""
    is_new: bool  # should always be true when party is full
    """true if new, false if moved --> true should also set the canon encounter"""

    # straightforward recovery (move back to party/unmark catch)


@dataclass
class PartyToDead:
    """change status for some member to dead (from party)"""

    member: member_t
    """who is being placed in cemetery"""
    # never is_new: only moved from party (see FailCanonEnc to fail an encounter)

    # straightforward recovery (move back to party)


@dataclass
class FailCanonEnc:
    """mark the current/most recent encounter as canon without catch"""

    member: member_t
    """what/where was the failed encounter"""

    # straightforward recovery (unset canon encounter)
    # that said, this shouldn't be queued up if a previous canon encounter has been
    # set in the current location -- when handling inputs/automarking, this should
    # be verified before processing this action


# TODO outline/add infrastructure for handling gift pokemon/other free encounters


# this one should only be necessary for tokens, which may not be relevant to all users
# thus we probably don't have to deal with updating canon listings
@dataclass
class EditEnc:
    """replace the species associated with a specific encounter"""

    old_member: member_t
    new_member: member_t

    # straightforward recovery (replace new with old)


action_t = ToParty | ToBoxed | PartyToDead | FailCanonEnc | EditEnc


@dataclass
class TrackerState:
    """global tracker state maintained by model -- treat as readonly outside en_model"""

    # TODO serialize/deserialize tracker state to save progress between sessions

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
    """undo action stack -- append/pop from right only"""

    redo_history: deque[action_t] = field(default_factory=deque, repr=False)
    """redo action stack -- cleared on new action"""


### EXTRA STUFF


def dbg(category, item, override=False):
    if override or item.__str__() != "":
        print(f"{category}:  {item}")


reset = "\033[0m"
bold = "\033[1m"
italic = "\033[3m"


class FilenameNotFoundError(Exception):
    """An exception class for when "" is found but not expected in the filename list"""


class CharacterDataNotFoundError(Exception):
    """An exception class for when None is found but not expected in the filename list"""
