import numpy as np
import cv2
import pytesseract
import re

from smm2_analyzer.utils import to_bgr, highlight_spot, match_color_score, adjust_gamma, bgr_to_hsl
from smm2_analyzer.constants import BAD_POPUP_CHARS
from smm2_analyzer.event_types import EVENT_LOSE_VS_POPUP, EVENT_CLEARCON_VS_POPUP

POPUP_HUE_RANGES = dict(
    mario=(170, 190),
    luigi=(290, 310),
    toad=(45, 60),
    toadette=(110, 150)
)

'''
POP_HUE_VALUE_RANGES = [
    (170, 190), # mario
    (290, 310), # luigi
    (35, 55), # blue
    (110, 150), # toadette

    # to_bgr((231, 45, 153)), # toadette pink
    # to_bgr((21, 220, 15)), # luigi green
    # to_bgr((225, 21, 56)), # mario red
    # to_bgr((11, 64, 236)), # toad blue
]
CHARACTER_NAMES = ['Toadette', 'Luigi', 'Mario', 'Toad'] 

detection_count = 0

def run_popup_check(playback: 'Playback', frame):
    global detection_count
    ##frame = cv2.resize(frame, (frame.shape[1]*2, frame.shape[0]*2))

    frame_h = frame.shape[0]
    frame_w = frame.shape[1]
    
    # these must match one of the 4 player colors
    crop_bounds = [
        (int(frame_w * 0.5), int(frame_h * 0.3640)), # 0.3740
        (int(frame_w * 0.5), int(frame_h * 0.47)), # 0.46
    ]

    frame_strip = frame[crop_bounds[0][1]:crop_bounds[1][1], 0:frame_w]
    frame_strip_h = frame_strip.shape[0]

    undistorted_resized_strip = cv2.resize(frame_strip, (frame_strip.shape[1]*2, frame_strip.shape[0]*2))
    resized_frame_strip = cv2.resize(frame_strip, (frame_strip.shape[1]*2, frame_strip.shape[0]*4))
    resized_frame_strip_w = resized_frame_strip.shape[1]
    resized_frame_strip_h = resized_frame_strip.shape[0]

    invert_stripe = cv2.bitwise_not(resized_frame_strip)

    # relative to crop with resized frame strip
    popup_bounds = [
        (int(resized_frame_strip_w * 0.5), 28),
        (int(resized_frame_strip_w * 0.5), resized_frame_strip_h-38),
    ]

    # these must *not* match one of the 4 player colors
    non_popup_color_positions = [
        (int(resized_frame_strip_w * 0.5), 1),
        (int(resized_frame_strip_w * 0.5), resized_frame_strip_h-1),
    ]
    
    resized_frame_strip_debug = resized_frame_strip.copy()

    color_indices_detected = list()
    found_colors = []
    for boundary_index, popup_bound in enumerate(popup_bounds):
        # NOTE: color inverted!!! otherwise hue values are too close
        color_in_stripe = invert_stripe[popup_bound[1], popup_bound[0]]
        pixel_hsl = bgr_to_hsl(color_in_stripe)
        pixel_hue = pixel_hsl[0]
        #print(to_bgr(color_in_stripe))
        #print(boundary_index)

        for hue_index, hue in enumerate(POP_HUE_VALUE_RANGES):
            #match = #match_color_score(to_bgr(color_in_stripe), to_bgr(color))
            #print(hue)
            hue_adjusted_min = (hue[0] / 360.0) * 255.0
            hue_adjusted_max = (hue[1] / 360.0) * 255.0

            #print(hue_index, hue_adjusted_min, hue_adjusted_max, pixel_hue, to_bgr(color_in_stripe))

            if pixel_hue > hue_adjusted_min and pixel_hue < hue_adjusted_max:
                found_colors.append(color_in_stripe)
                color_indices_detected.append(hue_index)

        #highlight_spot(resized_frame_strip_debug, int(popup_bound[0]), int(popup_bound[1]), color=(255, 0, 0))
    
    #print(color_indices_detected)
    if len(color_indices_detected) > 0:
        # all indices must be unique (cant be 2 diff borders)
        all_unique = len(set(color_indices_detected)) == 1

        # all positions must match
        all_found = len(color_indices_detected) == len(popup_bounds)

        # bg cant be same color as the detected
        bg_not_same = True

        #print(f"unique: {all_unique}, all_found: {all_found}")

        # if all_unique:
        #     for non_popup_color_position in non_popup_color_positions:
        #         #highlight_spot(playback.debug_frame, int(non_popup_color_position[0]), int(non_popup_color_position[1]), color=(255, 0, 0))
        #         match = match_color_score(resized_frame_strip[non_popup_color_position[1], non_popup_color_position[0]], POPUP_BORDER_COLORS[color_indices_detected[0]])

        #         if match < 40.0:
        #             playback.log("bg detected as same color")
        #             bg_not_same = False

        #print(all_unique, all_found)
        if all_unique and all_found and bg_not_same:
            detection_count = detection_count + 1
            #print(detection_count)
            if detection_count == 10:
                popup_color_index = color_indices_detected[0]

                crop_bounds = [
                    (int(frame_w * 0.5), int(frame_h * 0.3740)), # 0.3740
                    (int(frame_w * 0.5), int(frame_h * 0.46)), # 0.46
                ]

                # find box end
                is_correct_color = False
                x_pos = 10
                x_step = int(frame_w / 500)
                y_pos = int(round(frame_strip_h/2.0))

                target_color = sum(found_colors) / len(found_colors) #POPUP_BORDER_COLORS[popup_color_index]
                print(target_color)
                half_w = None

                while not is_correct_color:
                    # may be smarter to use contour tracking here?
                    found_color = invert_stripe[y_pos, x_pos]
                    #highlight_spot(playback.debug_frame, int(x_pos), int(round(popup_bounds[0][1] + y_pos)), color=target_color)

                    found_color_score = match_color_score(found_color, target_color)              
                    #print(x_pos, to_bgr(found_color), found_color_score)

                    if found_color_score < 20.0:
                        half_w = (frame_w/2)-x_pos
                        break

                    x_pos = x_pos + x_step                    
                    #print(x_pos)
                    if x_pos >= frame_w/2:
                        #logger.log("Could not find popup boundaries")
                        break

                if half_w is not None:
                    # mii img offset
                    x_offset_left = frame_w / 20.0
                    
                    padding = int(frame_w / 500)
                    x_start = int(frame_w/2 - half_w) + int(x_offset_left) + padding
                    x_end = int(frame_w/2 + half_w) - padding
                    frame_popup_box = frame_strip[padding:frame_strip_h-padding, x_start:x_end]
                    #frame_popup_box = cv2.resize(frame_popup_box, (frame_popup_box.shape[1]*4, frame_popup_box.shape[0]*4))

                    gamma_adjusted = adjust_gamma(frame_popup_box, 0.001)

                    char_name = CHARACTER_NAMES[popup_color_index]
                    popup_text =     pytesseract.image_to_string(gamma_adjusted).strip()
                
                    playback.add_debug_message(f"Popup Box detected for {char_name}: {popup_text}")
                    #cv2.imshow("popup threshold 2", gamma_adjusted)
                    
                    is_first_detection = False
                    #return True
                else:
                    detection_count = 0
        else:
            detection_count = 0

    else:
        detection_count = 0
        
    cv2.imshow("popup threshold 2", resized_frame_strip_debug)
    #print(detection_count)
'''
detection_count = 0
def run_popup_check(playback: 'Playback', frame):
    global detection_count

    frame_w = frame.shape[1]
    frame_h = frame.shape[0]

    crop_bounds = [
        (int(frame_w * 0.5), int(frame_h * 0.3640)), # 0.3740
        (int(frame_w * 0.5), int(frame_h * 0.47)), # 0.46
    ]
    
    crop = frame[
        crop_bounds[0][1]:crop_bounds[1][1],
        0:frame_w,
    ]
    crop_height = crop.shape[0]

    # invert for better hue seperation
    crop_inverted = cv2.bitwise_not(crop)

    hue_test_positions = [
        (int(frame_w * 0.5), int(crop_height * 0.1)),
        (int(frame_w * 0.5), int(crop_height * 0.9)),
    ]

    hue_neg_test_positions = [
        (int(frame_w * 0.5), int(crop_height * 0)),
        (int(frame_w * 0.5), int(crop_height * 1)-1),
    ]

    popup_playercolors_detected = []
    for player_character, hue_range in POPUP_HUE_RANGES.items():
        hue_min = (hue_range[0] / 360.0) * 255.0
        hue_max = (hue_range[1] / 360.0) * 255.0
        
        #print(player_character, hue_range)
        for hue_test_position in hue_test_positions:
            #highlight_spot(playback.debug_frame, hue_test_position[0], crop_bounds[0][1] + hue_test_position[1], (0, 0, 255))

            hsl_at_pixel = bgr_to_hsl(crop_inverted[hue_test_position[1]][hue_test_position[0]])
            hue_at_pixel = hsl_at_pixel[0]
            #print((hue_at_pixel / 255.0) * 360.0)

            if hue_at_pixel > hue_min and hue_at_pixel < hue_max:
                #print(player_character, hue_at_pixel, hue_range)
                #print("MATCH")
                popup_playercolors_detected.append(player_character)

    #print(popup_playercolors_detected)
    all_found = len(popup_playercolors_detected) == len(hue_test_positions)
    all_unique = len(set(popup_playercolors_detected)) == 1

    if all_found and all_unique:
        target_character = popup_playercolors_detected[0]
        bg_positions_match_popup_color = []
        
        hue_range = POPUP_HUE_RANGES[target_character]

        hue_min = (hue_range[0] / 360.0) * 255.0
        hue_max = (hue_range[1] / 360.0) * 255.0
        for hue_neg_test_index, hue_neg_test_position in enumerate(hue_neg_test_positions):
            hsl_at_pixel = bgr_to_hsl(crop_inverted[hue_neg_test_position[1]][hue_neg_test_position[0]])
            hue_at_pixel = hsl_at_pixel[0]

            #print(hue_neg_test_index)

            if hue_at_pixel > hue_min and hue_at_pixel and hue_at_pixel < hue_max:
                bg_positions_match_popup_color.append(hue_neg_test_index)

        if len(bg_positions_match_popup_color) == 0:
            detection_count = detection_count + 1
            if detection_count == 10:
                playback.add_debug_message(f"Popup Box for {target_character} possible")

                crop_filtered = cv2.bitwise_not(crop_inverted)
                #crop_gray = cv2.cvtColor(crop_inverted, cv2.COLOR_BGR2GRAY)
                
                read_texts = []
                for i in range(1, 100, 15):
                    popup_copy = crop_filtered.copy()
                    gamma = 0.01 + (i / 1000.0)
                    #print(gamma)
                    popup_copy = adjust_gamma(popup_copy, gamma)
                    ret, crop_threshed = cv2.threshold(popup_copy, 100, 255, cv2.THRESH_BINARY)
                    #crop_filtered = cv2.bitwise_not(crop_inverted)
                    popup_text = pytesseract.image_to_string(crop_threshed).strip()
                    filtered_text = re.sub(BAD_POPUP_CHARS, '', popup_text)

                    if "has" in filtered_text or "!" in filtered_text:
                        read_texts.append(filtered_text)
                    #playback.add_debug_message(popup_text)
                    #cv2.imshow("crop filtered", crop_threshed)
                
                REGEX_WIN = re.compile('(reached|goal)!?', flags=re.IGNORECASE)
                REGEX_CLEAR_CON = re.compile('(completed|clear|condition)!?', flags=re.IGNORECASE)

                #print([str(read_text) for read_text in read_texts])
                matches_win_regex = [REGEX_WIN.search(read_text) for read_text in read_texts]
                matches_clear_con_regex = [REGEX_CLEAR_CON.search(read_text) for read_text in read_texts]

                #print(matches_win_regex)
                #print(matches_clear_con_regex)

                is_detected_as_win = any(matches_win_regex)
                is_detected_as_clearcon = any(matches_clear_con_regex)

                if is_detected_as_win or is_detected_as_clearcon and not (is_detected_as_win and is_detected_as_clearcon):
                    if is_detected_as_win:
                        playback.add_event(EVENT_LOSE_VS_POPUP, character=target_character)
                    if is_detected_as_clearcon:
                        playback.add_event(EVENT_CLEARCON_VS_POPUP, character=target_character)
                else:
                    playback.log(read_texts)
                    playback.add_debug_message("Warning: Unclear detection of Popup Text")

        else:
            detection_count = 0
    else:
        detection_count = 0