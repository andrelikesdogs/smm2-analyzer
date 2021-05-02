ARROW_RIGHT = 2555904
ARROW_LEFT = 2424832

def handle(playback, ord_key):
    chr_key = chr(ord_key) if ord_key <= 0x110000 else chr(0)
    #print(f"Keypress {ord_key} -> {chr_key}")

    if chr_key == 'p':
        playback.unpause() if playback.paused else playback.pause()
    
    if chr_key == 'n':
        playback.jump_to_next()
    
    if ord_key == ARROW_RIGHT:
        playback.frame_scrubbing(100)
    
    if ord_key == ARROW_LEFT:
        playback.frame_scrubbing(-100)

    if chr_key == '+':
        playback.playback_delay = min(playback.playback_delay + 10, 120)
    
    if chr_key == '-':
        playback.playback_delay = max(playback.playback_delay - 10, 1)
        

    '''
    if chr_key == 'r':
        #cv2.waitKey(0)

    if chr_key == 'n':
        print("skip to next file")
        #break

    if ord_key == 2555904: # arrow right
        #frame_counter = frame_counter + 1000
        #capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

    if chr_key == '+': # arrow right
        frame_counter = frame_counter + 100
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

    if ord_key == 2424832: # arrow left
        frame_counter = frame_counter - 1000

        if frame_counter < 0:
            frame_counter = 0
        
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

    if chr_key == '-': # arrow right
        frame_counter = frame_counter - 100

        if frame_counter < 0:
            frame_counter = 0
        
        capture.set(cv2.CAP_PROP_POS_FRAMES, frame_counter)

        #break
    '''
    if chr_key == 'q' or ord_key == 27:
        playback.stop()