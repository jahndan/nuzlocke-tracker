import sys
import numpy
import cv2 as opencv
from mss import mss


def help():
    print(
        """\033[1mERROR: One or more necessary arguments were not passed.\033[0m The following arguments are required to run this program:
   \033[1mwidth\033[0m:   the width of the capture window in pixels (integer)
   \033[1mheight\033[0m:  the height of the capture window in pixels (integer)
   \033[1mleft\033[0m:    the x-coordinate of the upper-left corner of the capture window (integer)
   \033[1mtop\033[0m:     the y-coordinate of the upper-left corner of the capture window (integer)
   \033[1mscale\033[0m:   amount to downscale pixels by to match the images with (integer)
\033[3mNote: on macOS with a retina display, the scaling factor will probably need to be twice what you expect.\033[0m"""
    )


if __name__ == "__main__":
    # get all necessary args if given
    try:
        width, height = int(sys.argv[1]), int(sys.argv[2])
        left, top = int(sys.argv[3]), int(sys.argv[4])
        scaling = int(sys.argv[5])
        if scaling <= 0:
            raise ValueError
        scale = 1.00 / scaling

    # print explanation of necessary args
    except (IndexError, TypeError):
        help()
    except ValueError:
        print("ERROR: Scale factor must be positive and nonzero!")

    # if all args successfully parsed, continue
    else:
        sct = mss()
        bounding_box = {"width": width, "height": height, "left": left, "top": top}
        confidence = 0.99
        limit = 10000

        # read image with alpha channel
        sprite = opencv.imread("sprites/test.png", opencv.IMREAD_UNCHANGED)
        # split alpha channel to mask, keep rgb in sprite
        sprite, mask = sprite[:, :, :3], sprite[:, :, 3]

        while True:
            gbra = numpy.array(sct.grab(bounding_box))
            img = gbra[:, :, :3]  # discard alpha from screen capture

            res = opencv.resize(
                img, None, fx=scale, fy=scale, interpolation=opencv.INTER_NEAREST
            )

            # result = opencv.matchTemplate(res, sprite, opencv.TM_CCOEFF_NORMED)
            result = opencv.matchTemplate(
                res, sprite, opencv.TM_CCOEFF_NORMED, None, mask
            )
            match_indices = numpy.arange(result.size)[(result > confidence).flatten()]
            matches = numpy.unravel_index(match_indices[:limit], result.shape)
            print(matches)

            opencv.imshow("screen", res)
            if (opencv.waitKey(1) & 0xFF) == ord("q"):
                opencv.destroyAllWindows()
                break
