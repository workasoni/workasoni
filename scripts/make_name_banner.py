"""
Stand-in for prep_photo.py when there is no portrait photo yet.

Renders the name as big bold lettering on a white square, in the same
grayscale "dark subject on white" format prep_photo.py outputs, so
make_ascii_svg.py turns it into the same self-typing monochrome ASCII panel.

    python scripts/make_name_banner.py            # writes source-prepped.png
    python scripts/make_ascii_svg.py              # writes akash-ascii.svg

When you have a photo, run prep_photo.py on it instead and this file is unused.
"""
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-prepped.png")
LINES = ["AKASH", "SONI"]
SIDE = 1200

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]
font_path = next((p for p in FONT_CANDIDATES if os.path.exists(p)), None)


def font(size):
    return ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()


img = Image.new("L", (SIDE, SIDE), 255)
d = ImageDraw.Draw(img)

# size each line to fill ~86% of the width, then stack them centred
boxes, fonts = [], []
for line in LINES:
    size = 400
    while d.textlength(line, font=font(size)) > SIDE * 0.86:
        size -= 8
    f = font(size)
    fonts.append(f)
    boxes.append(d.textbbox((0, 0), line, font=f))

gap = 70
total_h = sum(b[3] - b[1] for b in boxes) + gap * (len(LINES) - 1)
y = (SIDE - total_h) / 2
for line, f, b in zip(LINES, fonts, boxes):
    w, h = b[2] - b[0], b[3] - b[1]
    d.text(((SIDE - w) / 2 - b[0], y - b[1]), line, font=f, fill=0)
    y += h + gap

# stretch the lettering to fill the square (tall, poster-like letters read far
# better at ascii resolution than short wide ones)
x0, y0, x1, y1 = Image.eval(img, lambda v: 255 - v).getbbox()
m = int(SIDE * 0.06)
letters = img.crop((x0, y0, x1, y1)).resize((SIDE - 2 * m, SIDE - 2 * m), Image.LANCZOS)
img = Image.new("L", (SIDE, SIDE), 255)
img.paste(letters, (m, m))

# soft edges give the ascii ramp a gradient to work with at the letter borders
img = img.filter(ImageFilter.GaussianBlur(2))
img.save(OUT)
print("wrote", OUT, img.size)
