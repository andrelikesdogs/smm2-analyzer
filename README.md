# Super Mario Maker 2: Analyzer

Analyze video files showing gameplay from the Nintendo Switch Game Super Mario Maker 2. It will analyze the videos frame by frame and log out events of gameplay events. Currently supported detections are:

- Level Start
    - Will log out the Level Code in the Event
- Versus Mode: Lose
- Versus Mode: Win
- Versus Mode: Time-Out
- Versus Mode: "Popup Box" Lose (player-character colored box that shows `<playername> has reached the goal`)
    - Will log character
- Versus Mode: Score Change
- Versus Mode: Level Ratings (except after a time-out)

# Usage
Clone the project and using python3, initialize a virtual-environment. (`python -m venv .`)

After activating the virtual environment, run the following command.

```bash
python main.py <videofile-glob> <start-file-index> <start-frame>
```
e.g.
```bash
python main.py vids/*.mp4 # starts playback on all videos in folder vids ending in .mp4
python main.py vids/*.mp4 --no-render # like above, but without visual output for faster processing
```

When the playback window is shown, the following keystrokes can be used to adjust playback/navigate:
| Keystroke | Function |
|-----------|----------|
| <kbd>q</kbd> or <kbd>esc</kbd> | Quit |
| <kbd>n</kbd> | Next File |
| <kbd>p</kbd> | Prev File |
| <kbd>→</kbd> (Arrowkey Right) | Skip 1000 Frames |
| <kbd>←</kbd> (Arrowkey Left) | Revert 1000 Frames |
| <kbd>+</kbd> (Numpad +) | Increase playback delay (slow down playback) |
| <kbd>-</kbd> (Numpad -) | Decrease playback delay (speed up playback) |

While the program is running, inspect the `events.log` file in the working directory, it will contain all logged events.

# Why?
After watching [https://www.youtube.com/watch?v=073XUHanTgo&list=PL3Hg1a3VjI1aOI1tB6gjSDO1tNUtdTaXQ](Simpleflips Walkies Series von Youtube) and seeing that a documentation about his in-game statistics were already assembled manually, I began to become interest in the idea of automating this analysis.

# How?
Using Python OpenCV I'm able to look through each frame of the video files and look for specific colors in specific places. It is very simple detections, but I'm sure this system can be expanded upon. Ironically, the software is currently unable to analyze simpleflips videos, as they're too heavily edited. Maybe more sophisticated algorithms will be able to detect more features more reliably in the future.

