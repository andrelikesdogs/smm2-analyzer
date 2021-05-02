import smm2_analyzer.playback import Playback

vid_files = glob.glob("vids/*.mp4")

def test_popups():
    player = Playback()

    # popups we want to test from simpleflips videos
    