from PIL import Image
import numpy
import cv2 as opencv
from bidict import bidict
if __name__ == "__main__":  # script has no parent package
    from readfont_index import normal_namemap, bold_namemap
else:  # relative import from parent package when loaded as module
    from .readfont_index import normal_namemap, bold_namemap


"""
this is the base palette in src/font/*.font.png:
# 0 : green (not content)
# 1 : white (background)
# 2 : light grey (text color 1)
# 3 : dark grey (text color 2)
# 4 : black (text color 3, for bold only)

this is the base palette in sprites/*.png:
# 0 : alpha (background/not content)
# 1 : light grey (text color 1)
# 2 : dark grey (text color 2)
# 3 : black (text color 3, for bold only)

these palettes' index mapping shouldn't be messed with
(sortkey and dynamic recoloring will break if it changes)
"""


### functions used for loading font data into models (import these from font)


# note: PIL is used directly for loading indexed-color (palette) images instead of this
def imload(filepath):
    """load a specified image preserving channels -- raises FileNotFoundError if not found"""
    im = opencv.imread(filepath, opencv.IMREAD_UNCHANGED)
    if im is None:
        raise FileNotFoundError
    else:
        return im


def substitute_colors(image: numpy.ndarray, pal: list[numpy.ndarray]):
    """replace indexed image data (2d) with palette colors using palette"""
    mapped = numpy.stack((image, image, image), axis=2, dtype=numpy.uint8)
    # TODO this *should* be very parallelizable
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            mapped[i, j] = pal[image[i, j]]
    return mapped


def sort_key(content: numpy.ndarray):
    """sorting key function for determining which characters need to be recognized first"""
    # wider chars first because thinner chars are more likely to falsely match
    # darker chars first because they are less likely to falsely match on thinner chars
    # note: the correctness of this hinges on the palette indices staying organized as they are
    return (content.shape[1] << 10) + int(content.sum())


char_dataset = list[tuple[int, str, numpy.ndarray, numpy.ndarray]]
"""more specific type alias than `list` so it's clear what this is made
of--the first is a sort key, the second is a single character, the third
is 3-channel image data, the fourth is a 1-channel mask for said image"""


# note: the fontmap is specific to, and should be supplied by, whatever model is using this function
def palette_transfer(chars, fontmap, palette: list[numpy.ndarray]) -> char_dataset:
    """Associates requested characters with their image data from the fontmap and remaps palette indices to colors.

    `chars`: an iterable of characters for which the relevant data is requested
    `fontmap`: a mapping between characters and image data (typically normal or bold)
    `palette`: a indexed collection of colors (which themselves are 3-vectors)
    """
    lst = []
    for char in chars:
        raw = imload("sprites/" + fontmap.get(char) + ".png")
        lst.append(
            (
                sort_key(raw),  # sorting key
                char,  # the character itself
                substitute_colors(raw, palette),  # palette mapped image
                numpy.where(raw > 0, numpy.uint8(255), numpy.uint8(0)),  # mask
            )
        )
    # it may be overkill, but the sort makes errors in recognition less likely
    return sorted(lst, reverse=True)


### functions used for splitting a font file into character sprites

def fix_color(content: numpy.ndarray):
    """simply remaps the palette indices 0,1 -> 0 so a transparency mask can be constructed trivially"""
    # color 0 is non-content, color 1 is transparent background, but we don't need that distinction after cropping
    # note: the correctness of this hinges on the palette indices staying organized as they are
    return numpy.where(content > 0, (content - 1), 0)


def crop_content(content: numpy.ndarray, vert=True, horiz=True):
    """crops a 2d array to content, i.e. removes rows/columns that only contain palette color 0"""
    assert content.ndim == 2  # 2d arrays only
    upperbound, lowerbound = 0, content.shape[0]
    leftbound, rightbound = 0, content.shape[1]
    cropping = True
    while cropping:
        # if no edges were cropped out, we are done
        cropping = False
        # check if edge-slices are empty, and crop them out
        if vert and (content[upperbound, :] == 0).all():
            upperbound += 1
            cropping = True
        if vert and (content[lowerbound - 1, :] == 0).all():
            lowerbound -= 1
            cropping = True
        if horiz and (content[:, leftbound] == 0).all():
            leftbound += 1
            cropping = True
        if horiz and (content[:, rightbound - 1] == 0).all():
            rightbound -= 1
            cropping = True
        # if no content is found i.e. all data gets cropped out, return None
        if upperbound >= lowerbound or leftbound >= rightbound:
            return None
    return content[upperbound:lowerbound, leftbound:rightbound]


def process_font(fontfile_arr: numpy.ndarray, names: bidict[int, str]):
    """makes a map from name of character --> img data of character"""
    # partition the full array into 16x16 subarrays
    vsplits, hsplits = numpy.arange(16, 512, 16), numpy.arange(16, 256, 16)
    partition = [
        char  # flatten while partitioning
        for sub in numpy.split(fontfile_arr, vsplits, axis=0)
        for char in numpy.split(sub, hsplits, axis=1)
    ]
    # add horizontally cropped character data to dict if its index is mapped to a filename
    # (vertical cropping gives smaller files, but not cropping allows for easier alignment)
    chars = dict()
    for index, filename in names.items():
        img = crop_content(partition[index], vert=False, horiz=True)
        if img is not None:
            chars[filename] = fix_color(img)
        # errors later iff this char is requested and its img is None
    return chars


def export_files(chars: dict, exports=None):
    """takes the map of char names and image data, uses that to export as files"""
    if exports is None:
        exports = chars.keys()
    for filename in exports:
        try:
            opencv.imwrite(f"sprites/{filename}.png", chars.get(filename))
        except:
            print(
                f"'{filename}' requested, but not found in character data!",
                "Check if it exists in the readfont_index.py mappings",
            )


if __name__ == "__main__":
    filename = "src/font/normal.font.png"
    print(f"Processing: {filename}")
    img = Image.open(filename)
    # palette = process_palette(img, False)
    # imarr = substitute_colors(numpy.array(img), palette)
    chars = process_font(numpy.array(img), normal_namemap)
    export_files(chars, normal_namemap.values())
    print(f"Finished processing: {filename}")

    filename = "src/font/bold.font.png"
    print(f"Processing: {filename}")
    img = Image.open(filename)
    # palette = process_palette(img, True)
    # imarr = substitute_colors(numpy.array(img), palette)
    chars = process_font(numpy.array(img), bold_namemap)
    export_files(chars, bold_namemap.values())
    print(f"Finished processing: {filename}.")
