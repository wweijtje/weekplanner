import datetime
from .config import find_event
from .draw import draw_shaded_rectangle, get_icon, font_S
from .utils import time_to_y
from pytz import utc

WEEKDAY_STR = ['monday','tuesday','wednesday','thursday','friday', 'saturday', 'sunday']

class Event(object):
    def __init__(self, name, dt_start, dt_end, config, symbol=None, holiday=None):

        self.name = name
        self.dt_start = dt_start
        self.dt_end = dt_end - datetime.timedelta(milliseconds=1) # Little trick to resolve that a full day spreads out to the next
        self.config = {}
        self._config = config

        if holiday is None:
            self.holiday = False
        else:
            self.holiday = holiday

        if self.in_config:
            self.config, _e = find_event(self.name, config, category='events')

            if holiday is None:
                if _e == 'holiday':
                    self.holiday = True
                else:
                    self.holiday = False
            else:
                self.holiday = holiday

        if symbol is None: # Géén symbol zet symbol op '' of False tbd
            if self.config:
                self.symbol = self.config['symbol']
            else:
                # Try to find a symbol
                self.symbol = self.get_symbol()
        else:
            self.symbol = symbol

    @property
    def is_full_day(self):
        """
        Checks if the event is a full day
        :return:
        """
        if (self.dt_end - self.dt_start) > datetime.timedelta(hours=23.9):
            return True
        else:
            return False
    @property
    def in_config(self) -> bool:
        if find_event(self.name, self._config, category='events') is None:
            return False
        else:
            return True
    def get_symbol(self):
        print(f'No symbol found for "{self.name}"')
        return 'saw'

    def  draw(self, img, draw_obj, x_0, x_e):
        """
        Draw an event based on the
        :param x_0:
        :return:
        """
        y_0 = int(time_to_y(self.dt_start, config=self._config))
        y_e = int(time_to_y(self.dt_end, config=self._config))
        if self.is_full_day:
            print(f'{self.name}: Not drawing full day event')
        else:
            draw_shaded_rectangle(draw_obj, (x_0, y_0, x_e, y_e))
            if self.symbol not in ["none", '']:
                img.paste(get_icon(self.symbol, mode='small'), (x_0 + 2, y_0 + 2))

        draw_obj.text((x_0+10,y_e-10), self.name, font=font_S, fill=0, anchor='lb')

    def __str__(self):
        return f"Event {self.name}"

class Day(object):
    VALID_VALUES = ["full", "half", "none"]

    def __init__(self, date, config, school_day = None):
        self.date = date
        self.start = datetime.datetime.combine(
            self.date,
            datetime.datetime.min.time()
        ).replace(tzinfo=utc)
        self.end = datetime.datetime.combine(
            self.date,
            datetime.datetime.max.time()
        ).replace(tzinfo=utc)
        self._config = config

        print(f'Day end {self.end}')
        self.events = []
        if school_day is None:
            # No value provided, load default
            self.school_day = self._config['days'][self.weekday]['schoolday']
        else:
            self.school_day = school_day

    @property
    def school_day(self):
        return self._school_day
    @school_day.setter
    def school_day(self, value):
        if value not in self.VALID_VALUES:
            raise ValueError(f"school_day must be one of {self.VALID_VALUES} not '{value}'")
        self._school_day = value

    def add_event(self, event: Event):
        print(f'{event.name}: is {event.holiday} een vakantie')
        if event.holiday:

            self.school_day = 'none'
        self.events.append(event)

    def __contains__(self, event: Event) -> bool:
        """Return True if event overlaps with this day."""
        # check for any overlap between [event.start, event.end] and [day.start, day.end]
        return not (event.dt_end < self.start or event.dt_start > self.end)
    def draw(self, img, draw_obj, idx=0):
        from .draw import bayer_tile, fill_rect_with_pattern

        DAY_WIDTH = self._config['display']['day_width']
        DAY_Y0 = self._config['display']['day_y0']
        DAY_YE = self._config['display']['day_ye']

        x_offset = 20
        x_spacing = 10

        x_0 = int(x_offset + idx * DAY_WIDTH)
        y_0 = DAY_Y0
        x_e = int(x_offset + DAY_WIDTH - x_spacing + idx * DAY_WIDTH)
        y_e = DAY_YE
        fill_rect_with_pattern(
            img,
            (x_0, y_0, x_e, y_e),
            bayer_tile(0.9)
        )
        print(f'Dit is een {self.school_day} schooldag')
        if self.school_day == 'full':
            y_e_full = time_to_y(
                datetime.datetime(2025,11,15,15, tzinfo=utc),
                config=self._config
            )
            print(f'Full school day ({DAY_Y0},{y_e_full})')
            draw_shaded_rectangle(
                draw_obj,
                (x_0+5, DAY_Y0+10, x_e, y_e_full)
            )

        elif self.school_day == 'half':

            y_e_half = time_to_y(
                datetime.datetime(2025,11,12,12, tzinfo=utc),
                config=self._config
            )
            print(f'half school day ({DAY_Y0},{y_e_half})')

            draw_shaded_rectangle(
                draw_obj,
                (x_0+5, DAY_Y0+10, x_e, y_e_half)
            )
        else:
            # Do Nothing
            pass

        # Add the day symbols
        draw_shaded_rectangle(
            draw_obj,
            (x_0, y_0-22, x_0 + 70, y_0 + 48)
        )
        img.paste(get_icon(self.weekday_symbol), (x_0 + 2, y_0-20))

        # Add events
        for _e in self.events:
            _e.draw(x_0=x_0 +5,x_e=x_e, img=img, draw_obj=draw_obj)

    @property
    def weekday_symbol(self):
        return self._config['days'][self.weekday]['symbol']
    @property
    def weekday_str(self):
        return self._config['days'][self.weekday]['name']

    @property
    def weekday(self):
        return WEEKDAY_STR[self.date.isoweekday()-1]
    @property
    def is_today(self):
        # TODO
        return False