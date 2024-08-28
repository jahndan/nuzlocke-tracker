from itertools import chain
from collections import deque
import cv2 as opencv
import numpy
from numpy import ndarray  # to keep annotations shorter
from enum import Enum
from dataclasses import dataclass, field  # dataclasses are effectively structs
from font import char_dataset


### MODEL-AGNOSTIC TEXT PARSING


def parse_text(region: ndarray, chardata: char_dataset, masked: bool = False):
    """
    Takes a cropped region of an image and parses it for text that matches the characters passed to it.

    `region` : a portion of a 3-channel image, whose height should be a multiple of 16\n
    `chardata` : an iterable associating characters with their image/mask data\n
    `threshold` (optional) : a minimum correlation for it to match when parsed\n
    """
    ROW_HEIGHT = 16
    # set up rows and haystacks
    rows, leftover_region = divmod(region.shape[0], ROW_HEIGHT)
    assert leftover_region == 0  # full rows of text (should be aligned)
    assert region.ndim == 3  # 3-channel image
    # split by row (was supposed to be parallelized)
    stacks = [region[ROW_HEIGHT * i : ROW_HEIGHT * (i + 1)] for i in range(rows)]
    results = [parse_text_row(haystack, chardata, masked) for haystack in stacks]
    return list(chain(*results))


def parse_text_row(haystack: ndarray, chardata: char_dataset, masked: bool = False):
    """
    Processes a single row of text -- parse_text() calls this function under the hood
    see `parse_text()` for parameters -- mildly faster than parse_text() for single-row
    """
    # negative indices don't show up naturally
    UNASSIGNED = -1
    OCCUPIED = -2

    chars, char_sizes, char_scores = [], [], []
    # iterate over characters, associate them with match scores
    for _, char, needle, mask in chardata:
        chars.append(char)  # character being matched
        char_sizes.append(needle.shape[1])  # width of character (height is fixed)
        score = opencv.matchTemplate(
            haystack, needle, opencv.TM_CCOEFF_NORMED, None, mask if masked else None
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


class ViewType(Enum):
    """
    different types of views in the game (with corresponding regions to search for text)
    """

    PC_BOX = -2
    """managing members in the box"""
    OVERWORLD = -1
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
"""(frequencies: dict[spec_t, int], canon: spec_t | None)"""
member_t = tuple[loc_t, spec_t]
"""(location: loc_t, species: spec_t)"""


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


@dataclass(repr=True)
class TrackerState:
    """global tracker state maintained by model -- treat as readonly outside en_model"""
    # Note: The .__repr__() generated for this is solely for debugging -- and as such, we
    # may or may not include various fields from that representation at our convenience.
    # In short, expect the .__repr__() or .__str__() methods to have unstable behavior.

    # TODO serialize/deserialize tracker state to save progress between sessions

    ### stuff that will not be stored when saving state on exit

    view_type: ViewType = field(default=ViewType.OVERWORLD, repr=True)
    """current view type (see documentation for the type)"""

    foes_left: int = field(default=0, repr=True)
    """how many pokemon are left in the battle -- should always be 0 in overworld"""

    species: tuple[spec_t, spec_t] = field(default=("", ""), repr=True)
    """opposing species last seen in battle -- holds last-seen value until location changes"""

    encounters_updated: bool = field(default=False, repr=False)
    """purely for housekeeping -- update encounters to track wild encounters once"""

    ### stuff that will be stored when saving state on exit

    location: loc_t = field(default="???", repr=True)
    """current location -- this should be initialized with a default value corresponding to the language"""
    # shouldn't be strictly necessary to save, but only assuming users start the tracker before opening the game

    encounters: dict[loc_t, enc_t] = field(default_factory=dict, repr=True)
    """table of encounter data thus far -- stores canon encounter & frequencies"""
    # dict maintains insertion order as of Python 3.7, which is convenient for us because
    # we will only insert dict entries when a species is first encountered in that area
    # which makes it clear to the user which encounter was caught (or supposed to be)

    party: set[member_t] = field(default_factory=set, repr=True)
    """members currently in party -- should be constrained to 6 members"""

    boxed: set[member_t] = field(default_factory=set, repr=True)
    """members currently in box -- only include living members"""

    dead: set[member_t] = field(default_factory=set, repr=True)
    """members currently in cemetery -- members should only arrive from party"""

    undo_history: deque[action_t] = field(default_factory=deque, repr=True)
    """stack of actions that can be undone -- append/pop from right only"""

    redo_history: deque[action_t] = field(default_factory=deque, repr=True)
    """stack of actions that can be redone -- cleared on new action"""


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


### EXTRA STUFF


reset = "\033[0m"
bold = "\033[1m"
italic = "\033[3m"


def dbg(category, item, override=False):
    if override or (item is not None and item.__str__() != ""):
        print(f"{bold}{category}: {reset} {item}")


class FilenameNotFoundError(Exception):
    """An exception class for when "" is found but not expected in the filename list"""


class CharacterDataNotFoundError(Exception):
    """An exception class for when None is found but not expected in the filename list"""
