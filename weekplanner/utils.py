import os
from datetime import datetime, time
from PIL import Image
import numpy as np




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

