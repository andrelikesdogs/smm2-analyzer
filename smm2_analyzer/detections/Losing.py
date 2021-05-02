import cv2
import numpy as np

from smm2_analyzer.utils import to_bgr, highlight_spot, match_color_score
from smm2_analyzer.event_types import EVENT_LOSE_VS

BG_COLOR_LOSE_SCREEN = to_bgr((247, 211, 12))
BG_COLOR_FONT_LOSE = to_bgr((96, 74, 193))
is_first_detection = True

def run_lose_check(playback: 'Playback', frame):
    global is_first_detection
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    # read color at specific point, if it's the right color, do the more expensive check
    lose_detect_pos_x = int(frame_w / 2)
    lose_detect_pos_y = int(frame_h * 0.3)
    
    lose_detect_score = match_color_score(frame[lose_detect_pos_y, lose_detect_pos_x], BG_COLOR_LOSE_SCREEN)
    color_check_spots = [
        (int(frame_w * 0.5025), int(frame_h * 0.528))
    ]

    if lose_detect_score < 1.0:
        total_pixel_count = frame_w * frame_h
        pixel_count = np.count_nonzero(np.all(frame==BG_COLOR_LOSE_SCREEN, axis=2))
        
        amount_of_pixels_bg_color = pixel_count / total_pixel_count

        if amount_of_pixels_bg_color > 0.9:
            all_spots_valid = True
            for color_check_pos in color_check_spots:
                highlight_spot(playback.debug_frame, color_check_pos[0],color_check_pos[1])
                
                font_color_match = match_color_score(frame[color_check_pos[1],color_check_pos[0]], BG_COLOR_FONT_LOSE)

                if font_color_match > 10.0:
                    all_spots_valid = False

            if all_spots_valid:
                if is_first_detection:
                    playback.add_debug_message("Lose Detected (vs)")
                    playback.add_event(EVENT_LOSE_VS)
                is_first_detection = False
        else:
            is_first_detection = True
    else:
        is_first_detection = True