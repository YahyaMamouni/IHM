# -*- coding: utf-8 -*-

import re
import subprocess


def get_console_screen_resolution():
    xrandr_output = str(
        subprocess.Popen(["xrandr"], stdout=subprocess.PIPE).communicate()[0]
    )
    match_obj = re.findall(r"current\s(\d+) x (\d+)", xrandr_output)

    width = -1
    height = -1

    if match_obj:
        width = match_obj[0][0]
        height = match_obj[0][1]

    return width, height


def has_a_16_by_9_screen_ratio():
    width, height = get_console_screen_resolution()
    return int(width) / 16 * 9 == int(height)
