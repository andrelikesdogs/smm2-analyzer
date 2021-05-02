import re

DETECTION_THRESHOLD_FACTOR = 1.5

BAD_POPUP_CHARS = r'[\n\r]'

RANKS = dict(
    D=(0, 999),
    C=(1000, 1999),
    B=(2000, 2999),
    A=(3000, 3999),
    S=(4000, 4999),
    S_PLUS=(5000, 9999)
)