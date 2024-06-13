from PIL import Image
import numpy
import cv2 as opencv
from bidict import bidict
from readfont_index import normal_fontmap, bold_fontmap


# reads, reformats, and modifies the built-in palette to be usable
def process_palette(im: Image, recolor=""):
    raw = im.getpalette()  # flattened rgb triple array
    # unflattening said array with bgr triples for sanity
    pal = [
        [raw[3 * i + 2], raw[3 * i + 1], raw[3 * i + 0]]  # packing triples in bgr order
        for i in range(len(raw) // 3)
    ]
    # replace with bgra quadruples, i.e. add alpha channel
    npal = pal.copy()
    [x.append(255) for x in npal]  # modifies npal through side effects
    # swapping colors as desired
    npal[4] = [0, 0, 0, 0]  # green --> zero vector
    npal[0] = [255, 255, 255, 0]  # white --> nonzero vector but still transparent
    npal[3] = [15, 15, 15, 0]  # black --> nonzero vector but still transparent
    return npal


# create bgra array of image data from palette indexed image data
def substitute_colors(mat: numpy.ndarray, pal: list[list]):
    assert len(mat.shape) == 2  # array passed in must be a 2d array of palette indices!
    # substitute indices for palette colors
    imlst = [[pal[idx] for idx in lst] for lst in mat.tolist()]
    return numpy.array(imlst)


# 4-channel color equality (args should either be a standalone color or 1d subarray)
def match_color(pixel: numpy.ndarray, color: numpy.ndarray):
    assert pixel.shape == (4,)
    assert color.shape == (4,)
    for i in range(4):
        if pixel[i] != color[i]:
            return False
    return True


# checks if all pixels in a 2d subarray match bgra(0, 0, 0, 0)
def check_content(strip: numpy.ndarray):
    assert len(strip.shape) == 2  # 2d subarrays only
    for pixel in strip:
        if not match_color(pixel, numpy.array([0, 0, 0, 0])):
            return True
    return False


# crops a 3d array to content, i.e. removes rows/columns that only contain bgra(0, 255, 0, 0)
def crop_content(content: numpy.ndarray, vert=True, horiz=True):
    assert len(content.shape) == 3  # 3d arrays only
    upperbound, lowerbound = 0, content.shape[0]
    leftbound, rightbound = 0, content.shape[1]
    cropping = True
    while cropping:
        cropping = False
        if not check_content(content[upperbound, :]):
            upperbound += 1
            cropping = True
        if not check_content(content[lowerbound - 1, :]):
            lowerbound -= 1
            cropping = True
        if not check_content(content[:, leftbound]):
            leftbound += 1
            cropping = True
        if not check_content(content[:, rightbound - 1]):
            rightbound -= 1
            cropping = True
        if upperbound >= lowerbound or leftbound >= rightbound:
            return None  # if no content is found i.e. all data gets cropped out, return None
    return content[upperbound:lowerbound, leftbound:rightbound]


# makes a map from name of character --> img data of character
def process_font(arr: numpy.ndarray, names: bidict[int, str]):
    # partition the full array into 16x16 subarrays
    vsplits, hsplits = numpy.arange(16, 512, 16), numpy.arange(16, 256, 16)
    partition = [
        char  # flatten while partitioning
        for sub in numpy.split(arr, vsplits, axis=0)
        for char in numpy.split(sub, hsplits, axis=1)
    ]
    # add character data to dict if its index is mapped to a filename
    # chars = {filename: crop_content(partition[index]) for index, filename in names.items}
    chars = dict()
    for index, filename in names.items():
        chars[filename] = crop_content(partition[index])
    return chars


# takes the map of char names and image data, uses that to export as files
def export_files(chars: dict, exports=None):
    # todo all the hard work
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
    filename = "src/font/data_00000000.font.png"
    print(f"Processing: {filename}")
    img = Image.open(filename)
    palette = process_palette(img)
    imarr = substitute_colors(numpy.array(img), palette)
    chars = process_font(imarr, normal_fontmap)
    export_files(chars)
    print(f"Finished processing: {filename}")

    filename = "src/font/data_00000002.font.png"
    print(f"Processing: {filename}")
    img = Image.open(filename)
    # palette = process_palette(img)  # same palette used in all data files
    imarr = substitute_colors(numpy.array(img), palette)
    chars = process_font(imarr, bold_fontmap)
    export_files(chars)
    print(f"Finished processing: {filename}.")
