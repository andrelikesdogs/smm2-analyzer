import cv2
import numpy as np
import pytesseract
import re

from smm2_analyzer.constants import DETECTION_THRESHOLD_FACTOR
from smm2_analyzer.utils import to_bgr, highlight_spot, adjust_gamma
from smm2_analyzer.event_types import EVENT_START_LEVEL


COLOR_LEVEL_START_BOX = to_bgr((247, 211, 12))
is_first_detection = False

def run_start_level_check(playback: 'Playback', frame):
    global is_first_detection
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    code_corners = [
        (int(frame_w * 0.065), int(frame_h * 0.248)),
        (int(frame_w * 0.215), int(frame_h * 0.248)),
        (int(frame_w * 0.065), int(frame_h * 0.285)),
        (int(frame_w * 0.215), int(frame_h * 0.285)),
    ]
    start_corners = [
        (int(frame_w * 0.945), int(frame_h * 0.28)),
        (int(frame_w * 0.055), int(frame_h * 0.28)),
        (int(frame_w * 0.945), int(frame_h * 0.09)),
        (int(frame_w * 0.055), int(frame_h * 0.09)),
    ]
    bg_check_positions = [
        (int(frame_w * 0.5), int(frame_h * 0.33)),
        (int(frame_w * 0.055), int(frame_h * 0.33)),
        (int(frame_w * 0.945), int(frame_h * 0.33)),
    ]

    #bg_check_pos = (int(frame_w * 0.5), int(frame_h * 0.35))

    bg_color_match_sum = 0
    for bg_check_pos in bg_check_positions:
        #highlight_spot(debug_frame, bg_check_pos[0], bg_check_pos[1], color=(255, 255, 255))
        bg_color_match_sum = bg_color_match_sum + np.sum(frame[bg_check_pos[1], bg_check_pos[0]])
    #print(bg_color_match)

    if bg_color_match_sum < 0.2 * DETECTION_THRESHOLD_FACTOR:
        correct_corners = 0
        for corner in start_corners:
            #print(to_bgr(frame[corner[1], corner[0]]))
            corner_match_score = np.sqrt(np.sum((frame[corner[1], corner[0]] - COLOR_LEVEL_START_BOX)**2))

            #highlight_spot(debug_frame, corner[0], corner[1], color=(0, 255, 255))
            if corner_match_score < (20.0 * DETECTION_THRESHOLD_FACTOR): # slight gradient on box
                correct_corners = correct_corners + 1

        if correct_corners == len(start_corners):
            #print("start detected")
            if is_first_detection:
                #logger.log("Level Start detected")
                # only runs on first time the corners were detected
                # run OCR
                
                code_only = frame[
                    code_corners[0][1]:code_corners[3][1],
                    code_corners[0][0]:code_corners[3][0]
                ]

                code_only_gamma = adjust_gamma(code_only, 0.4)
                level_code = pytesseract.image_to_string(code_only_gamma)

                # common issue with level code reading, but O can't appear in code
                level_code = level_code.strip().replace('O', '0')
                level_code_cleaned = re.sub(r'(\s|[^A-Z0-9])', '', level_code)

                playback.add_debug_message(f"Level Started detected, Code: {level_code}")
                playback.add_event(EVENT_START_LEVEL, level_code=level_code)

            is_first_detection = False
        else:
            # reset first detection flag for next detection
            is_first_detection = True
    else:
        # reset first detection flag for next detection
        is_first_detection = True