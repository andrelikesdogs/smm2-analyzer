import numpy as np
import glob
import os
import sys
from pathlib import Path
from imutils.video import FPS

import argparse

from smm2_analyzer.detections.Winning import run_win_check 
from smm2_analyzer.detections.Start import run_start_level_check
from smm2_analyzer.detections.Score import run_score_check
from smm2_analyzer.detections.Popups import run_popup_check
from smm2_analyzer.detections.Rating import run_rating_check

from smm2_analyzer.playback import Playback

parser = argparse.ArgumentParser(description="Run SMM Computervision analysis on files")
parser.add_argument('file_index', type=int, default=0, nargs="?")
parser.add_argument('frame_index', type=int, default=0, nargs="?")
parser.add_argument('--no-render', action="store_true")
args = parser.parse_args()

if __name__ == "__main__":
    vid_files = glob.glob("vids/*.mp4")
    
    start_file_index = args.file_index
    start_frame = args.frame_index
    no_render  = args.no_render

    player = Playback(vid_files, start_file_index, start_frame, render=not no_render)

    event_file = 'events.log'
    file_handle = open(event_file, "w+")
    file_handle.close()

    def event_writer(file_index, file_name, frame_index, event, event_args):
        with open(event_file, 'a') as event_log:
            event_log.write(f'[{file_name} - {frame_index}]: {event} ({str(event_args)})\n')

    player.on_event(event_writer)
    player.play()
