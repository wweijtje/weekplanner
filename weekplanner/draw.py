import os
import numpy as np
from PIL import Image, ImageFont

DEFAULT_FONT = 'verdana'
font_XL = ImageFont.truetype(DEFAULT_FONT, size=60)
font_L = ImageFont.truetype(DEFAULT_FONT, size=40)
font_M = ImageFont.truetype(DEFAULT_FONT, size=30)
font_S = ImageFont.truetype(DEFAULT_FONT, size=14)

def split_image(original: Image.Image):
    # Ensure RGB
    im = original.convert("RGB")
    width, height = im.size

    white_red = Image.new("RGB", (width, height), "white")
    white_black = Image.new("RGB", (width, height), "white")

    px = im.load()
    wr_px = white_red.load()
    wb_px = white_black.load()

    for y in range(height):
        for x in range(width):
            r, g, b = px[x, y]

            # classify
            if (r, g, b) == (0, 0, 0):            # black
                wb_px[x, y] = (0, 0, 0)          # keep in white-black
                wr_px[x, y] = (255, 255, 255)    # ignore in white-red

            elif (r, g, b) == (255, 0, 0):       # red
                wr_px[x, y] = (255, 0, 0)        # keep in white-red
                wb_px[x, y] = (255, 255, 255)    # ignore in white-black

            else:                                # white
                wr_px[x, y] = (255, 255, 255)
                wb_px[x, y] = (255, 255, 255)

    return white_red, white_black

# --- 1. Define Bayer matrix (8×8 classic) ---
def bayer_matrix(size=8):
    return np.array([
        [0, 48, 12, 60, 3, 51, 15, 63],
        [32, 16, 44, 28, 35, 19, 47, 31],
        [8, 56, 4, 52, 11, 59, 7, 55],
        [40, 24, 36, 20, 43, 27, 39, 23],
        [2, 50, 14, 62, 1, 49, 13, 61],
        [34, 18, 46, 30, 33, 17, 45, 29],
        [10, 58, 6, 54, 9, 57, 5, 53],
        [42, 26, 38, 22, 41, 25, 37, 21],
    ]) / 64.0

# --- 2. Convert it into a black/white tile for a tone ---
def bayer_tile(level: float, size=8):
    """Return an 8×8 halftone tile with black density based on `level` (0–1)."""
    m = bayer_matrix(size)
    arr = (m < level).astype(np.uint8) * 255
    return Image.fromarray(arr, mode="L")

# --- 3. Function to fill a rectangle in an existing image ---
def fill_rect_with_pattern(img, xy, tile):
    """Fill a rectangular area (x0, y0, x1, y1) with a repeated pattern tile."""

    x0, y0, x1, y1 = xy
    for y in range(y0, y1, tile.height):
        for x in range(x0, x1, tile.width):
            img.paste(tile, (x, y))

def draw_shaded_rectangle(draw, xy, fill=(255,255,255), outline=(0,0,0), shade_color=(0,0,0), shade_offset=0, shade_width=2):
    """
    Draws a rectangle with a shading line underneath it.

    Parameters
    ----------
    img : PIL.Image
        Image to draw on.
    xy : tuple
        Rectangle coordinates as (x1, y1, x2, y2).
    fill : str or tuple, optional
        Fill color of the rectangle.
    outline : str or tuple, optional
        Outline color of the rectangle.
    shade_color : str or tuple, optional
        Color of the shading line.
    shade_offset : int, optional
        Distance below the rectangle for the shading line.
    """

    # Draw the rectangle
    draw.rectangle(xy, fill=fill, outline=outline)

    # Draw a shading line below the rectangle
    x1, y1, x2, y2 = xy
    draw.line((x1- shade_width/2, y2 + shade_offset - shade_width/2, x2-shade_offset, y2 + shade_offset- shade_width/2), fill=shade_color, width=shade_width) # Horizontal shade
    draw.line((x1-shade_width/2, y1 + shade_offset, x1-shade_width/2, y2 + shade_offset), fill=shade_color, width=shade_width) # Vertical shade

    return draw

def get_icon(name: str, mode = 'normal', category=None):
    # Create a blank white image for 800x480
    if category:
        icon_folder = os.path.join("icons", category)
    else:
        icon_folder = "icons"
    icon = Image.open(os.path.join(icon_folder, f"{name}.png")).convert("RGBA")
    #
    if mode == 'small':
        icon = icon.resize((32, 32), Image.Resampling.LANCZOS)
    # Convert transparency to white background
    white_bg = Image.new("RGBA", icon.size, (255, 255, 255, 255))
    white_bg.paste(icon, (0, 0), icon)  # use icon's alpha as mask
    icon_bw = white_bg.convert("1")  # 1-bit for e-ink
    # Paste onto base
    return icon_bw