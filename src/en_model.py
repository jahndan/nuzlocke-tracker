import numpy
import cv2 as opencv
from en_fontmap import normal_fontmap, bold_fontmap
from font import palette_transfer, charset


# TODO also ideally parallelize what can be parallelized for more speed

# minimal sets of chars that can be useful in general
lower_alpha = set("abcdefghijklmnopqrstuvwxyz")
upper_alpha = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alphabet = lower_alpha | upper_alpha
numbers = set("0123456789")
# TODO do we even need to identify punctuation?
# punctuation = set("$!?,.•/‘’“”„«»()♂♀+-*#=&~:;")
# note: ellipsis … may not be used in english version of game

locations_palette = [
    numpy.array([0xFF, 0xFF, 0xFF], dtype=numpy.uint8),
    numpy.array([0xA3, 0x92, 0x92], dtype=numpy.uint8),
    numpy.array([0x01, 0x01, 0x01], dtype=numpy.uint8),
    numpy.array([0x00, 0x00, 0x00], dtype=numpy.uint8),
]
locations: charset = palette_transfer(
    alphabet | numbers | set(".’-"),
    normal_fontmap,
    locations_palette,
)

# species = alphabet | set("-2")  # this is definitely missing stuff
# # potentially something that uses bold_fontmap (like level, gender)
# # etc ...


def process_text(region: numpy.ndarray, chardat: charset, threshold: float = 0.95):
    """Takes a cropped region of an image and parses it for text that matches the characters passed to it.

    `region` : a portion of a 3-channel image, whose height should be a multiple of 16\n
    `charset` : an iterable associating characters with their image/mask data\n
    `threshold` (optional) : a minimum correlation for it to match when parsed\n"""
    ROW_HEIGHT = 16
    # negative indices don't show up naturally
    UNASSIGNED = -1
    OCCUPIED = -2

    # set up rows and haystack if necessary
    rows, leftover_region = divmod(region.shape[0], ROW_HEIGHT)
    assert leftover_region == 0  # full rows of text (should be aligned)
    assert region.ndim == 3  # 3-channel image
    haystack = (
        region
        if rows <= 1
        else numpy.concatenate(
            # preserve inner row structures, but place them horizontally next to each other
            [region[ROW_HEIGHT * i : ROW_HEIGHT * (i + 1)] for i in range(rows)],
            axis=1,
        )
    )

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


def process(frame: numpy.ndarray):
    """The main function that drives the English tracker model -- should be called on every frame captured"""
    # locations
    loc_data = process_text(frame[16:32, 8:123, :], locations)
    # there should be various side effects based on the output of process_text
    print(loc_data)

    # process others
    pass
