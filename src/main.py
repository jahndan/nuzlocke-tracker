import sys
import pickle
import numpy
import cv2 as opencv
from mss import mss
import en_model as model
from common import reset, bold, italic, debug_format
from keyboard_input import globalHotkeys, event_queue


def print_arg_help():
    """information about the required arguments to run this script"""
    print(
        f"""{bold}ERROR: One or more necessary arguments were not passed.{reset} The following arguments are required to run this program:
   {bold}width{reset}:   the width of the capture window in pixels (integer)
   {bold}height{reset}:  the height of the capture window in pixels (integer)
   {bold}left{reset}:    the x-coordinate of the upper-left corner of the capture window (integer)
   {bold}top{reset}:     the y-coordinate of the upper-left corner of the capture window (integer)
   {bold}scale{reset}:   amount to downscale pixels by to match the images with (integer)
{italic}Note: on macOS with a retina display, the scaling factor will probably need to be twice what you expect.{reset}"""
    )


if __name__ == "__main__":
    ## TODO replace this with a more flexible way of passing args than sys.argv
    ## also allow user to specify language (currently only English supported)
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
        print_arg_help()
        exit(1)
    except ValueError:
        print("ERROR: Scale factor must be positive and nonzero!")
        exit(1)

    # if all args successfully parsed, load tracker savestate and continue
    try:
        with open("savestate.pickle", "rb") as load:
            state = pickle.load(load)
    except:
        # initialize a new tracker state assuming a new game
        state = model.TrackerState(location="Twinleaf Town")
        # assumed english for now since no other models exist yet

    sct = mss()
    bounding_box = {"width": width, "height": height, "left": left, "top": top}

    # initialize the tracker display canvas
    canvas = numpy.full((384, 256, 3), model.display_palette[0], dtype=numpy.uint8)
    model.draw_to_display(state, canvas)
    opencv.imshow("tracker", canvas)

    # temp: solely to make debugging less cluttered
    prev_state = ""

    while True:
        gbra = numpy.array(sct.grab(bounding_box))
        img = gbra[:, :, :3]  # discard alpha from screen capture
        res = opencv.resize(
            img, None, fx=scale, fy=scale, interpolation=opencv.INTER_NEAREST
        )

        model.process_frame(state, res)  # may mutate state
        if event_queue:  # implicitly evaluates false if empty
            model.handle_event(state, event_queue.popleft())

        # if the state has changed, update the display canvas
        if state.__repr__() != prev_state:
            prev_state = state.__repr__()
            print(f"{bold}STATE{reset}")
            print(debug_format(state))
            model.draw_to_display(state, canvas)
            opencv.imshow("tracker", canvas)

        opencv.imshow("screen", res)  # mainly for checking the bounds were correct
        if (opencv.waitKey(1) & 0xFF) == ord("q"):
            opencv.destroyAllWindows()
            break

    # on exit
    with open("savestate.pickle", "wb") as write:
        print("Saving current tracker state to 'savestate.pickle'")
        pickle.dump(state, write, protocol=pickle.HIGHEST_PROTOCOL)
