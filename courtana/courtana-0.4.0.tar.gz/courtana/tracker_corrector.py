#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
Tracker Corrector
=================

This module uses data that comes from the 2 Flies Tracker software to
find possible errors, asks confirmation to the user and apply the
corrections.

The user is able to watch the tracker results live on the video, and
when the script detects problems, it asks the user what to do.
OR
The script runs and identifies the problems, and then only shows those
to the user so he can decide what to do.
OR BOTH

In the end, a single pandas DataFrame is created containing the data of
both flies.


Instructions:
-------------

Keybinds to control the video processing loop:
* Q:           Quit and discard every change
* Down Arrow:  Autoplay
* Up Arrow:    Pause
* Left Arrow:  Go one frame backwards (only when the video is paused)
* Right Arrow: Go one frame forward (only when the video is paused)

To correct observed errors use:
* I: Swap flies identity
* O: Swap blue arrow orientation
* P: Swap pink arrow orientation
* M: Mark frame as corrected


"""

from os import path
import logging
import cv2
import pandas as pd

from video import Video
from tracker import TrackerData

VIDEO_PATH_TEMPLATE = "/media/hugo/DATA/R14H09/video_mix/videos"
VIDEO_FILENAME_TEMPLATE = "MA_{}.avi"
TRACKER_OUTPUT_PATH_TEMPLATE = "/media/hugo/DATA/R14H09/opencsp_output/all"
TRACKER_OUTPUT_FILENAME_TEMPLATE = "MA_{}_mtout.csv"

GENDER_SYMBOL = {'female': '♀', 'male': '♂'}
GENDER_COLOR = {'female': (150, 25, 198), 'male': (198, 150, 25)}


def draw_fly(frame, data, **kwargs):
    """Draw fly.
    Represents a fly's position and orientation in an OpenCV image with
    an arrow.
    :frame: an OpenCV image
    :data: a line of the DataFrame corresponding to the frame to visualize
    `kwargs` are passed to the arrowedLine method.
    """
    head_x = int(data["Position Head X [pixels]"])
    head_y = int(data["Position Head Y [pixels]"])
    tail_x = int(data["Position Tail X [pixels]"])
    tail_y = int(data["Position Tail Y [pixels]"])

    kwargs['thickness'] = kwargs.get('thickness', 2)
    kwargs['tipLength'] = kwargs.get('tipLength', 0.4)
    cv2.arrowedLine(frame, (tail_x, tail_y), (head_x, head_y), **kwargs)


def video_generator(video, start=None, end=None):
    """Video generator.
    :video: Video object
    Returns two consecutive frames: previous and current.
    """
    start = start if start is not None else 1
    end = end if end is not None else video.nframes
    for i in range(start, end):
        yield i-1, i


def check_head_tail_swap(df, pframe, cframe):
    """
    Check head/tail swap for both flies.
    In order to identify this, it looks at the flies' angle in two
    consecutive frames. If they differ by approximately 180 degrees,
    then probably a swap occurred.
    :df: Pandas DataFrame like TrackerData.female
    :pframe: Previous frame number
    :cframe: Current frame number
    """
    try:
        angle = df.loc[cframe, 'Rotation [degrees]']
        last_angle = df.loc[pframe, 'Rotation [degrees]']
    except KeyError:
        logging.warning("Failed to read frame {}".format(cframe))
    else:
        return compare_angles(angle, last_angle)


def compare_angles(a1, a2, err=25):
    """
    Compares two angles and returns True if their difference is in the
    range (180-err; 180+err)
    :a1: current angle
    :a2: previous angle
    :err: angle error (180+-err)
    """
    return 180 - err < abs(a1 - a2) < 180 + err


def scan_video(v, t, start=None, end=None):
    """
    Scan video for problems regarding swap of flies' identification or
    flies' orientation.
    Returns the frame numbers where such problems were noticed.

    :v: Video object
    :t: TrackerData object
    """
    logging.info("Scanning video...")
    frames_with_problems = []
    for pframe, cframe in video_generator(video, start, end):
        logging.debug("Frame %5d: scanning", cframe)
        if any((check_head_tail_swap(data.female, pframe, cframe),
                check_head_tail_swap(data.male, pframe, cframe))):
            logging.debug("Head/Tail swap problem detected")
            frames_with_problems.append(cframe)
    else:
        logging.info("Scan complete")
    return frames_with_problems


def show_frame(v, t, i):
    """Show frame.
    :v: Video object
    :t: TrackerData object
    :i: Frame number
    """
    logging.debug("Frame %5d: Show", i)
    frame = v.read_frame(i)

    # Display current frame number
    cv2.putText(frame,
                "Frame " + str(i),
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (255, 0, 0),
                1,
                cv2.LINE_AA)

    # Display fly position and orientation
    draw_fly(frame, t.female.loc[i], color=GENDER_COLOR['female'])
    draw_fly(frame, t.male.loc[i], color=GENDER_COLOR['male'])

    cv2.imshow("Video", frame)


def play_video(v, t, start=None, end=None, wait_time=1):
    """Play video
    :v: Video object
    :t: TrackerData object
    """
    start = start if start is not None else 0
    end = end if end is not None else v.nframes
    logging.info("Playing...")
    for i in range(start, end):
        show_frame(v, t, i)

        key = cv2.waitKey(wait_time)
        if key == ord('q'):
            logging.warning("Interrupted by user")
            break
    else:
        logging.info("Finished successfully")


if __name__ == '__main__':

    logging.basicConfig(filename=None,
                        format='%(levelname)s: %(message)s',
                        filemode='w',
                        level=logging.DEBUG)

    logging.info("Initializing TrackerCorrector")

    video_id = 2  # TOFIX User input

    # Video file name
    vfn = path.join(VIDEO_PATH_TEMPLATE,
                    VIDEO_FILENAME_TEMPLATE.format(video_id))
    logging.debug("Video path: %s", vfn)

    # Tracker data file name
    dfn = path.join(TRACKER_OUTPUT_PATH_TEMPLATE,
                    TRACKER_OUTPUT_FILENAME_TEMPLATE.format(video_id))
    logging.debug("Tracker data path: %s", dfn)

    # Output file name: tracker data corrected
    ofnf = path.join(TRACKER_OUTPUT_PATH_TEMPLATE,
                     "MA_{}_tracker_f.csv".format(video_id))
    ofnm = path.join(TRACKER_OUTPUT_PATH_TEMPLATE,
                     "MA_{}_tracker_m.csv".format(video_id))

    logging.info("Loading video")
    video = Video(vfn)

    logging.info("Loading tracker data")
    data = TrackerData(dfn, fbi=0, fps=30,  pxmm=31.060)

    logging.info("Initializing OpenCV window")
    window = cv2.namedWindow("Video")

    scan_results = scan_video(video, data, end=7000)
    print(scan_results)

    for frame in scan_results:
        print("* Frame {:5d}/{:5d}:".format(frame, video.nframes))
        show_frame(video, data, frame)

        # Which fly has problems?
        if check_head_tail_swap(data.female, frame-1, frame):
            logging.debug("Frame %5d: What to do?", frame)
            print("A problem with the Female's orientation was detected!")
            print("- Press [O] to correct the orientation")
            print("- Press [Q] to quit")
            print("- Any other key will skip this frame and move on")

            key = cv2.waitKey(0)
            if key == ord('o'):
                # Swap head/tail x position (a, b = b, a)
                data.female.loc[frame, "Position Head X [pixels]"], \
                    data.female.loc[frame, "Position Tail X [pixels]"] = \
                    data.female.loc[frame, "Position Tail X [pixels]"], \
                    data.female.loc[frame, "Position Head X [pixels]"]

                # Swap head/tail y position (a, b = b, a)
                data.female.loc[frame, "Position Head Y [pixels]"], \
                    data.female.loc[frame, "Position Tail Y [pixels]"] = \
                    data.female.loc[frame, "Position Tail Y [pixels]"], \
                    data.female.loc[frame, "Position Head Y [pixels]"]

                # Correct the angle
                # TODO maybe calculate it from new positions instead of
                # changing the value
                a0 = data.female.loc[frame-1, "Rotation [degrees]"]
                a1 = data.female.loc[frame, "Rotation [degrees]"]
                if a1 < a0:
                    data.female.loc[frame, "Rotation [degrees]"] += 180
                else:
                    data.female.loc[frame, "Rotation [degrees]"] -= 180
                logging.debug("Frame %5d: Corrected", frame)
            elif key == ord('q'):
                logging.warning("Interrupted by user")
                break
            else:
                logging.debug("Frame %5d: Ignored", frame)

        if check_head_tail_swap(data.male, frame-1, frame):
            logging.debug("Frame %5d: What to do?", frame)
            print("A problem with the Male's orientation was detected!")
            print("- Press [O] to correct the orientation")
            print("- Press [Q] to quit")
            print("- Any other key will skip this frame and move on")

            key = cv2.waitKey(0)
            if key == ord('o'):
                # Swap head/tail x position (a, b = b, a)
                data.male.loc[frame, "Position Head X [pixels]"], \
                    data.male.loc[frame, "Position Tail X [pixels]"] = \
                    data.male.loc[frame, "Position Tail X [pixels]"], \
                    data.male.loc[frame, "Position Head X [pixels]"]

                # Swap head/tail y position (a, b = b, a)
                data.male.loc[frame, "Position Head Y [pixels]"], \
                    data.male.loc[frame, "Position Tail Y [pixels]"] = \
                    data.male.loc[frame, "Position Tail Y [pixels]"], \
                    data.male.loc[frame, "Position Head Y [pixels]"]

                # Correct the angle
                # TODO maybe calculate it from new positions instead of
                # changing the value
                a0 = data.male.loc[frame-1, "Rotation [degrees]"]
                a1 = data.male.loc[frame, "Rotation [degrees]"]
                if a1 < a0:
                    data.male.loc[frame, "Rotation [degrees]"] += 180
                else:
                    data.male.loc[frame, "Rotation [degrees]"] -= 180
                logging.debug("Frame %5d: Corrected", frame)
            elif key == ord('q'):
                logging.warning("Interrupted by user")
                break
            else:
                logging.debug("Frame %5d: Ignored", frame)

    scan_results = scan_video(video, data, end=7000)
    print(scan_results)

    # play_video(video, data, 300, 700, wait_time=1)
