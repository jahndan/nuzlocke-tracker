from PIL import Image
import numpy
import cv2 as opencv
from bidict import bidict
if __name__ == "__main__":  # script has no parent package
    from readfont_index import normal_namemap, bold_namemap
else:  # relative import from parent package when loaded as module
    from .readfont_index import normal_namemap, bold_namemap

## we may want to use del to remove unnecessary
## names and let python deallocate them

### this is the base palette in src/font/*.font.png:
# 0 : green (not content)
# 1 : white (background)
# 2 : light grey (text color 1)
# 3 : dark grey (text color 2)
# 4 : black (text color 3, for bold only)

### this is the base palette in sprites/*.png:
# 0 : alpha (background/not content)
# 1 : light grey (text color 1)
# 2 : dark grey (text color 2)
# 3 : black (text color 3, for bold only)

## note: sprites are now one channel, which will need updating where loaded
# mask can be constructed with numpy.where(img > 0, 255, 0)


## no longer necessary
# def process_palette(im: Image, bold: bool):
#     """reads, reformats, and modifies the built-in palette to be usable"""
#     raw = im.getpalette()  # flattened rgb triple array
#     # unflattening said array with bgr triples for sanity
#     pal = [
#         [raw[3 * i + 2], raw[3 * i + 1], raw[3 * i + 0]]  # packing triples in bgr order
#         for i in range(len(raw) // 3)
#     ]
#     # replace with bgra quadruples, i.e. add alpha channel
#     npal = [color + [0xFF] for color in pal]
#     # map green to the zero vector because it is not part of content
#     npal[4] = [0x00, 0x00, 0x00, 0x00]
#     # map white to zero alpha because it is part of content but transparent
#     npal[0] = [0xFF, 0xFF, 0xFF, 0x00]
#     # non-bold: map black to zero alpha like white (bold uses black for nontransparent color)
#     npal[3] = [0x0F, 0x0F, 0x0F, 0xFF] if bold else [0xFF, 0xFF, 0xFF, 0x00]
#     return npal


## not strictly required for this, but may want relocation for dynamically recoloring
# def substitute_colors(mat: numpy.ndarray, pal: list[list]):
#     """replace indexed image data with palette colors using nested list palette"""
#     assert len(mat.shape) == 2  # array passed in must be a 2d array of palette indices!
#     # substitute indices for palette colors
#     imlst = [[pal[idx] for idx in lst] for lst in mat.tolist()]
#     return numpy.array(imlst)


## shouldn't be needed anymore but might be useful in general?
# def match_color(pixel: numpy.ndarray, color: numpy.ndarray):
#     """4-channel color equality (args should either be a standalone color or 1d subarray)"""
#     assert pixel.shape == (4,)  # length 4, 1d arrays only
#     assert color.shape == (4,)  # length 4, 1d arrays only
#     for i in range(4):
#         if pixel[i] != color[i]:
#             return False
#     return True


## also unnecessary at this point
# def check_content(strip: numpy.ndarray):
#     """checks if all pixels in a 1d strip are palette color 0"""
#     assert len(strip.shape) == 1  # 1d strips only
#     for pixel in strip:
#         if pixel != 0:
#             return True
#     return False


def sortkey(content: numpy.ndarray):
    return (content.shape[1] << 10) + int(content.sum())


def fix_color(content: numpy.ndarray):
    return numpy.where(content > 0, (content - 1), 0)


def crop_content(content: numpy.ndarray, vert=True, horiz=True):
    """crops a 2d array to content, i.e. removes rows/columns that only contain palette color 0"""
    assert len(content.shape) == 2  # 2d arrays only
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


def process_font(arr: numpy.ndarray, names: bidict[int, str]):
    """makes a map from name of character --> img data of character"""
    # partition the full array into 16x16 subarrays
    vsplits, hsplits = numpy.arange(16, 512, 16), numpy.arange(16, 256, 16)
    partition = [
        char  # flatten while partitioning
        for sub in numpy.split(arr, vsplits, axis=0)
        for char in numpy.split(sub, hsplits, axis=1)
    ]
    # add character data to dict if its index is mapped to a filename
    chars = dict()
    for index, filename in names.items():
        img = crop_content(partition[index], vert=False, horiz=True)
        if img is not None:
            chars[filename] = fix_color(img)
        # errors later iff this char is requested and its img is None
    return chars


def export_files(chars: dict, exports=None):
    """takes the map of char names and image data, uses that to export as files"""
    if exports == None:
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
