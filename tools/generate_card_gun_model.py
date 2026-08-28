"""Build Kid 1412's card gun on TaCZ's Rhino .357 skeleton.

The bone tree, pivots and the stock animation (tacz:rhino357) stay TaCZ's own,
so the gun draws, fires and reloads exactly like a first-party revolver.  All
visible geometry is replaced to match the reference prop:

  * a tall slab-sided silver box up front with one huge bore in its face
  * a large exposed drum (octagon body, hex end plates) right behind it
  * a stepped rear frame descending into a near-vertical ribbed black grip
  * an open silver trigger with a front spur instead of a closed guard

Model space: -Z is the muzzle, +Y is up.  The drum turns around y=9.5625 and
the bore sits at y=9.03 (the bottom chamber -- kept from the Rhino).

    python3 tools/generate_card_gun_model.py
"""

import json
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TACZ = ROOT / "run/tacz/tacz_default_gun/assets/tacz"
BASE = "rhino357"

OUT_MODEL = ROOT / "assets/kid1412/geo_models/gun/card_gun_geo.json"
OUT_LOD = ROOT / "assets/kid1412/geo_models/gun/lod/card_gun.json"
OUT_TEX = ROOT / "assets/kid1412/textures/gun/uv/card_gun.png"
OUT_TEX_S = ROOT / "assets/kid1412/textures/gun/uv/card_gun_s.png"
OUT_TEX_N = ROOT / "assets/kid1412/textures/gun/uv/card_gun_n.png"
OUT_LOD_TEX = ROOT / "assets/kid1412/textures/gun/lod/card_gun.png"
OUT_DISPLAY = ROOT / "assets/kid1412/display/guns/card_gun_display.json"

ATLAS = 256

# --- key dimensions, all in model units ------------------------------------
DRUM_Y = 9.5625          # cylinder axis, fixed by the skeleton
BORE_Y = 9.03            # fires from the bottom chamber, like the Rhino
MUZZLE_Z = -5.62
BOX_LEN = 5.60           # the front box is ~half the body length
BOX_BOT, BOX_TOP_Y = 7.05, 10.90
BOX_HALF_W = 1.02
DRUM_A = 1.00            # drum apothem (flat-to-flat 2.0, wider than the frame)
CHAMBER_RING = 0.55      # bottom chamber lines up with the bore
DRUM_Z0, DRUM_Z1 = 1.60, 3.72
GRIP_RAKE = 24.0
GRIP_PIVOT = [0, 8.0, 4.90]

# --------------------------------------------------------------------------
# palette
# --------------------------------------------------------------------------
INK = (26, 28, 33, 255)
GRIP_BLACK = (34, 36, 44, 255)
GRIP_DEEP = (20, 21, 27, 255)
STEEL_LO = (150, 156, 166, 255)
STEEL = (186, 192, 200, 255)
STEEL_HI = (218, 223, 230, 255)
WHITE_MET = (236, 239, 243, 255)
SHADOW = (108, 114, 124, 255)
CREAM = (243, 240, 231, 255)
CREAM_SHADE = (208, 203, 190, 255)
RED = (176, 34, 44, 255)
CLEAR = (0, 0, 0, 0)

# --- atlas layout (x, y, w, h) ---------------------------------------------
BOX_SIDE = (0, 0, 72, 48)
BOX_SIDE_L = (72, 0, 72, 48)
BOX_TOP = (144, 0, 56, 48)
BOX_UNDER = (200, 0, 56, 48)
BOX_FRONT = (0, 48, 36, 64)
DRUM_END = (36, 48, 64, 64)       # front face: cards in the chambers
DRUM_RATCHET = (100, 48, 64, 64)  # rear face: dark empty-looking chambers
GRIP_SIDE = (164, 48, 48, 64)
GRIP_BACK = (212, 48, 28, 64)
DRUM_FACET = (0, 120, 64, 32)
CARD_ROLL = (64, 120, 64, 32)
CARD_END = (128, 120, 32, 32)
MEDALLION = (160, 120, 32, 32)
MEDALLION_L = (192, 120, 32, 32)
BUTT = (224, 120, 32, 32)
PLATE = (0, 152, 48, 24)
PLATE_L = (48, 152, 48, 24)
FRAME_SIDE = (96, 152, 64, 32)
REAR_SIDE = (160, 152, 48, 32)

SWATCH_Y = 208
SWATCH_NAMES = ["steel", "steel_hi", "steel_lo", "white", "shadow", "grip",
                "grip_deep", "ink", "cream", "cream_shade", "red", "hidden"]
SWATCH_COLORS = [STEEL, STEEL_HI, STEEL_LO, WHITE_MET, SHADOW, GRIP_BLACK,
                 GRIP_DEEP, INK, CREAM, CREAM_SHADE, RED, CLEAR]


def sw(name):
    return (SWATCH_NAMES.index(name) * 16 + 2, SWATCH_Y + 2, 12, 12)


DIGITS = {
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
}


def digits(d, text, x, y, scale, color, gap=1):
    cx = x
    for ch in text:
        for j, row in enumerate(DIGITS[ch]):
            for i, bit in enumerate(row):
                if bit == "1":
                    d.rectangle([cx + i * scale, y + j * scale,
                                 cx + (i + 1) * scale - 1, y + (j + 1) * scale - 1],
                                fill=color)
        cx += (3 + gap) * scale


def spade(d, cx, cy, w, h, color):
    r = w * 0.29
    d.polygon([(cx, cy - h * 0.46), (cx + w * 0.5, cy + h * 0.06),
               (cx - w * 0.5, cy + h * 0.06)], fill=color)
    d.ellipse([cx - w * 0.5, cy - h * 0.10, cx - w * 0.5 + 2 * r, cy - h * 0.10 + 2 * r],
              fill=color)
    d.ellipse([cx + w * 0.5 - 2 * r, cy - h * 0.10, cx + w * 0.5, cy - h * 0.10 + 2 * r],
              fill=color)
    d.polygon([(cx - w * 0.20, cy + h * 0.46), (cx + w * 0.20, cy + h * 0.46),
               (cx + w * 0.07, cy + h * 0.10), (cx - w * 0.07, cy + h * 0.10)], fill=color)


def clamp(v):
    return 0 if v < 0 else 255 if v > 255 else int(v)


def brushed(img, rect, top, bottom, rng, streak=7):
    x, y, w, h = rect
    px = img.load()
    for j in range(h):
        t = j / max(1, h - 1)
        base = [top[k] + (bottom[k] - top[k]) * t for k in range(4)]
        line = rng.randint(-streak, streak)
        for i in range(w):
            n = line + rng.randint(-2, 2)
            px[x + i, y + j] = (clamp(base[0] + n), clamp(base[1] + n),
                                clamp(base[2] + n), clamp(base[3]))


def screws(d, rect, positions, r=2):
    x, y = rect[0], rect[1]
    for px, py in positions:
        d.ellipse([x + px - r, y + py - r, x + px + r, y + py + r],
                  fill=STEEL_LO, outline=INK)
        d.line([(x + px - r + 1, y + py), (x + px + r - 1, y + py)], fill=INK)


def build_atlas():
    rng = random.Random(1412)
    img = Image.new("RGBA", (ATLAS, ATLAS), CLEAR)
    d = ImageDraw.Draw(img)

    for i, color in enumerate(SWATCH_COLORS):
        d.rectangle([i * 16, SWATCH_Y, i * 16 + 15, SWATCH_Y + 15], fill=color)

    # --- box flank: low recessed slot, triangle mark, seams, screws ---------
    brushed(img, BOX_SIDE, STEEL_HI, STEEL, rng)
    x, y, w, h = BOX_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    d.rectangle([x + 2, y + 8, x + w - 3, y + 8], fill=STEEL_LO)           # top seam
    d.rectangle([x + 2, y + 9, x + w - 3, y + 9], fill=WHITE_MET)
    d.rectangle([x + w - 18, y + 2, x + w - 18, y + h - 3], fill=STEEL_LO)  # rear seam
    d.rectangle([x + 6, y + h - 13, x + w - 22, y + h - 8],                 # low slot
                fill=STEEL_LO, outline=SHADOW)
    d.rectangle([x + 8, y + h - 12, x + w - 24, y + h - 11], fill=(96, 102, 112, 255))
    d.polygon([(x + 24, y + 18), (x + 33, y + 34), (x + 15, y + 34)],       # triangle
              outline=SHADOW)
    screws(d, BOX_SIDE, [(6, 5), (w - 7, 5), (6, h - 6), (w - 7, h - 6),
                         (w - 24, h - 10), (8, h - 10)])

    # --- box top: rails and a raised rear plate -----------------------------
    brushed(img, BOX_TOP, WHITE_MET, STEEL_HI, rng, streak=4)
    x, y, w, h = BOX_TOP
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    for j in (8, 10, h - 11, h - 9):
        d.rectangle([x + 4, y + j, x + w - 5, y + j], fill=STEEL_LO)
    d.rectangle([x + 8, y + 16, x + w - 9, y + h - 17], outline=STEEL_LO)
    screws(d, BOX_TOP, [(w // 2, 12), (w // 2, h - 12)])

    brushed(img, BOX_UNDER, STEEL, SHADOW, rng)
    x, y, w, h = BOX_UNDER
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK)
    d.rectangle([x + 6, y + 18, x + w - 7, y + h - 19], fill=STEEL_LO, outline=SHADOW)

    # --- box front: one huge bore, four screws ------------------------------
    brushed(img, BOX_FRONT, STEEL_HI, STEEL, rng)
    x, y, w, h = BOX_FRONT
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK)
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], outline=STEEL_LO)
    # bore centre: y=BORE_Y on a face spanning BOX_BOT..BOX_TOP_Y
    cy = y + h * (BOX_TOP_Y - BORE_Y) / (BOX_TOP_Y - BOX_BOT)
    cx = x + w / 2
    rx = w * 0.34
    ry = rx * (h / (BOX_TOP_Y - BOX_BOT)) / (w / (BOX_HALF_W * 2))  # keep it round
    for rr, fill in ((1.30, STEEL_LO), (1.12, SHADOW), (1.0, (52, 54, 60, 255)),
                     (0.74, (16, 17, 21, 255))):
        d.ellipse([cx - rx * rr, cy - ry * rr, cx + rx * rr, cy + ry * rr],
                  fill=fill, outline=INK)
    d.ellipse([cx - rx * 0.62, cy - ry * 0.80, cx + rx * 0.10, cy - ry * 0.10],
              fill=(70, 74, 82, 255))
    d.ellipse([cx - rx * 0.55, cy - ry * 0.72, cx + rx * 0.05, cy - ry * 0.16],
              fill=(20, 21, 26, 255))
    screws(d, BOX_FRONT, [(5, 5), (w - 6, 5), (5, h - 6), (w - 6, h - 6)])

    # --- drum faces ---------------------------------------------------------
    def drum_face(rect, card_fill, hole_fill):
        # transparent corners: the square plate face renders as a disc
        fx, fy, fw, fh = rect
        ccx, ccy = fx + fw / 2, fy + fh / 2
        tile = Image.new("RGBA", (fw, fh), CLEAR)
        td = ImageDraw.Draw(tile)
        td.ellipse([1, 1, fw - 2, fh - 2], fill=STEEL, outline=SHADOW, width=2)
        td.ellipse([5, 5, fw - 6, fh - 6], outline=STEEL_LO)
        for k in range(6):
            a = math.radians(30 + k * 60)
            ex, ey = fw / 2 + 19 * math.cos(a), fh / 2 - 19 * math.sin(a)
            td.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=hole_fill, outline=INK)
            if card_fill:
                td.ellipse([ex - 7, ey - 7, ex + 7, ey + 7],
                           fill=card_fill, outline=CREAM_SHADE)
        td.ellipse([fw / 2 - 6, fh / 2 - 6, fw / 2 + 6, fh / 2 + 6],
                   fill=STEEL_LO, outline=INK)
        img.paste(tile, (fx, fy))

    drum_face(DRUM_END, CREAM, (46, 48, 54, 255))
    drum_face(DRUM_RATCHET, None, (30, 31, 37, 255))

    # --- drum flank: uniform flutes so all eight facets tile ---------------
    brushed(img, DRUM_FACET, STEEL_HI, STEEL, rng)
    x, y, w, h = DRUM_FACET
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    for j in (7, h - 8):
        d.rectangle([x + 4, y + j, x + w - 5, y + j], fill=STEEL_LO)
        d.rectangle([x + 4, y + j + 1, x + w - 5, y + j + 1], fill=WHITE_MET)

    # --- grip: horizontal ribs ---------------------------------------------
    brushed(img, GRIP_SIDE, GRIP_BLACK, GRIP_DEEP, rng, streak=3)
    x, y, w, h = GRIP_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=(10, 11, 14, 255))
    for j in range(10, h - 8, 7):
        d.rectangle([x + 5, y + j, x + w - 6, y + j + 1], fill=(12, 13, 17, 255))
        d.rectangle([x + 5, y + j + 2, x + w - 6, y + j + 2], fill=(58, 61, 70, 255))
    d.ellipse([x + w / 2 - 3, y + 4, x + w / 2 + 3, y + 10], fill=STEEL_LO, outline=INK)

    brushed(img, GRIP_BACK, GRIP_BLACK, GRIP_DEEP, rng, streak=3)
    d.rectangle([GRIP_BACK[0], GRIP_BACK[1], GRIP_BACK[0] + GRIP_BACK[2] - 1,
                 GRIP_BACK[1] + GRIP_BACK[3] - 1], outline=(10, 11, 14, 255))

    brushed(img, BUTT, STEEL_HI, STEEL, rng)
    d.rectangle([BUTT[0], BUTT[1], BUTT[0] + BUTT[2] - 1, BUTT[1] + BUTT[3] - 1],
                outline=SHADOW)
    d.rectangle([BUTT[0] + 6, BUTT[1] + 10, BUTT[0] + BUTT[2] - 7,
                 BUTT[1] + BUTT[3] - 11], outline=STEEL_LO)

    # --- cards --------------------------------------------------------------
    x, y, w, h = CARD_ROLL
    for j in range(h):
        t = abs(j / (h - 1) - 0.5) * 2
        v = [int(CREAM[k] - (CREAM[k] - CREAM_SHADE[k]) * (t ** 1.4)) for k in range(3)]
        d.rectangle([x, y + j, x + w - 1, y + j], fill=tuple(v) + (255,))
    d.rectangle([x, y + h // 2 - 1, x + w - 1, y + h // 2], fill=RED)
    for cx2 in (14, 34, 54):
        spade(d, x + cx2, y + h * 0.5, 9, 12, INK)

    x, y, w, h = CARD_END
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=INK)
    for k, r in enumerate((14, 10, 6, 3)):
        d.ellipse([x + w / 2 - r, y + h / 2 - r, x + w / 2 + r, y + h / 2 + r],
                  fill=CREAM if k % 2 == 0 else CREAM_SHADE, outline=CREAM_SHADE)

    # --- marks and small plates ---------------------------------------------
    brushed(img, PLATE, STEEL_HI, STEEL, rng)
    d.rectangle([PLATE[0], PLATE[1], PLATE[0] + PLATE[2] - 1, PLATE[1] + PLATE[3] - 1],
                outline=SHADOW)
    digits(d, "1412", PLATE[0] + 8, PLATE[1] + 6, 2, (74, 78, 86, 255))
    d.rectangle([PLATE[0] + 6, PLATE[1] + 18, PLATE[0] + PLATE[2] - 7, PLATE[1] + 18],
                fill=SHADOW)

    x, y, w, h = MEDALLION
    d.ellipse([x + 1, y + 1, x + w - 2, y + h - 2], fill=STEEL_HI, outline=SHADOW)
    d.ellipse([x + 6, y + 6, x + w - 7, y + h - 7], outline=(62, 66, 74, 255), width=2)
    d.ellipse([x + 10, y + 10, x + w - 11, y + h - 11], outline=STEEL_LO)
    for k in range(3):
        dx, dy = x + w * 0.70 + k * 3, y + h * 0.70 + k * 3
        d.ellipse([dx - 1, dy - 1, dx + 1, dy + 1], fill=(62, 66, 74, 255))

    brushed(img, FRAME_SIDE, STEEL, STEEL_LO, rng)
    x, y, w, h = FRAME_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    d.rectangle([x + 3, y + 5, x + w - 4, y + h - 6], outline=STEEL_LO)
    screws(d, FRAME_SIDE, [(8, 8), (w - 9, h - 9)])

    brushed(img, REAR_SIDE, STEEL, STEEL_LO, rng)
    x, y, w, h = REAR_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    for j in range(4, h - 4, 5):
        d.rectangle([x + 3, y + j, x + w - 4, y + j], fill=STEEL_LO)

    # mirrored twins so marks read correctly on the -X flank
    for src, dst in ((PLATE, PLATE_L), (MEDALLION, MEDALLION_L),
                     (BOX_SIDE, BOX_SIDE_L)):
        patch = img.crop((src[0], src[1], src[0] + src[2], src[1] + src[3]))
        img.paste(patch.transpose(Image.FLIP_LEFT_RIGHT), (dst[0], dst[1]))
    return img


def build_specular(atlas):
    spec = Image.new("RGBA", atlas.size, (168, 168, 168, 255))
    d = ImageDraw.Draw(spec)

    def fill(rect, v):
        d.rectangle([rect[0], rect[1], rect[0] + rect[2] - 1, rect[1] + rect[3] - 1],
                    fill=(v, v, v, 255))

    for rect in (BOX_SIDE, BOX_SIDE_L, BOX_TOP, BOX_FRONT, FRAME_SIDE, REAR_SIDE,
                 DRUM_END, DRUM_RATCHET, DRUM_FACET, BUTT, PLATE, PLATE_L,
                 MEDALLION, MEDALLION_L):
        fill(rect, 225)
    fill(BOX_UNDER, 150)
    for rect in (GRIP_SIDE, GRIP_BACK):
        fill(rect, 55)
    for rect in (CARD_ROLL, CARD_END):
        fill(rect, 40)
    spec.putalpha(atlas.getchannel("A"))
    return spec


# --------------------------------------------------------------------------
# geometry helpers
# --------------------------------------------------------------------------
FACES = ("north", "south", "east", "west", "up", "down")
HIDDEN = sw("hidden")


def cube(origin, size, faces, rotation=None, pivot=None):
    if isinstance(faces, tuple):
        faces = {"all": faces}
    uv = {}
    for name in FACES:
        r = faces.get(name, faces.get("all", sw("steel")))
        uv[name] = {"uv": [r[0], r[1]], "uv_size": [r[2], r[3]]}
    out = {"origin": [round(v, 4) for v in origin],
           "size": [round(v, 4) for v in size], "uv": uv}
    if rotation is not None:
        out["rotation"] = [round(v, 4) for v in rotation]
        out["pivot"] = [round(v, 4) for v in (pivot or origin)]
    return out


BOX = {"all": sw("steel"), "east": BOX_SIDE, "west": BOX_SIDE_L,
       "up": BOX_TOP, "down": BOX_UNDER, "north": BOX_FRONT, "south": sw("steel_lo")}
GRIP = {"all": sw("grip"), "east": GRIP_SIDE, "west": GRIP_SIDE,
        "south": GRIP_BACK, "north": GRIP_BACK, "down": BUTT, "up": sw("grip_deep")}
CARD = {"all": CARD_ROLL, "north": CARD_END, "south": CARD_END}


def barrel_cubes():
    """The tall front box with the huge bore."""
    return [
        cube([-BOX_HALF_W, BOX_BOT, MUZZLE_Z], [BOX_HALF_W * 2,
             BOX_TOP_Y - BOX_BOT, BOX_LEN], BOX),
        # raised plate on the top rear of the box
        cube([-0.80, BOX_TOP_Y, MUZZLE_Z + 3.0], [1.60, 0.28, 2.40],
             {"all": sw("steel_hi"), "up": BOX_TOP,
              "east": sw("steel"), "west": sw("steel")}),
        # front sight tab
        cube([-0.16, BOX_TOP_Y, MUZZLE_Z + 4.35], [0.32, 0.48, 0.34],
             {"all": sw("steel_lo"), "south": sw("shadow")}),
    ]


def gun_body_cubes():
    """Joint block, top strap, stepped rear frame, open trigger spur."""
    return [
        # short joint between box and drum
        cube([-0.67, 7.85, BOX_LEN + MUZZLE_Z - 0.02], [1.34, 2.95, 0.95],
             {"all": sw("steel"), "east": FRAME_SIDE, "west": FRAME_SIDE,
              "up": BOX_TOP, "down": BOX_UNDER}),
        # top strap over the drum into the rear
        cube([-0.55, 10.58, -0.10], [1.10, 0.40, 4.60],
             {"all": sw("steel"), "up": BOX_TOP}),
        # rear sight notch block at the strap's end
        cube([-0.36, 10.98, 4.02], [0.72, 0.26, 0.44], {"all": sw("steel_lo")}),
        # stepped rear frame descending into the grip
        cube([-0.66, 8.10, 3.80], [1.32, 2.62, 0.75],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE}),
        cube([-0.62, 8.10, 4.55], [1.24, 1.95, 0.65],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE}),
        cube([-0.58, 8.10, 5.20], [1.16, 1.25, 0.55],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE}),
        # frame floor under the drum, box bottom stays the lowest line
        cube([-0.56, 7.62, -0.05], [1.12, 0.50, 4.40],
             {"all": sw("steel_lo"), "down": BOX_UNDER}),
        # 1412 plates on the rear step
        cube([0.640, 8.85, 3.92], [0.045, 0.52, 1.05],
             {"all": sw("steel_hi"), "east": PLATE}),
        cube([-0.685, 8.85, 3.92], [0.045, 0.52, 1.05],
             {"all": sw("steel_hi"), "west": PLATE_L}),
        # open trigger guard: front post and a short lip, no closed loop
        cube([-0.30, 6.72, 1.62], [0.60, 0.95, 0.30], {"all": sw("steel_lo")}),
        cube([-0.30, 6.72, 1.62], [0.60, 0.26, 1.55], {"all": sw("steel_lo")}),
    ]


def drum_cubes():
    """Octagonal drum body; each end capped by one alpha-cutout disc plate."""
    s = 2 * DRUM_A * math.tan(math.radians(22.5))
    facet = {"all": sw("steel"), "east": DRUM_FACET, "west": DRUM_FACET,
             "up": sw("steel"), "down": sw("steel"),
             "north": sw("steel_lo"), "south": sw("steel_lo")}
    out = []
    for k in range(4):
        out.append(cube([-DRUM_A, DRUM_Y - s / 2, DRUM_Z0], [DRUM_A * 2, s,
                        DRUM_Z1 - DRUM_Z0], facet,
                        rotation=[0, 0, 45 * k], pivot=[0, DRUM_Y, (DRUM_Z0 + DRUM_Z1) / 2]))
    plate_r = 0.96
    out.append(cube([-plate_r, DRUM_Y - plate_r, DRUM_Z0 - 0.16],
                    [plate_r * 2, plate_r * 2, 0.17],
                    {"all": HIDDEN, "north": DRUM_END}))
    out.append(cube([-plate_r, DRUM_Y - plate_r, DRUM_Z1 - 0.01],
                    [plate_r * 2, plate_r * 2, 0.17],
                    {"all": HIDDEN, "south": DRUM_RATCHET}))
    return out


CHAMBERS = {"round7": 210, "round8": 150, "round9": 90,
            "round10": 30, "round11": 330, "round12": 270}
CHAMBER_TIPS = {"bone4": 210, "bone2": 150, "bone6": 90,
                "bone7": 30, "bone8": 330, "bone9": 270}


def chamber_card(angle, z0, length):
    a = math.radians(angle)
    cx, cy = CHAMBER_RING * math.cos(a), DRUM_Y + CHAMBER_RING * math.sin(a)
    return cube([cx - 0.17, cy - 0.17, z0], [0.34, 0.34, length], CARD)


def grip_cubes():
    rake = dict(rotation=[GRIP_RAKE, 0, 0], pivot=GRIP_PIVOT)
    return [
        # silver wedge tying the grip into the rear frame
        cube([-0.64, 7.30, 4.30], [1.28, 1.30, 2.15],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE,
              "up": BOX_TOP}, **rake),
        cube([-0.60, 3.35, 4.42], [1.20, 4.10, 2.00], GRIP, **rake),
        cube([-0.58, 3.45, 6.38], [1.16, 3.90, 0.28],
             {"all": sw("grip"), "south": GRIP_BACK}, **rake),
        cube([-0.64, 3.05, 4.38], [1.28, 0.32, 2.12],
             {"all": sw("steel"), "down": BUTT}, **rake),
        cube([0.598, 4.95, 5.00], [0.04, 0.72, 0.72],
             {"all": sw("steel_hi"), "east": MEDALLION}, **rake),
        cube([-0.638, 4.95, 5.00], [0.04, 0.72, 0.72],
             {"all": sw("steel_hi"), "west": MEDALLION_L}, **rake),
    ]


def loader_cards():
    out = []
    for k in range(6):
        a = math.radians(30 + k * 60)
        cx, cy = 0.55 * math.cos(a), 9.79 + 0.55 * math.sin(a)
        out.append(cube([cx - 0.17, cy - 0.17, 2.30], [0.34, 0.34, 1.30], CARD))
    return out


NEW_CUBES = {
    "barrel": barrel_cubes,
    "gun_body": gun_body_cubes,
    "bone5": drum_cubes,
    "grip": grip_cubes,
    "hammer": lambda: [
        cube([-0.15, 10.35, 4.55], [0.30, 0.90, 0.40], {"all": sw("steel_lo")}),
        cube([-0.21, 11.10, 4.65], [0.42, 0.26, 0.72], {"all": sw("steel_hi")}),
    ],
    "trigger": lambda: [
        cube([-0.12, 6.95, 2.55], [0.24, 1.35, 0.40], {"all": sw("steel_hi")},
             rotation=[10, 0, 0], pivot=[0, 8.35, 2.73]),
    ],
    "crane": lambda: [
        cube([-0.80, 8.90, 0.90], [0.22, 0.50, 1.40],
             {"all": sw("steel"), "up": sw("steel_hi"), "down": sw("shadow")}),
    ],
    "ejector": lambda: [
        cube([-0.10, DRUM_Y - 0.10, -0.30], [0.20, 0.20, 2.05], {"all": sw("steel_lo")}),
    ],
    "bone11": lambda: [
        cube([-0.34, DRUM_Y - 0.17, 3.90], [0.68, 0.34, 0.16], {"all": sw("steel_lo")}),
    ],
    "cylinder_release": lambda: [
        cube([-0.84, 9.62, 4.10], [0.16, 0.44, 0.85], {"all": sw("steel_hi")}),
    ],
    "bone": lambda: [],
    "speed_loader": lambda: [
        cube([-0.58, 9.21, 3.58], [1.16, 1.16, 0.30],
             {"all": sw("steel_lo"), "north": DRUM_END, "south": DRUM_RATCHET}),
    ],
}
CLEARED = ["rear_sight", "rear_sight_illuminated", "sight_illuminated"]


def build_geometry():
    model = json.loads((TACZ / f"geo_models/gun/{BASE}_geo.json").read_text())
    geometry = model["minecraft:geometry"][0]
    geometry["description"].update({
        "identifier": "geometry.kid1412.card_gun",
        "texture_width": ATLAS, "texture_height": ATLAS,
    })
    bones = {b["name"]: b for b in geometry["bones"]}

    for name, cubes in NEW_CUBES.items():
        bones[name]["cubes"] = cubes()
    for name in CLEARED:
        bones[name]["cubes"] = []
    for name, angle in CHAMBERS.items():
        bones[name]["cubes"] = [chamber_card(angle, DRUM_Z0 + 0.06, 2.00)]
    for name, angle in CHAMBER_TIPS.items():
        # card faces sitting proud on the front plate, ejected by the reload
        bones[name]["cubes"] = [chamber_card(angle, DRUM_Z0 - 0.22, 0.07)]
    for name, card in zip(("round1", "round2", "round3", "round4", "round5", "round6"),
                          loader_cards()):
        bones[name]["cubes"] = [card]
    for name in ("lefthand_pos", "righthand_pos"):
        for c in bones[name]["cubes"]:
            c["uv"] = {f: {"uv": [HIDDEN[0], HIDDEN[1]],
                           "uv_size": [HIDDEN[2], HIDDEN[3]]} for f in FACES}
            c.pop("inflate", None)
    # the front sight tab is taller than the Rhino's; lift the aim line over it
    bones["iron_view"]["pivot"][1] = 11.42
    return model


def build_lod():
    def bone(name, pivot, parent=None, cubes=None, rotation=None):
        out = {"name": name, "pivot": pivot}
        if parent:
            out["parent"] = parent
        if rotation:
            out["rotation"] = rotation
        out["cubes"] = cubes or []
        return out

    bones = [
        bone("root", [0, 0, 0]),
        bone("frame", [0, BORE_Y, 0], "root", [
            cube([-BOX_HALF_W, BOX_BOT, MUZZLE_Z],
                 [BOX_HALF_W * 2, BOX_TOP_Y - BOX_BOT, BOX_LEN], BOX),
            cube([-0.66, 7.85, BOX_LEN + MUZZLE_Z], [1.32, 3.10, 5.80],
                 {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE,
                  "up": BOX_TOP}),
        ]),
        bone("cylinder", [0, DRUM_Y, (DRUM_Z0 + DRUM_Z1) / 2], "root", [
            cube([-DRUM_A, DRUM_Y - DRUM_A, DRUM_Z0 - 0.15],
                 [DRUM_A * 2, DRUM_A * 2, DRUM_Z1 - DRUM_Z0 + 0.3],
                 {"all": sw("steel"), "north": DRUM_END, "south": DRUM_RATCHET,
                  "east": DRUM_FACET, "west": DRUM_FACET,
                  "up": DRUM_FACET, "down": DRUM_FACET}),
        ]),
        bone("grip", GRIP_PIVOT, "root", [
            cube([-0.62, 3.05, 4.35], [1.24, 4.45, 2.10], GRIP,
                 rotation=[GRIP_RAKE, 0, 0], pivot=GRIP_PIVOT),
        ]),
        bone("muzzle", [0, BORE_Y, MUZZLE_Z], "root"),
        bone("lefthand", [-6, 19, 0], "root"),
        bone("righthand", [6, 19.2794, -0.3694], "root"),
    ]
    return {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.kid1412.card_gun_lod",
                        "texture_width": ATLAS, "texture_height": ATLAS,
                        "visible_bounds_width": 4, "visible_bounds_height": 3,
                        "visible_bounds_offset": [0, 0.25, -0.35]},
        "bones": bones}]}


def build_display():
    display = json.loads((TACZ / f"display/guns/{BASE}_display.json").read_text())
    display["model"] = "kid1412:gun/card_gun_geo"
    display["texture"] = "kid1412:gun/uv/card_gun"
    display["lod"] = {"model": "kid1412:gun/lod/card_gun",
                      "texture": "kid1412:gun/lod/card_gun"}
    display["slot"] = "kid1412:gun/slot/card_gun"
    display["hud"] = "kid1412:gun/hud/card_gun"
    display.pop("shell", None)
    display["muzzle_flash"] = {"texture": "tacz:flash/common_muzzle_flash", "scale": 0.12}
    display["sounds"].update({
        "shoot": "tacz:deagle/deagle_silence",
        "shoot_3p": "tacz:deagle/deagle_silence_3p",
        "dry_fire": "tacz:dry_fire",
    })
    return display


def main():
    if not TACZ.is_dir():
        sys.exit(f"[error] TaCZ default gun pack not found at {TACZ}. Run the client once.")

    for path in (OUT_MODEL, OUT_LOD, OUT_TEX, OUT_LOD_TEX, OUT_DISPLAY):
        path.parent.mkdir(parents=True, exist_ok=True)

    OUT_MODEL.write_text(json.dumps(build_geometry(), ensure_ascii=False, indent=2) + "\n")
    OUT_LOD.write_text(json.dumps(build_lod(), ensure_ascii=False, indent=2) + "\n")
    OUT_DISPLAY.write_text(json.dumps(build_display(), ensure_ascii=False, indent=2) + "\n")

    atlas = build_atlas()
    atlas.save(OUT_TEX)
    build_specular(atlas).save(OUT_TEX_S)
    Image.new("RGBA", atlas.size, (128, 128, 255, 255)).save(OUT_TEX_N)
    atlas.save(OUT_LOD_TEX)

    print(f"model {OUT_MODEL.relative_to(ROOT)}")
    print(f"lod   {OUT_LOD.relative_to(ROOT)}")
    print(f"disp  {OUT_DISPLAY.relative_to(ROOT)}")
    print(f"uv    {OUT_TEX.relative_to(ROOT)} {atlas.size}")


if __name__ == "__main__":
    main()
