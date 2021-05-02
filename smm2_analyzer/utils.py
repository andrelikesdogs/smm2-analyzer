import time
import cv2
import numpy as np
import colorsys
import re

from .constants import DETECTION_THRESHOLD_FACTOR

def to_bgr(pixel):
    return (pixel[2], pixel[1], pixel[0])
def to_rgb(pixel):
    return (pixel[2], pixel[1], pixel[0])

def bgr_to_hsl(pixel):
    return np.array(colorsys.rgb_to_hls(*[x / 255.0 for x in to_rgb(pixel)])) * 255.0

def current_millis():
    return round(time.time() * 1000)

def match_color_score(color_a, color_b, threshold=DETECTION_THRESHOLD_FACTOR):
    color_a_hsl = np.array(colorsys.rgb_to_hls(*[x / 255.0 for x in color_a])) * 255.0
    color_b_hsl = np.array(colorsys.rgb_to_hls(*[x / 255.0 for x in color_b])) * 255.0

    return np.sqrt(np.sum((color_a_hsl - color_b_hsl)**2))
    # return np.sqrt(np.sum((np.array(color_a) - np.array(color_b))**2))

def adjust_gamma(img, gamma):
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")

    return cv2.LUT(img, table)

def highlight_spot(frame, x, y, color = (0, 0, 255)):
    cv2.drawMarker(frame, (x, y), to_bgr(color))

    return frame

INT_ONLY_REGEX = re.compile('[^0-9]')
def only_int(val):
    #print((str(int(val)), str(val)))
    val_without_invalid_chars = re.sub(INT_ONLY_REGEX, '', val)

    return val_without_invalid_chars == str(val)