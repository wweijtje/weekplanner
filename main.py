import datetime
import os

from PIL import Image, ImageDraw, ImageFont
import yaml

from weekplanner.weekplanner import Event, Day
from weekplanner.google import collect_agenda_data, get_timestamp_from_google
from weekplanner.weather_api import get_weather_openmeteo, get_weather_icon
from weekplanner.draw import get_icon, draw_shaded_rectangle, font_M, font_XL, font_L, split_image

#%% Open the configuration

with open("config.yaml", encoding="utf-8") as stream:
    try:
        config  = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

NO_DAYS = config['display']['no_days']
NO_DAYS_LT = config['display']['no_days_long_term']
RESOLUTION = config['display']['resolution']

now = datetime.datetime.now(datetime.UTC)
end_time = now + datetime.timedelta(days=NO_DAYS_LT)

response_events = collect_agenda_data(now, end_time, config['google'])
print(response_events[0])



events = []
for _e in response_events:
    # try:
    events.append(
        Event(
            name=_e['summary'],
            dt_start = get_timestamp_from_google(_e['start']),
            dt_end = get_timestamp_from_google(_e["end"]),
            config= config
        )
    )
    # except:
    #     print(_e)
print(events[0])
print(f'Found {len(events)} events')


print(RESOLUTION)
img = Image.new("RGB", RESOLUTION, (255,255,255))  # "1" = 1-bit pixels, 1 = white


draw = ImageDraw.Draw(img)


# Draw something
# General

_ = draw_shaded_rectangle(draw, (10, 10, 790, 460))  # Outline


DAY_LENGTH = int(360)  # In pixels
DAY_WIDTH = int(round((RESOLUTION[0]-100)/NO_DAYS,0)) # Pixels


# Wat als we nu in plaats van dat lijntje een stippellijntje zetten? met dikker bolletjes als er iets is? Misschien dikkere
# punt voor zondagen?
distance = int(round((RESOLUTION[0]-20)/NO_DAYS_LT))
for i in range(NO_DAYS_LT):
    draw.point((10 + distance*i, 100), 0)

# draw.text((60, 60), "Hello e-ink!", font=font, fill=0)

# --- 4. Demo: draw rectangles with different "gray" levels ---
levels = [0.1, 0.3, 0.5, 0.7, 0.9]         # light → dark tones

# Weather Block
print('weer data')
weather_data = get_weather_openmeteo(config['weather']['latitude'], config['weather']['longitude'])
print(weather_data)
if weather_data:
    temp_max = weather_data['daily']['temperature_2m_max'][0]  # °C
    temp_min = weather_data['daily']['temperature_2m_min'][0]  # °C
    weather_code = weather_data['daily']['weather_code'][0]
    weather_icon = get_weather_icon(weather_code)

    draw.text((770, 15), f"{str(temp_max)}°C", font=font_XL, fill=0, anchor='rt')
    draw.text((770, 95), f"{str(temp_min)}°C", font=font_M, fill=0, anchor='rb')
    img.paste(get_icon(weather_icon, category="weather"), (500, 20))

# Date block
dt = datetime.date.today()
draw.text((15, 35), f"{dt.strftime('%d/%m/%y')}", font=font_L, fill=0, anchor='lt')

"""draw.rounded_rectangle(
    (100, 100, 300, 200),  # (x0, y0, x1, y1)
    radius=20,  # corner radius
    fill=0,  # black fill
    outline=1  # white outline
)"""

week_list = []

for i in range(NO_DAYS):

    week_list.append(
        Day(
            dt + datetime.timedelta(days=i),
            config=config
        )
    )





for _i, d in enumerate(week_list):
    for _e in events:
        if _e in d:
            d.add_event(event=_e)

    d.draw(img, draw_obj=draw, idx=_i)

print('Got to the end!')

draw.line((10, 100, RESOLUTION[0] - 10, 100),fill=(255,0,0)) # Horizontal divider


img.show()  # or save
img_red, img_black = split_image(img)
img_black.save(os.path.join(config['display']['output_folder'],"display.bmp"))
img_red.save(os.path.join(config['display']['output_folder'],"display_r.bmp"))
