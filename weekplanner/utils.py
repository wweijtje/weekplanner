import os
from datetime import datetime, time
from PIL import Image
import numpy as np
import textwrap


def draw_text_bottom_right(draw, text, box, font, fill=(0, 0, 0), spacing=2, ellipsis="…"):
    """
    Draw wrapped text inside box (x1,y1,x2,y2), bottom-right aligned.
    Adds ellipsis if the text does not fit vertically.
    """
    x1, y1, x2, y2 = box
    box_width  = x2 - x1
    box_height = y2 - y1

    # Estimate max chars per line
    avg_char_w = font.getlength("A")
    max_chars_per_line = max(1, int(box_width / avg_char_w))

    # Wrap the text
    wrapped = textwrap.wrap(text, width=max_chars_per_line)

    # Measurements
    line_height = font.getbbox("Hg")[3] - font.getbbox("Hg")[1]

    # Determine how many lines fit vertically
    max_lines = 1
    while True:
        total_h = max_lines * line_height + (max_lines - 1) * spacing
        if total_h > box_height:
            max_lines -= 1
            break
        max_lines += 1

    if max_lines < 1:
        return  # box too small to fit even one line

    # If text fits fully, use all wrapped lines
    if len(wrapped) <= max_lines:
        visible_lines = wrapped
    else:
        # Need to truncate: take bottom-most lines that fit
        visible_lines = wrapped[-max_lines:]

        # Add ellipsis to the first visible line
        first = visible_lines[0]
        # Ensure ellipsis fits in width
        ellipsis_width = font.getlength(ellipsis)
        max_width = box_width

        # Trim characters until the ellipsis fits
        while font.getlength(first + ellipsis) > max_width and len(first) > 0:
            first = first[:-1]

        visible_lines[0] = first + ellipsis

    # Bottom alignment
    total_text_height = len(visible_lines) * line_height + (len(visible_lines) - 1) * spacing
    current_y = y2 - total_text_height

    # Draw each line right-aligned
    for line in visible_lines:
        line_width = font.getlength(line)
        line_x = x2 - line_width
        draw.text((line_x, current_y), line, font=font, fill=fill)
        current_y += line_height + spacing


# Helper to convert a timestamp to vertical pixel coordinate
def time_to_y(dt, config, img_height=None, y_offset = None):

    START_OF_DAY = config['display']['start_of_day']
    END_OF_DAY = config['display']['end_of_day']

    if img_height is None:
        img_height = config['display']['day_ye']-config['display']['day_y0']

    if y_offset is None:
        y_offset = config['display']['day_y0']


    t_start = datetime.strptime(START_OF_DAY, '%H:%M').time()
    t_end = datetime.strptime(END_OF_DAY, '%H:%M').time()
    """Convert a datetime to a y-coordinate based on START/END_OF_DAY."""
    total_minutes_day = (
        datetime.combine(datetime.today(), t_end) -
        datetime.combine(datetime.today(), t_start)
    ).total_seconds() / 60

    minutes_since_start = (
        datetime.combine(datetime.today(), dt.time()) -
        datetime.combine(datetime.today(), t_start)
    ).total_seconds() / 60

    # Clip values (before or after the day range)
    minutes_since_start = max(0, int(min(minutes_since_start, total_minutes_day)))

    return int(y_offset + (minutes_since_start / total_minutes_day) * img_height)

def all_event_keywords(config, category="events"):
    all_keywords = ''
    for _e in config[category]:
        _c = config[category][_e]
        all_keywords += ''.join(_c['keywords'])
    all_keywords = all_keywords.lower().replace(' ','')
    return all_keywords

