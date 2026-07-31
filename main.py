import datetime
import os
import traceback

from PIL import Image, ImageDraw, ImageFont
import yaml

from weekplanner.utils import wait_for_internet, load_events_cache, save_events_cache, get_cache_path, format_cache_timestamp
from weekplanner.weekplanner import Event, Day
from weekplanner.google import collect_agenda_data, get_timestamp_from_google, compact_google_event, compact_google_events
from weekplanner.weather_api import get_weather_openmeteo, get_weather_icon
from weekplanner.draw import get_icon, draw_shaded_rectangle, font_M, font_XL, font_L, split_image, font_S


now = datetime.datetime.now(datetime.UTC)

print(f'----Weekplanner started at: {now}-----')

all_errors = []
TEST_MODE = False
DEBUG_MODE = False
#%% Open the configuration
RESOLUTION = [800, 480] # Default resolution

with open("config.yaml", encoding="utf-8") as stream:
    try:
        config  = yaml.safe_load(stream)
        NO_DAYS = config['display']['no_days']
        NO_DAYS_LT = config['display']['no_days_long_term']
        RESOLUTION = config['display']['resolution']
    except yaml.YAMLError as exc:
        error_stack = traceback.format_exc()
        error_str = f'Failed to load configuration: {error_stack}'
        all_errors.append(error_str)
        print(error_str)




#%% Initiate the drawing
img = Image.new("RGB", RESOLUTION,
                (255, 255, 255))  # "1" = 1-bit pixels, 1 = white

draw = ImageDraw.Draw(img)

#%% Wait for internet
connected = wait_for_internet()
cache_path = get_cache_path(config)
end_time = now + datetime.timedelta(days=NO_DAYS_LT)

if connected:
    refreshed_cache = {
        "generated_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "window_start": now.isoformat(),
        "window_end": end_time.isoformat(),
        "agendas": {}
    }

    for _agenda in config['google']['agenda']:
        response_events = None
        try:
            response_events = collect_agenda_data(
                now,
                end_time,
                config['google'],
                agenda=_agenda
            )
            refreshed_cache["agendas"][_agenda['id']] = compact_google_events(response_events)
        except Exception:
            error_stack = traceback.format_exc()
            error_str = f'Failed to refresh agenda cache for {_agenda}: {error_stack}'
            print(error_str)
            all_errors.append(error_str)

    try:
        save_events_cache(cache_path, refreshed_cache)
    except Exception:
        error_stack = traceback.format_exc()
        error_str = f'Failed to save agenda cache to {cache_path}: {error_stack}'
        print(error_str)
        all_errors.append(error_str)
else:
    error_str = 'No internet, using locally cached Google agenda data.'
    all_errors.append(error_str)
    print(error_str)

events = []
cache_generated_at = None
try:
    cached_data = load_events_cache(cache_path)
    cache_generated_at = cached_data.get("generated_at")
    cached_agendas = cached_data.get("agendas", {})

    for _agenda in config['google']['agenda']:
        agenda_events = cached_agendas.get(_agenda['id'], [])
        for _e in agenda_events:
            try:
                compact_event = {
                    "summary": _e.get('summary', 'Untitled'),
                    "start": _e['start'],
                    "end": _e["end"]
                }
            except KeyError:
                # Backward compatibility: convert full Google event shape on read.
                compact_event = compact_google_event(_e)

            try:
                if compact_event is None:
                    continue
                events.append(
                    Event(
                        name=compact_event['summary'],
                        dt_start=get_timestamp_from_google(compact_event['start']),
                        dt_end=get_timestamp_from_google(compact_event["end"]),
                        config=config,
                        agenda=_agenda
                    )
                )
            except Exception:
                error_stack = traceback.format_exc()
                error_str = f'Failed to parse cached event for agenda {_agenda}: {error_stack}'
                print(error_str)
                all_errors.append(error_str)
except Exception:
    error_stack = traceback.format_exc()
    error_str = f'Failed to load cached agenda data from {cache_path}: {error_stack}'
    print(error_str)
    all_errors.append(error_str)

print(f'Found {len(events)} events from local cache')

# Draw something
# General

_ = draw_shaded_rectangle(draw, (5, 5, 795, 460))  # Outline


DAY_LENGTH = int(360)  # In pixels
DAY_WIDTH = int(round((RESOLUTION[0]-100)/NO_DAYS,0)) # Pixels


# Wat als we nu in plaats van dat lijntje een stippellijntje zetten? met dikker bolletjes als er iets is? Misschien dikkere
# punt voor zondagen?
distance = int(round((RESOLUTION[0]-20)/NO_DAYS_LT))
for i in range(NO_DAYS_LT):
    draw.point((10 + distance*i, 100), 0)

# draw.text((60, 60), "Hello e-ink!", font=font, fill=0)

# --- 4. Demo: draw rectangles with different "gray" levels ---
levels = [0.1, 0.3, 0.5, 0.7, 0.9]         # light -> dark tones

# Weather Block
weather_data = None
if connected:
    weather_data = get_weather_openmeteo(config['weather']['latitude'], config['weather']['longitude'])
elif TEST_MODE:
    print('Skipping weather fetch because internet is unavailable')

if TEST_MODE:
    print('Weather data')
    print(weather_data)

if weather_data:
    temp_max = weather_data['daily']['temperature_2m_max'][0]  # deg C
    temp_min = weather_data['daily']['temperature_2m_min'][0]  # deg C
    weather_code = weather_data['daily']['weather_code'][0]
    weather_icon = get_weather_icon(weather_code)

    draw.text((770, 15), f"{str(temp_max)}°C", font=font_L, fill=0, anchor='rt')
    draw.text((770, 80), f"{str(temp_min)}°C", font=font_M, fill=0, anchor='rb')
    img.paste(get_icon(weather_icon, category="weather"), (550, 20))

# Date block
dt = datetime.date.today()
draw.text((25, 10), f"{dt.strftime('%d/%m')}", font=font_XL, fill=0, anchor='lt')

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

# Add last update timestamp
draw.text(
    (15, RESOLUTION[1] - 5),
    f"Last update: {format_cache_timestamp(cache_generated_at)}",
    font=font_S,
    fill=0,
    anchor='lb'
)


# %% Show errors on screen
if all_errors and DEBUG_MODE:
    bg_coords = [10, 5, 780, 200]

    # Draw the white background rectangle
    draw.rectangle(bg_coords, fill="white")
    # Print the errors
    draw.text(
        (15, 10),
        all_errors[0],
        font=font_S,
        fill=0
    )

#%%
if TEST_MODE:
    img.show()  # or save
else:
    img_red, img_black = split_image(img)
    # Dithering to improve the visuals
    img_black = img_black.convert('1')
    img_red = img_red.convert('1')
    img_black.save(os.path.join(config['display']['output_folder'],"display.bmp"))
    img_red.save(os.path.join(config['display']['output_folder'],"display_r.bmp"))