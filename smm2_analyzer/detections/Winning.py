import cv2
import numpy as np

from smm2_analyzer.utils import to_bgr, highlight_spot
from smm2_analyzer.event_types import EVENT_WIN_VS

BG_COLOR_WIN_SCREEN = to_bgr((216, 26, 47))
is_first_detection = False

def run_win_check(playback: 'Playback', frame):
    global is_first_detection
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    # read color at specific point, if it's the right color, do the more expensive check
    win_detect_pos_x = int(frame_w / 2)
    win_detect_pos_y = int(frame_h * 0.3)

    #print(frame[winDetectPosY, winDetectPosX])
    win_detect_score = np.sqrt(np.sum((frame[win_detect_pos_y, win_detect_pos_x] - BG_COLOR_WIN_SCREEN)**2))

    if win_detect_score < 1.0:
        #print("entering win detection")
        total_pixel_count = frame_w * frame_h
        pixel_count = np.count_nonzero(np.all(frame==BG_COLOR_WIN_SCREEN, axis=2))
        
        amount_of_pixels_bg_color = pixel_count / total_pixel_count

        if amount_of_pixels_bg_color > 0.9:
            if is_first_detection:
                #logger.log("Win Detected")
                playback.add_debug_message("Win Detected (vs)")
                playback.add_event(EVENT_WIN_VS)
            is_first_detection = False
        else:
            is_first_detection = True


    #highlight_spot(debug_frame, win_detect_pos_x, win_detect_pos_y)