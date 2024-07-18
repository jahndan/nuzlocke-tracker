import numpy
import cv2 as opencv
from main import imload
from en_fontmap import normal_fontmap, bold_fontmap
from bidict import bidict
from typing import Iterable, Callable
from font import substitute_colors, sort_key as font_sortkey


def image(x: Iterable, f: Callable):
    """utility function for taking the mathematical image of a set under a function/mapping"""
    return {y: f(y) for y in x}


"""
def normal_map(char):
    tmp = imload("sprites/" + normal_fontmap.get(char) + ".png")
    return tmp[:, :, :3], tmp[:, :, 3]  # split bgra into image + mask


def bold_map(char):
    tmp = imload("sprites/" + bold_fontmap.get(char) + ".png")
    return tmp[:, :, :3], tmp[:, :, 3]  # split bgra into image + mask
"""


# maybe make our own class for charsets and fontmaps? (they'd basically just be wrappers)
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
locations: list[tuple] = palette_transfer(
    alphabet | numbers | set(".’-"), normal_fontmap, locations_palette
)
# species = alphabet | set("-2")  # this is definitely missing stuff
# # potentially something that uses bold_fontmap (like level, gender)
# # etc ...


### TODO debugging prints + removing them once done


def stall():
    # return
    while True:  # debug: wait for input
        if (opencv.waitKey(1) & 0xFF) == ord("q"):
            break


# chardict probably actually needs a class: list of tuples of (sortkey, char, img, mask)
def process_locations(haystack: numpy.ndarray, chardict: list[tuple], threshold=0.95):
    print("----------")
    # negative indices don't show up naturally
    UNASSIGNED = -1
    OCCUPIED = -2

    # get cropped area dims for convenience
    fr_height, fr_width = haystack.shape[:-1]

    print("haystack shape:", haystack.shape)
    opencv.imshow(
        "haystack",
        opencv.resize(haystack, None, fx=4, fy=4, interpolation=opencv.INTER_NEAREST),
    )
    print()
    stall()
    print()
    debug_minima, debug_maxima = [], []
    # iterate over characters in locations, associate them with match scores
    chars, char_sizes, char_scores = [], [], []
    for _, char, needle, mask in chardict:
        chars.append(char)  # character being matched
        char_sizes.append(needle.shape[:-1])  # height, width of character
        # print("haystack", haystack.shape, haystack.dtype)
        # print("needle", needle.shape, needle.dtype)
        # print(needle)
        # print("mask", mask.shape, mask.dtype)
        # print(mask)
        score = opencv.matchTemplate(
            haystack, needle, opencv.TM_CCOEFF_NORMED, None, mask
        )
        char_scores.append(
            # fixing the size to be consistent
            numpy.pad(
                score,
                ((0, needle.shape[0] - 1), (0, needle.shape[1] - 1)),
                mode="constant",
                constant_values=-1,  # pad with lowest possible score for TM_CCOEFF_NORMED
            ).flat
            # TODO double check if this flatten then unflatten business is unnecessary
        )
        print("char:", char, needle.shape[:-1])
        debug_minima.append(numpy.nanmin(score))
        debug_maxima.append(numpy.nanmax(score))
        print("score extrema:", numpy.nanmin(score), numpy.nanmax(score))
        print("nan found:", numpy.isnan(score).any())
        print("posinf found:", numpy.isposinf(score).any())
        print("neginf found:", numpy.isneginf(score).any())
        print("score:", score)
        opencv.imshow(
            "needle",
            opencv.resize(needle, None, fx=4, fy=4, interpolation=opencv.INTER_NEAREST),
        )
        opencv.imshow(
            "mask",
            opencv.resize(mask, None, fx=4, fy=4, interpolation=opencv.INTER_NEAREST),
        )
        opencv.imshow(
            "score",
            opencv.resize(
                numpy.pad(score, ((0, needle.shape[0] - 1), (0, needle.shape[1] - 1))),
                None,
                fx=4,
                fy=4,
                interpolation=opencv.INTER_NEAREST,
            ),
        )
        print()
        stall()
    print()
    print("extrema:", min(debug_minima), max(debug_maxima))
    print("chars:", chars)
    char_scores = numpy.array(char_scores)
    # get indices & maxima along char axis (with thresholding to ignore nonmatches)
    maxima, indices = char_scores.max(axis=0), char_scores.argmax(axis=0)
    print("maxima:", maxima.reshape(16, fr_width))
    print("indices:", indices.reshape(16, fr_width))
    print()
    stall()
    print()
    char_matches = numpy.where(
        maxima > threshold, indices, numpy.full_like(indices, UNASSIGNED)
    ).reshape(
        fr_height, fr_width
    )  # unflatten back to 2d
    print("initial matches:", char_matches)
    opencv.imshow(
        "initial matches",
        opencv.resize(
            (char_matches) * (1.0 / len(chars)),
            None,
            fx=4,
            fy=4,
            interpolation=opencv.INTER_NEAREST,
        ),
    )
    print()
    stall()
    # block out overlapping matches
    for (y, x), i in numpy.ndenumerate(char_matches):
        # y, x are indices in char_matches, i is an index in char_data that (y,x) corresponds to
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        c_height, c_width = char_sizes[i]
        # block out the full region, but set the upper left corner back to what it was
        char_matches[y : (y + c_height), x : (x + c_width)] = OCCUPIED
        char_matches[y, x] = i
    opencv.imshow(
        "matches",
        opencv.resize(
            (char_matches + 2) * (1.0 / len(chars)),
            None,
            fx=4,
            fy=4,
            interpolation=opencv.INTER_NEAREST,
        ),
    )
    print("blocked matches:", char_matches)
    print()
    stall()
    print()
    # stringify from matches
    # TODO support multi-line blocks of text (this correctly stringifies one-liners only)
    words = []
    current = ""
    column_empty = numpy.where(
        # empty iff everything is UNASSIGNED
        numpy.logical_and(
            # axis 0 is the vertical
            char_matches.max(axis=0) == UNASSIGNED,
            char_matches.min(axis=0) == UNASSIGNED,
        ),
        True,
        False,
    )
    print("column_empty:", column_empty)
    print()
    stall()
    # iterate over axes in opposite order to avoid alignment issues (TODO: standardize char height? to iterate y,x instead?)
    for (x, y), i in numpy.ndenumerate(char_matches.swapaxes(0, 1)):
        if column_empty[x] == True and current != "":
            words.append(current)
            current = ""
        if i < 0:  # if i == UNASSIGNED or i == OCCUPIED:
            continue
        current = current + chars[i]
    print("----------")
    return words


def process(frame: numpy.ndarray):
    # locations
    print(process_locations(frame[15:31, 8:123, :], locations))
    # process others

    # notes: haystack is the slice to search for text in (should be properly
    # vertically aligned, with its height a multiple of 16), and rows should
    # dictate how many 16px rows of text there are
    # process_text(haystack, rows) -> numpy.block([ haystack[2*i:2*(i+1)] for i in range(rows) ])
    pass
