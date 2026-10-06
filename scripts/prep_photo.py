"""
Prepare a portrait PHOTO for clean ASCII conversion:
  1. remove the background (rembg, isnet-general-use) so the subject is isolated.
     isnet keeps a cast wall shadow out of the mask, which the u2net models
     tend to swallow as part of the person.
  2. boost local contrast with OpenCV CLAHE, so a flatly lit face gets real
     highlights and shadows instead of turning into one dark blob
  3. light tone stretch over the subject only
  4. composite onto pure white (white -> spaces in the ascii ramp) and crop a
     square head and shoulders frame

Output: source-prepped.png (grayscale), consumed by make_ascii_svg.py.

    python scripts/prep_photo.py <input photo> [output.png]
"""
import os
import sys

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

HERE = os.path.dirname(os.path.abspath(__file__))
INP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "source-photo.png")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "..", "source-prepped.png")
MODEL = os.environ.get("REMBG_MODEL", "isnet-general-use")

CLAHE_CLIP = 2.6       # higher = punchier local contrast
CLAHE_GRID = 8
FRAME_BOTTOM = 0.86    # keep this fraction of the subject's height (trims the torso)
TOP_MARGIN = 0.05      # headroom above the hair, as a fraction of the frame

# 1. cut out the subject
cut = remove(Image.open(INP).convert("RGBA"), session=new_session(MODEL))
rgb = np.array(cut.convert("RGB"))
alpha = np.array(cut.split()[-1])                 # 0 = background
gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

# 2. local contrast
clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP, tileGridSize=(CLAHE_GRID, CLAHE_GRID))
eq = clahe.apply(cv2.bilateralFilter(gray, 7, 30, 7))

# 3. tone stretch over the subject only
lo, hi = np.percentile(eq[alpha > 128], [2, 97])
out = np.clip((eq.astype(np.float32) - lo) / (hi - lo), 0, 1) * 255

# 4. paste onto white (feathered a hair to avoid a halo), square crop
mask = cv2.GaussianBlur(alpha.astype(np.float32) / 255.0, (0, 0), 1.0)
out = out * mask + 255.0 * (1.0 - mask)

ys, xs = np.where(alpha > 20)
top, bot = ys.min(), ys.min() + int((ys.max() - ys.min()) * FRAME_BOTTOM)
side = bot - top
y0 = int(top - side * TOP_MARGIN)
side = bot - y0
cx = (xs.min() + xs.max()) // 2
x0 = cx - side // 2
canvas = np.full((side, side), 255, np.uint8)
sx0, sy0 = max(x0, 0), max(y0, 0)
sx1, sy1 = min(x0 + side, out.shape[1]), min(y0 + side, out.shape[0])
canvas[sy0 - y0:sy1 - y0, sx0 - x0:sx1 - x0] = out[sy0:sy1, sx0:sx1].astype(np.uint8)

Image.fromarray(canvas, mode="L").save(OUT)
print("wrote", OUT, canvas.shape)
