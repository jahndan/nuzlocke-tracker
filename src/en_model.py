import numpy
import cv2 as opencv
from main import imload
from en_fontmap import normal_fontmap, bold_fontmap
from bidict import bidict
from typing import Iterable, Callable
from font import substitute_colors, sort_key as font_sortkey

# TODO also ideally parallelize what can be parallelized for more speed

# TODO clarify terminology
# in palette transfer, charset is a literal set of single character strings
# elsewhere, charset is what palette transfer returns: ordered list associating chars with img data


# maybe make our own classes for charsets and fontmaps? (they'd basically just be wrappers)
def palette_transfer(charset: Iterable, fontmap: bidict, palette: list[numpy.ndarray]):
    lst = []
    for char in charset:
        raw = imload("sprites/" + fontmap.get(char) + ".png")
        lst.append(
            (
                font_sortkey(raw),  # sorting key
                char,  # the character itself
                substitute_colors(raw, palette),  # palette mapped image
                numpy.where(raw > 0, numpy.uint8(255), numpy.uint8(0)),  # mask
            )
        )
    # it may be overkill, but the sort makes errors in recognition less likely
    return sorted(lst, reverse=True)


# minimal sets of chars that can be useful in general
lower_alpha = set("abcdefghijklmnopqrstuvwxyz")
upper_alpha = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
alphabet = lower_alpha | upper_alpha
numbers = set("0123456789")
# do we ever need to identify punctuation?
# punctuation = set("$!?,.•/‘’“”„«»()♂♀+-*#=&~:;")
# ellipsis … may not be used in english version of game

# char dicts for each part of the logic (é/e doesn't distinguish anything)
# locations = sorted(
#     image(alphabet | numbers | set(".’-"), normal_map),
#     key=sort_key
# )
locations_palette = [
    numpy.array([0xFF, 0xFF, 0xFF], dtype=numpy.uint8),
    numpy.array([0xA3, 0x92, 0x92], dtype=numpy.uint8),
    numpy.array([0x01, 0x01, 0x01], dtype=numpy.uint8),
    numpy.array([0x00, 0x00, 0x00], dtype=numpy.uint8),
]
locations = palette_transfer(
    alphabet | numbers | set(".’-"),
    normal_fontmap,
    locations_palette,
)
# species = alphabet | set("-2")  # this is definitely missing stuff
# # potentially something that uses bold_fontmap (like level, gender)
# # etc ...
# TODO charset class??


def stall():
    # return
    while True:  # debug: wait for input
        if (opencv.waitKey(1) & 0xFF) == ord("q"):
            break


def process_text(region: numpy.ndarray, charset, threshold: float = 0.95):
    # the gen 4 font is standardized at 16px height
    ROW_HEIGHT = 16
    # negative indices don't show up naturally
    UNASSIGNED = -1
    OCCUPIED = -2

    ## TODO test that this works correctly with multi-line pieces of text
    # set up rows and haystack if necessary
    rows, leftover_region = divmod(region.shape[0], ROW_HEIGHT)
    assert leftover_region == 0  # full rows of text (should be aligned)
    haystack = (
        region
        if rows <= 1
        else numpy.block(
            # preserve inner row structures, but place them horizontally next to each other
            [region[ROW_HEIGHT * i : ROW_HEIGHT * (i + 1)] for i in range(rows)]
            ## TODO this may need to be nested inside another list so it concats horizontally
        )
    )

    chars, char_sizes, char_scores = [], [], []
    # iterate over characters in charset, associate them with match scores
    for _, char, needle, mask in charset:
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
    # get indices of strongest char match in each position (maxima for threshold comparison)
    maxima, indices = char_scores.max(axis=0), char_scores.argmax(axis=0)

    char_matches = numpy.where(
        maxima > threshold, indices, numpy.full_like(indices, UNASSIGNED)
    )

    # block out overlapping matches
    for (x,), i in numpy.ndenumerate(char_matches):
        # x is a horizontal position for char_matches
        # i is an index in char_data that (y,x) corresponds to
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        c_width = char_sizes[i]
        # block out the full region, but leave the original pixel
        char_matches[x + 1 : x + c_width] = OCCUPIED
        # char_matches[x] = i

    # stringify from matches
    words = []
    current_word = ""
    for (x,), i in numpy.ndenumerate(char_matches):
        if i == UNASSIGNED and current_word != "":
            words.append(current_word)
            current_word = ""
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        current_word = current_word + chars[i]
    return words


def process(frame: numpy.ndarray):
    # locations
    loc_data = process_text(frame[15:31, 8:123, :], locations)
    # there should be various side effects based on the output of process_text
    print(loc_data)

    # process others
    pass
