import cv2
import os
import time

from .detections.Winning import run_win_check 
from .detections.Start import run_start_level_check
from .detections.Score import run_score_check
from .detections.Popups import run_popup_check
from .detections.Rating import run_rating_check
from .detections.Losing import run_lose_check
from .detections.Timeout import run_timeout_check

import smm2_analyzer.keypress_handler as keypress_handler

ANALYTIC_FUNCTIONS = [
    run_start_level_check,
    run_win_check,
    run_score_check,
    run_popup_check,
    run_rating_check,
    run_lose_check,
    run_timeout_check
]

class Playback:
    def __init__(self, file_list, start_file_index, start_frame, render=True):
        self.current_frame = start_frame
        self.total_frames = 0

        self.file_list = file_list
        self.current_file_index = start_file_index
        self.current_file = file_list[self.current_file_index]

        self.render = render

        self.frame = None
        self.debug_frame = None

        self.stopped = False
        self.paused = False
        self.playback_delay = 20

        self.debug_messages = []
        self.log_entries = []

        self.initalize_video()
        self.log(f"Started Playback with {len(file_list)} files on file {self.current_file_index} ({self.current_file})")

    def log(self, *args, **kwargs):
        self.log_entries.append(dict(
            file=self.current_file,
            frame=self.current_frame,
            total_frames=self.total_frames,
            message=args,
            message_kwargs=kwargs,
        ))
        cur_frame_t = str(self.current_frame).rjust(len(str(self.total_frames)), " ")
        print(f"[{self.current_file} - {cur_frame_t} of {self.total_frames}]", *args, **kwargs)

    def initalize_video(self):
        if self.current_file:
            self.video_source = cv2.VideoCapture(os.path.abspath(self.current_file), cv2.CAP_FFMPEG)

            if not self.video_source.isOpened():
                print("Capture failed")
                exit(0)

            self.total_frames = int(self.video_source.get(cv2.CAP_PROP_FRAME_COUNT))
            self.video_source.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

    def jump_to_segment(self, segment_num: int):
        self.current_file = self.file_list[segment_num]
        self.initalize_video()

    def jump_to_next(self):
        if self.current_file_index >= len(self.file_list):
            # all files done
            self.current_file = None
        else:
            self.current_file_index = self.current_file_index + 1
            self.current_file = self.file_list[self.current_file_index]
        self.initalize_video()

    def jump_to_prev(self):
        next_file_index = max(self.current_file_index, 0)
        self.jump_to_segment(next_file_index)


    def frame_scrubbing(self, num):
        elapsed = self.current_frame
        remaining = self.total_frames - self.current_frame
        
        # when at start of file
        if elapsed + num < 0:
            prev_frame = self.current_frame
            self.jump_to_prev()
            self.current_frame = self.total_frames - prev_frame
        # when at end of file
        elif elapsed + num > self.total_frames:
            self.jump_to_next()
            self.current_frame = abs(remaining - num)
        # otherwise just jump
        else:
            self.current_frame = self.current_frame + num
            
        self.video_source.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
    
    def read_frame(self):
        if self.current_frame + 1 > self.total_frames:
            self.jump_to_next()

        return_value, frame = self.video_source.read()
        self.current_frame = self.current_frame + 1
        
        if not return_value:
            print("could not read frame")
            return
        
        self.frame = frame
        self.debug_frame = self.frame.copy()

    def run_analysis(self):
        for check in ANALYTIC_FUNCTIONS:
            check(self, self.frame)

    def render_debug_frame(self):
        cur_time = int(time.time()*1000)

        start_height = 40
        pos_x = 10
        pos_y = start_height
        messages_to_remove = []
        for message_index, debug_message in enumerate(self.debug_messages):
            if cur_time > debug_message['destroy_time']:
                messages_to_remove.append(message_index)
            else:
                self.write_debug_text(debug_message['message'], (pos_x, pos_y + (20 * message_index)))
        
        for index in reversed(messages_to_remove):
            del self.debug_messages[index]

    def write_debug_text(self, text, position):
        offsets = [(1, 1), (-1, 1), (-1, -1), (1, -1)]

        for offset in offsets:
            cv2.putText(self.debug_frame, text, (position[0] + offset[0], position[1] + offset[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, 0)
            
        cv2.putText(self.debug_frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
    
    def add_debug_message(self, message, duration=10):
        self.log(message)
        self.debug_messages.append(dict(
            message=message,
            destroy_time=int(time.time()*1000) + (duration * 1000)
        ))

    def add_event(self, event_type, **event_args):
        self.log(f"{event_type}: ", event_args)

        if self.event_log_callback:
            self.event_log_callback(self.current_file_index, self.current_file, self.current_frame, event_type, event_args)

    def on_event(self, callback):
        self.event_log_callback = callback

    def stop(self):
        self.log("Playback stopped")
        self.stopped = True

    def pause(self):
        self.paused = True
    
    def unpause(self):
        self.paused = False

    def play(self):
        while True:
            if self.stopped:
                break

            self.read_frame()
            self.run_analysis()

            cur_frame_t = str(self.current_frame).rjust(len(str(self.total_frames)), " ")
            self.write_debug_text(f"Frame {cur_frame_t} of {self.total_frames} in {self.current_file}", (10, 20))
            
            if self.render:
                self.render_debug_frame()
                cv2.imshow("SMM2 Analyzer", self.debug_frame)

                wait_duration = 0 if self.paused else self.playback_delay
                keypress = cv2.waitKeyEx(wait_duration)

                if keypress > -1:
                    keypress_handler.handle(self, keypress)

