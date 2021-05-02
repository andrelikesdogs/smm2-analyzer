import numpy as np
import cv2
import pytesseract

from smm2_analyzer.utils import to_bgr, highlight_spot, adjust_gamma, only_int, match_color_score
from smm2_analyzer.constants import DETECTION_THRESHOLD_FACTOR
from smm2_analyzer.event_types import EVENT_RATED_LEVEL

BG_COLOR_SCORE_CHANGE = to_bgr((247, 211, 12))
BG_COLOR_OUTER_SCORE_CHANGE = to_bgr((4, 45, 84))

is_first_detection = True

CIRCLE_BG_UNSELECTED = (253, 253, 253)

CIRCLE_BG_SELECTED = (108, 196, 230)
CIRCLE_BG_SELECTED_ACTIVE = (156, 221, 250)

def run_rating_check(playback: 'Playback', frame):
    global is_first_detection
    
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]
    
    bg_check_corners = [
        # corners around current rank
        (int(frame_w * 0.4), int(frame_h * 0.3)),
        (int(frame_w * 0.6), int(frame_h * 0.3)),
        (int(frame_w * 0.4), int(frame_h * 0.7)),
        (int(frame_w * 0.6), int(frame_h * 0.7)),
        # edges
        (int(frame_w * 0.02), int(frame_h * 0.45)),
        (int(frame_w * 0.98), int(frame_h * 0.45)),
    ]

    bg_outer_check_corners = [
        (int(frame_w * 0.5), int(frame_h * 0.1)), # above
        (int(frame_w * 0.5), int(frame_h * 0.85)) # below
    ]

    circle_checks = [
        (int(frame_w * 0.345), int(frame_h * 0.45)),
        (int(frame_w * 0.5), int(frame_h * 0.45)),
        (int(frame_w * 0.655), int(frame_h * 0.45)),
    ]


    bg_outer_matches = True
    for bg_outer_check_corner in bg_outer_check_corners:
        bg_outer_corner_score = np.sqrt(np.sum((frame[bg_outer_check_corner[1], bg_outer_check_corner[0]] - BG_COLOR_OUTER_SCORE_CHANGE)**2)) 
        #bg_outer_corner_match_sum = bg_outer_corner_score
        #highlight_spot(debug_frame, bg_outer_check_corner[0], bg_outer_check_corner[1], color=(255, 0, 255))

        #print(bg_outer_corner_score)
        if bg_outer_corner_score > 40.0 * DETECTION_THRESHOLD_FACTOR:
            bg_outer_matches = False

    #print(bg_outer_corner_match_sum)

    bg_matches = True
    for bg_check_corner in bg_check_corners:
        bg_corner_score = np.sqrt(np.sum((frame[bg_check_corner[1], bg_check_corner[0]] - BG_COLOR_SCORE_CHANGE)**2)) 
        #bg_corner_match_sum = bg_corner_match_sum + bg_corner_score
        #highlight_spot(debug_frame, bg_check_corner[0], bg_check_corner[1], color=(255, 0, 0))

        if bg_corner_score > 0.1 * DETECTION_THRESHOLD_FACTOR:
            bg_outer_matches = False

    if bg_matches and bg_outer_matches:
        if is_first_detection:
            scores_selected = [match_color_score(frame[x[1], x[0]], CIRCLE_BG_SELECTED) for x in circle_checks]
            scores_selected_active = [match_color_score(frame[x[1], x[0]], CIRCLE_BG_SELECTED_ACTIVE) for x in circle_checks]
        
            sum_selected_scores = sum(scores_selected)

            if int((sum_selected_scores / len(scores_selected)) * 1000.0) == int(scores_selected[0] * 1000.0):
                #print("no selection made, in animation?")
                return
            
            lowest_score_index = None
            found_more_than_one = False
            for bg_check_pos_index, bg_check_score in enumerate(scores_selected_active):
                if bg_check_score < 1.0:
                    if lowest_score_index is not None:
                        found_more_than_one = True
                    lowest_score_index = bg_check_pos_index
            
            if lowest_score_index is not None:
                ratings = ["BOO", "MEH", "LIKE"]

                playback.add_debug_message(f"Rating was entered: {ratings[lowest_score_index]}")
                playback.add_event(EVENT_RATED_LEVEL, rating=ratings[lowest_score_index])


            is_first_detection = False
    else:
        is_first_detection = True