import numpy as np
import cv2
import pytesseract

from smm2_analyzer.utils import to_bgr, highlight_spot, adjust_gamma, only_int
from smm2_analyzer.constants import DETECTION_THRESHOLD_FACTOR, RANKS
from smm2_analyzer.event_types import EVENT_SCORE_VS_CHANGE

BG_COLOR_SCORE_CHANGE = to_bgr((247, 211, 12))
BG_COLOR_OUTER_SCORE_CHANGE = to_bgr((4, 45, 84))

detection_counter = 0
staged_score_values = None
last_kinda_hash = None

def run_score_check(playback: 'Playback', frame):
    global detection_counter
    global staged_score_values
    global last_kinda_hash
    
    frame_h = frame.shape[0]
    frame_w = frame.shape[1]

    bg_check_corners = [
        # corners around current rank
        (int(frame_w * 0.4), int(frame_h * 0.3)),
        (int(frame_w * 0.6), int(frame_h * 0.3)),
        (int(frame_w * 0.4), int(frame_h * 0.55)),
        (int(frame_w * 0.6), int(frame_h * 0.55)),
        # edges
        (int(frame_w * 0.02), int(frame_h * 0.45)),
        (int(frame_w * 0.98), int(frame_h * 0.45)),
    ]

    bg_outer_check_corners = [
        (int(frame_w * 0.5), int(frame_h * 0.1)), # above
        (int(frame_w * 0.5), int(frame_h * 0.58)), # inside rank diamond
        (int(frame_w * 0.5), int(frame_h * 0.85)) # below
    ]

    rank_score_box = [
        (int(frame_w * 0.65), int(frame_h * 0.73)),
        (int(frame_w * 0.775), int(frame_h * 0.77)),
    ]

    # current_rank_box = [
    #     (int(frame_w * 0.45), int(frame_h * 0.35)),
    #     (int(frame_w * 0.55), int(frame_h * 0.50)),
    # ]


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

    # for current_rank_box_pos in current_rank_box:
    #     highlight_spot(playback.debug_frame, current_rank_box_pos[0], current_rank_box_pos[1])

    if bg_matches and bg_outer_matches:
        if detection_counter > 10:
            if detection_counter == 10:
                # only outputs once (yea a lil shitty oops)
                print("Score change detected")

            for box_corner in rank_score_box:
                highlight_spot(playback.debug_frame, box_corner[0], box_corner[1], color=(0, 255, 255))

            crop = frame[rank_score_box[0][1]:rank_score_box[1][1], rank_score_box[0][0]:rank_score_box[1][0]]

            #crop = cv2.bitwise_not(crop)
            crop = cv2.resize(crop, (crop.shape[1]*2, crop.shape[0]*2))
            crop = adjust_gamma(crop, 0.2)

            # not really a hash but maybe good enough
            hash_kinda = np.sum(crop)

            if not last_kinda_hash or hash_kinda != last_kinda_hash:
                #print(hashKinda)
                #cv2.imshow("score change", crop)
                score_read_str = pytesseract.image_to_string(crop).strip()

                if "/" in score_read_str:
                    # clean up values
                    rank_score, rank_score_needed_for_rankup = [x.strip() for x in score_read_str.split("/")]
                    
                    # make sure it's not malformed
                    if only_int(rank_score) and only_int(rank_score_needed_for_rankup):
                        staged_score_values = (int(rank_score), int(rank_score_needed_for_rankup))
                        #logger.log(f"Reading Score: {staged_score_values}")
                    else:
                        playback.log(f"Read failed due to invalid character in \"{score_read_str}\"")
                        detection_counter = 0
                else:
                    detection_counter = 0
            
            last_kinda_hash = hash_kinda
            #return True

        detection_counter = detection_counter + 1
    else:
        detection_counter = 0

        if staged_score_values:
            playback.add_debug_message(f"Final Score changes: {staged_score_values}")

            matched_rank = None
            points = staged_score_values[0]
            next_rank = staged_score_values[1]

            for rank, rank_range in RANKS.items():
                if points >= rank_range[0] and points <= rank_range[1]:
                    matched_rank = rank

            playback.add_event(EVENT_SCORE_VS_CHANGE, points=points, next_rank=next_rank, rank=matched_rank)

            staged_score_values = None

    #print(bg_outer_corner_match_sum)