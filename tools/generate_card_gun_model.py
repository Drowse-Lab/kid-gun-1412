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
OUT_ANIM = ROOT / "assets/kid1412/animations/card_gun.animation.json"

ATLAS_W, ATLAS_H = 256, 320

# --- key dimensions, all in model units ------------------------------------
DRUM_Y = 9.5625          # cylinder axis, fixed by the skeleton
CHAMBER_R = 0.5313       # exact chamber ring radius of the rhino skeleton
BORE_Y = 9.5625 - 0.5313  # bottom chamber: lands on the box centreline
MUZZLE_Z = -4.70
BOX_LEN = 4.68           # 39.5% of overall length, per the manual
BOX_BOT, BOX_TOP_Y = 7.42, 10.72
BOX_HALF_W = 1.45
DRUM_A = 1.00            # 0.47x the box height, per the manual
DRUM_Z0, DRUM_Z1 = 1.55, 3.32
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
NAVY_BACK = (34, 46, 92, 255)
CLEAR = (0, 0, 0, 0)

# --- atlas layout (x, y, w, h) ---------------------------------------------
BOX_SIDE = (0, 0, 72, 48)
BOX_SIDE_L = (72, 0, 72, 48)
BOX_TOP = (144, 0, 56, 48)
BOX_UNDER = (200, 0, 56, 48)
BOX_FRONT = (0, 48, 36, 64)
DRUM_END = (36, 48, 64, 64)       # front face: cards in the chambers
FRONT_FACE = (100, 48, 64, 64)    # flat muzzle plate: ring + vertical slot
FRONT_L = (100, 48, 30, 64)       # left half, up to the slot
FRONT_R = (134, 48, 30, 64)       # right half, past the slot
GRIP_SIDE = (164, 48, 48, 64)
GRIP_BACK = (212, 48, 28, 64)
DRUM_FACET = (0, 120, 64, 32)
CARD_ROLL = (64, 120, 64, 32)
CARD_END = (128, 120, 32, 32)
CARD_FACE = (0, 224, 44, 64)
CARD_FACE_L = (44, 224, 44, 64)
CARD_BACK = (88, 224, 44, 64)
MEDALLION = (160, 120, 32, 32)
MEDALLION_L = (192, 120, 32, 32)
BUTT = (224, 120, 32, 32)
MUZZLE_DISC = (208, 152, 32, 32)
BOX_SIDE_F = (0, 0, 20, 48)         # front slice of the box flank (+X side)
BOX_SIDE_F_L = (124, 0, 20, 48)     # matching slice of the mirrored flank
BOX_BAND = (0, 184, 72, 16)
BOX_BAND_L = (72, 184, 72, 16)
PLATE = (0, 152, 48, 24)
PLATE_L = (48, 152, 48, 24)
FRAME_SIDE = (96, 152, 64, 32)
REAR_SIDE = (160, 152, 48, 32)

SWATCH_Y = 208
SWATCH_NAMES = ["steel", "steel_hi", "steel_lo", "white", "shadow", "grip",
                "grip_deep", "ink", "cream", "cream_shade", "red", "hidden", "bore"]
SWATCH_COLORS = [STEEL, STEEL_HI, STEEL_LO, WHITE_MET, SHADOW, GRIP_BLACK,
                 GRIP_DEEP, INK, CREAM, CREAM_SHADE, RED, CLEAR, (20, 21, 26, 255)]


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
    img = Image.new("RGBA", (ATLAS_W, ATLAS_H), CLEAR)
    d = ImageDraw.Draw(img)

    for i, color in enumerate(SWATCH_COLORS):
        d.rectangle([i * 16, SWATCH_Y, i * 16 + 15, SWATCH_Y + 15], fill=color)

    # --- box flank: plain brushed alloy, clover-in-triangle mark ------------
    brushed(img, BOX_SIDE, STEEL_HI, STEEL, rng)
    x, y, w, h = BOX_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    d.rectangle([x + w - 18, y + 3, x + w - 18, y + h - 9], fill=STEEL_LO)   # rear seam
    d.rectangle([x + 2, y + h - 8, x + w - 3, y + h - 8], fill=STEEL_LO)     # band seam
    # engraved triangle with the four leaf clover inside it
    tri = [(x + 16, y + 9), (x + 27, y + 29), (x + 5, y + 29)]
    d.polygon(tri, outline=SHADOW)
    d.polygon([(x + 16, y + 12), (x + 25, y + 28), (x + 7, y + 28)], outline=STEEL_LO)
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3)):
        d.ellipse([x + 16 + dx - 3, y + 23 + dy - 3, x + 16 + dx + 3, y + 23 + dy + 3],
                  fill=STEEL_LO, outline=SHADOW)
    screws(d, BOX_SIDE, [(6, 8), (w - 7, 8), (6, h - 13), (w - 7, h - 13)])

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

    # --- box front: narrow nose face; the bore ring itself is geometry ------
    brushed(img, BOX_FRONT, STEEL_HI, STEEL, rng)
    x, y, w, h = BOX_FRONT
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK)
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], outline=STEEL_LO)
    d.ellipse([x + w // 2 - 4, y + h - 18, x + w // 2 + 4, y + h - 10],
              outline=SHADOW)                                # small circle detail
    screws(d, BOX_FRONT, [(5, 5), (w - 6, 5), (5, h - 6), (w - 6, h - 6)])

    # --- protruding muzzle ring face: alpha disc, dark recessed centre ------
    x, y, w, h = MUZZLE_DISC
    tile = Image.new("RGBA", (w, h), CLEAR)
    td = ImageDraw.Draw(tile)
    td.ellipse([0, 0, w - 1, h - 1], fill=STEEL_HI, outline=SHADOW)
    td.ellipse([3, 3, w - 4, h - 4], fill=STEEL_LO, outline=SHADOW)
    td.ellipse([6, 6, w - 7, h - 7], fill=(38, 40, 46, 255), outline=INK)
    td.ellipse([9, 9, w - 10, h - 10], fill=(14, 15, 19, 255))
    td.ellipse([10, 9, 20, 16], fill=(52, 55, 62, 255))
    td.ellipse([11, 10, 19, 15], fill=(18, 19, 24, 255))
    img.paste(tile, (x, y))

    # --- bottom band: brushed with the latched hatch ------------------------
    brushed(img, BOX_BAND, STEEL, STEEL_LO, rng)
    x, y, w, h = BOX_BAND
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    d.rectangle([x + 26, y + 3, x + 52, y + h - 3], fill=STEEL_LO, outline=SHADOW)
    d.rectangle([x + 29, y + 5, x + 40, y + 7], fill=WHITE_MET, outline=SHADOW)
    d.rectangle([x + 33, y + 9, x + 49, y + h - 4], fill=STEEL_HI, outline=SHADOW)
    screws(d, BOX_BAND, [(8, h // 2), (w - 9, h // 2)])

    # --- drum faces ---------------------------------------------------------
    def drum_face(rect, card_fill, hole_fill, ring_frac=0.44, hole_frac=0.17):
        # transparent corners: the square plate face renders as a disc
        fx, fy, fw, fh = rect
        ccx, ccy = fx + fw / 2, fy + fh / 2
        tile = Image.new("RGBA", (fw, fh), CLEAR)
        td = ImageDraw.Draw(tile)
        td.ellipse([1, 1, fw - 2, fh - 2], fill=STEEL, outline=SHADOW, width=2)
        td.ellipse([5, 5, fw - 6, fh - 6], outline=STEEL_LO)
        rr = fw / 2 * ring_frac                      # matches the modelled chambers
        hr = fw / 2 * hole_frac
        for k in range(6):
            a = math.radians(30 + k * 60)
            ex, ey = fw / 2 + rr * math.cos(a), fh / 2 - rr * math.sin(a)
            td.ellipse([ex - hr, ey - hr, ex + hr, ey + hr], fill=hole_fill, outline=INK)
            if card_fill:
                td.ellipse([ex - hr * 0.75, ey - hr * 0.75, ex + hr * 0.75, ey + hr * 0.75],
                           fill=card_fill, outline=CREAM_SHADE)
        td.ellipse([fw / 2 - 6, fh / 2 - 6, fw / 2 + 6, fh / 2 + 6],
                   fill=STEEL_LO, outline=INK)
        img.paste(tile, (fx, fy))

    drum_face(DRUM_END, CREAM, (46, 48, 54, 255))

    # --- flat muzzle plate: engraved ring, the card slot straight through it
    x, y, w, h = FRONT_FACE
    brushed(img, FRONT_FACE, STEEL_HI, STEEL, rng)
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    for cx0, cy0, cx1, cy1 in ((x, y, x + 8, y + 8), (x + w - 9, y, x + w - 1, y + 8),
                               (x, y + h - 9, x + 8, y + h - 1),
                               (x + w - 9, y + h - 9, x + w - 1, y + h - 1)):
        d.line([(cx0, cy1), (cx1, cy0)], fill=STEEL_LO)          # chamfered corners
    ccx, ccy = x + w // 2, y + 30
    for r, col in ((21, SHADOW), (19, STEEL_LO), (16, WHITE_MET)):
        d.ellipse([ccx - r, ccy - r, ccx + r, ccy + r], outline=col)
    d.rectangle([ccx - 2, y + 3, ccx + 2, y + h - 4], fill=(24, 25, 30, 255))  # slot
    d.rectangle([ccx - 1, y + 3, ccx - 1, y + h - 4], fill=(60, 63, 70, 255))
    d.polygon([(x + 52, y + 44), (x + 58, y + 54), (x + 46, y + 54)], outline=SHADOW)
    d.rectangle([x + 8, y + 48, x + 12, y + 56], outline=STEEL_LO)             # hook
    d.rectangle([x + 8, y + 48, x + 15, y + 50], outline=STEEL_LO)
    screws(d, FRONT_FACE, [(6, 14), (w - 7, 14), (6, h - 15), (w - 7, h - 15)])

    # --- drum flank: smooth metal with one ring seam midway ----------------
    brushed(img, DRUM_FACET, STEEL_HI, STEEL, rng, streak=3)
    x, y, w, h = DRUM_FACET
    d.rectangle([x + w // 2 - 1, y, x + w // 2 - 1, y + h - 1], fill=STEEL_LO)
    d.rectangle([x + w // 2, y, x + w // 2, y + h - 1], fill=WHITE_MET)
    d.rectangle([x + 2, y, x + 2, y + h - 1], fill=SHADOW)
    d.rectangle([x + w - 3, y, x + w - 3, y + h - 1], fill=SHADOW)

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

    # --- full card faces for the reload fan ---------------------------------
    x, y, w, h = CARD_FACE
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=INK)
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], fill=CREAM)
    d.rectangle([x + 4, y + 4, x + w - 5, y + h - 5], outline=CREAM_SHADE)
    spade(d, x + w / 2, y + h / 2, w * 0.46, h * 0.34, INK)
    spade(d, x + 8, y + 10, 7, 9, INK)
    spade(d, x + w - 9, y + h - 11, 7, 9, INK)
    x, y, w, h = CARD_BACK
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=INK)
    back = Image.new("RGBA", (w - 4, h - 4), NAVY_BACK)
    bd = ImageDraw.Draw(back)
    for j in range(-h, h * 2, 7):                     # harlequin diamonds
        bd.line([(0, j), (w - 4, j + h)], fill=(58, 76, 128, 255), width=2)
        bd.line([(w - 4, j), (0, j + h)], fill=(58, 76, 128, 255), width=2)
    img.paste(back, (x + 2, y + 2))
    d.rectangle([x + 4, y + 4, x + w - 5, y + h - 5], outline=CREAM)

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

    # --- rear frame plate: the prop's fan of radiating ribs -----------------
    brushed(img, REAR_SIDE, STEEL_HI, STEEL, rng)
    x, y, w, h = REAR_SIDE
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=SHADOW)
    hub = (x + w - 6, y + 4)
    for k in range(6):
        a = math.radians(118 + k * 13)
        ex, ey = hub[0] + 40 * math.cos(a), hub[1] - 40 * math.sin(a)
        mx, my = hub[0] + 12 * math.cos(a), hub[1] - 12 * math.sin(a)
        d.line([(mx, my), (ex, ey)], fill=SHADOW, width=2)
        d.line([(mx + 1, my + 1), (ex + 1, ey + 1)], fill=WHITE_MET)
    d.rectangle([x + 2, y + 2, x + w - 3, y + h - 3], outline=STEEL_LO)
    screws(d, REAR_SIDE, [(8, h - 8)])
    # small oval button
    d.ellipse([x + 10, y + 5, x + 20, y + 10], fill=STEEL_LO, outline=SHADOW)

    # mirrored twins so marks read correctly on the -X flank
    for src, dst in ((PLATE, PLATE_L), (MEDALLION, MEDALLION_L),
                     (BOX_SIDE, BOX_SIDE_L), (BOX_BAND, BOX_BAND_L),
                     (CARD_FACE, CARD_FACE_L)):
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
                 DRUM_END, FRONT_FACE, DRUM_FACET, BUTT, PLATE, PLATE_L,
                 MEDALLION, MEDALLION_L, MUZZLE_DISC, BOX_BAND, BOX_BAND_L):
        fill(rect, 225)
    fill(BOX_UNDER, 150)
    for rect in (GRIP_SIDE, GRIP_BACK):
        fill(rect, 55)
    for rect in (CARD_ROLL, CARD_END, CARD_FACE, CARD_FACE_L, CARD_BACK):
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


def octagon(apothem, z0, length, faces, pivot_y=None, centre_x=0.0):
    """Four rotated boxes read as an eight sided prism around the drum axis."""
    side = 2 * apothem * math.tan(math.radians(22.5))
    py = DRUM_Y if pivot_y is None else pivot_y
    return [cube([centre_x - apothem, py - side / 2, z0], [apothem * 2, side, length],
                 faces, rotation=[0, 0, 45 * k], pivot=[centre_x, py, z0 + length / 2])
            for k in range(4)]


def bolt_face(cx, cy, z, r=0.085, depth=0.055):
    """A screw head standing off a face that points down -Z / +Z."""
    return cube([cx - r, cy - r, z], [r * 2, r * 2, depth], {"all": sw("steel_lo")})


def bolt_flank(x, cy, cz, r=0.085, depth=0.05):
    """A screw head standing off a face that points along X."""
    return cube([x, cy - r, cz - r], [depth, r * 2, r * 2], {"all": sw("steel_lo")})


def rolled_card(cx, cy, z0, length, radius, faces):
    """A playing card rolled into a tube -- four boxes read as an octagon."""
    side = 2 * radius * math.tan(math.radians(22.5))
    return [cube([cx - radius, cy - side / 2, z0], [radius * 2, side, length], faces,
                 rotation=[0, 0, 45 * k], pivot=[cx, cy, z0 + length / 2])
            for k in range(4)]


def ring_cubes(count, radius, cx, cy, z0, length, size, faces):
    """A hollow ring of small cubes -- a chamber mouth the card shows through."""
    out = []
    for k in range(count):
        a = math.radians(k * 360.0 / count)
        px, py = cx + radius * math.cos(a), cy + radius * math.sin(a)
        out.append(cube([px - size / 2, py - size / 2, z0], [size, size, length], faces))
    return out


def chamber_axis(index):
    a = math.radians(-150 + index * 60)      # matches the skeleton's pivot ring
    return CHAMBER_R * math.cos(a), DRUM_Y + CHAMBER_R * math.sin(a)


def barrel_cubes():
    """The front box: a wide slab ending in a flat plate with the card slot.

    The prop's muzzle is not a barrel: the big front face carries an engraved
    ring, and the card leaves through a vertical slot cut straight through it.
    """
    z0 = MUZZLE_Z
    slab_z = z0 + 0.40
    W = BOX_HALF_W
    H = BOX_TOP_Y - BOX_BOT
    gap = 0.11                                  # half width of the card slot
    out = [
        # main slab
        cube([-W, BOX_BOT, slab_z], [W * 2, H, BOX_LEN - 0.40],
             {"all": sw("steel"), "east": BOX_SIDE, "west": BOX_SIDE_L,
              "up": BOX_TOP, "down": BOX_UNDER, "south": sw("steel_lo")}),
        # dark slot floor, just wide enough to show through the gap
        cube([-0.20, BOX_BOT + 0.08, z0 + 0.14], [0.40, H - 0.16, 0.10],
             {"all": sw("bore")}),
        # front half plates; the space between them is the vertical muzzle slot
        cube([-W + 0.06, BOX_BOT + 0.05, z0], [W - 0.06 - gap, H - 0.10, 0.42],
             {"all": sw("steel"), "north": FRONT_L, "up": sw("steel_hi"),
              "down": sw("shadow")}),
        cube([gap, BOX_BOT + 0.05, z0], [W - 0.06 - gap, H - 0.10, 0.42],
             {"all": sw("steel"), "north": FRONT_R, "up": sw("steel_hi"),
              "down": sw("shadow")}),
        # chin under the front plate
        cube([-W + 0.02, BOX_BOT - 0.20, z0 + 0.06], [W * 2 - 0.04, 0.46, 0.46],
             {"all": sw("steel_lo"), "down": BOX_UNDER}),
        # raised deck at the top rear of the box
        cube([-0.86, BOX_TOP_Y, z0 + 2.55], [1.72, 0.28, 2.05],
             {"all": sw("steel_hi"), "up": BOX_TOP,
              "east": sw("steel"), "west": sw("steel")}),
        cube([-0.16, BOX_TOP_Y, z0 + 3.90], [0.32, 0.42, 0.32],
             {"all": sw("steel_lo"), "south": sw("shadow")}),
        # bottom band with the latched hatch, toward the front like the prop
        cube([-(W + 0.04), BOX_BOT - 0.55, slab_z],
             [(W + 0.04) * 2, 0.58, BOX_LEN - 0.85],
             {"all": sw("steel_lo"), "east": BOX_BAND, "west": BOX_BAND_L,
              "down": BOX_UNDER}),
        cube([-0.42, BOX_BOT - 0.65, z0 + 0.95], [0.84, 0.16, 1.20],
             {"all": sw("steel_hi"), "down": BOX_UNDER}),
        cube([-0.20, BOX_BOT - 0.71, z0 + 1.22], [0.40, 0.10, 0.52],
             {"all": sw("steel_lo")}),
        # raised side panels
        cube([W - 0.005, 8.35, z0 + 1.40], [0.055, 1.60, 2.60],
             {"all": sw("steel_hi"), "east": BOX_SIDE}),
        cube([-(W + 0.05), 8.35, z0 + 1.40], [0.055, 1.60, 2.60],
             {"all": sw("steel_hi"), "west": BOX_SIDE_L}),
    ]
    # 45 degree chamfers joining the front plate to top and bottom
    for sy in (1, -1):
        cy = (BOX_TOP_Y - 0.04) if sy > 0 else (BOX_BOT + 0.04)
        out.append(cube([-W - 0.01, cy - 0.08, z0 - 0.20],
                        [W * 2 + 0.02, 0.16, 0.80],
                        {"all": sw("steel_hi")},
                        rotation=[45 * sy, 0, 0], pivot=[0, cy, z0 + 0.20]))
    # vertical bevels at the front corners
    for sx in (-1, 1):
        out.append(cube([sx * (W - 0.10) - 0.07, BOX_BOT + 0.06, z0 - 0.14],
                        [0.14, H - 0.12, 0.55],
                        {"all": sw("steel_hi")},
                        rotation=[0, -sx * 35, 0], pivot=[sx * (W - 0.10), 9.0, z0 + 0.14]))
    # chamfered long edges on the slab section
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx = sx * (W - 0.09)
            cy = (BOX_TOP_Y - 0.11) if sy > 0 else (BOX_BOT + 0.11)
            ln = BOX_LEN - 0.90
            out.append(cube([cx - 0.15, cy - 0.15, slab_z + 0.05], [0.30, 0.30, ln],
                            {"all": sw("steel_hi")}, rotation=[0, 0, 45],
                            pivot=[cx, cy, slab_z + 0.05 + ln / 2]))
    return out


def gun_body_cubes():
    """Top rail, fan-ribbed rear plate, gussets and the bare trigger."""
    rod = {"all": sw("steel_hi"), "north": sw("steel_lo"), "south": sw("steel_lo")}
    out = [
        # thin centre strap between the two rods
        cube([-0.16, 10.52, -0.30], [0.32, 0.22, 5.35],
             {"all": sw("steel"), "up": BOX_TOP}),
        cube([-0.38, 10.34, -0.62], [0.76, 0.52, 0.70],
             {"all": sw("steel"), "up": sw("steel_hi")}),
        # hooked step at the rear end of the rail, as drawn in the anime
        cube([-0.38, 10.56, 4.55], [0.76, 0.28, 1.05],
             {"all": sw("steel"), "up": BOX_TOP}),
        cube([-0.34, 10.82, 5.20], [0.68, 0.34, 0.40], {"all": sw("steel_hi")}),
        cube([-0.34, 10.82, 4.80], [0.68, 0.20, 0.42], {"all": sw("steel_lo")}),
        # one solid receiver block: rail on top, grip below, no floating struts
        cube([-0.72, 7.85, 3.30], [1.44, 2.72, 3.35],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE,
              "up": sw("steel_hi"), "down": sw("steel_lo")}),
        cube([0.70, 10.00, 3.90], [0.28, 0.40, 0.42], {"all": sw("steel_lo")}),
        cube([-0.98, 10.00, 3.90], [0.28, 0.40, 0.42], {"all": sw("steel_lo")}),
        cube([0.725, 8.75, 4.15], [0.042, 0.42, 1.05],
             {"all": sw("steel_hi"), "east": PLATE}),
        cube([-0.767, 8.75, 4.15], [0.042, 0.42, 1.05],
             {"all": sw("steel_hi"), "west": PLATE_L}),
        cube([-0.62, 7.72, 0.20], [1.24, 0.58, 3.30],
             {"all": sw("steel_lo"), "down": BOX_UNDER}),
        cube([-0.44, 7.30, 0.15], [0.88, 0.52, 0.80], {"all": sw("steel_lo")}),
        cube([-0.44, 7.46, -0.22], [0.88, 0.66, 0.38], {"all": sw("steel_lo")},
             rotation=[36, 0, 0], pivot=[0, 7.79, -0.03]),
        # spine closing the daylight between box and drum dome
        cube([-0.40, 8.55, -0.02], [0.80, 1.70, 1.20], {"all": sw("steel_lo")}),
        cube([-0.11, 7.02, 1.95], [0.22, 0.80, 0.32], {"all": sw("steel_hi")},
             rotation=[-14, 0, 0], pivot=[0, 7.82, 2.11]),
        # pivot pins at the bracket ends
        cube([-0.72, 7.56, 0.28], [1.44, 0.24, 0.24], {"all": sw("steel_hi")}),
    ]
    # the two long rods the anime draws running the length of the gun
    for sx in (-1, 1):
        out += octagon(0.095, -0.62, 5.60, rod, pivot_y=10.56, centre_x=sx * 0.42)
        out.append(cube([sx * 0.42 - 0.14, 10.36, 5.25], [0.28, 0.36, 0.34],
                        {"all": sw("steel_lo")}))
    # the rib fan on the rear plate, modelled rather than only painted
    for k in range(6):
        angle = -58 + k * 13
        for x, face in ((0.715, "east"), (-0.765, "west")):
            out.append(cube([x, 9.15, 3.75], [0.05, 0.16, 1.55],
                            {"all": sw("steel_hi")},
                            rotation=[angle, 0, 0], pivot=[0, 10.45, 5.05]))
    return out


def drum_cubes():
    """Octagonal drum with real chamber mouths, dome forward, card disc aft."""
    facet = {"all": sw("steel"), "east": DRUM_FACET, "west": DRUM_FACET,
             "up": sw("steel"), "down": sw("steel"),
             "north": sw("steel_lo"), "south": sw("steel_lo")}
    out = octagon(DRUM_A, DRUM_Z0, DRUM_Z1 - DRUM_Z0, facet)
    # a recessed flute on each of the eight facets
    for k in range(8):
        out.append(cube([-DRUM_A - 0.045, DRUM_Y - 0.30, DRUM_Z0 + 0.28],
                        [0.05, 0.60, DRUM_Z1 - DRUM_Z0 - 0.56],
                        {"all": sw("steel_lo")},
                        rotation=[0, 0, 45 * k], pivot=[0, DRUM_Y, DRUM_Z0 + 1.0]))
    # stepped dome on the muzzle side
    dome = {"all": sw("steel_hi"), "north": sw("steel"), "south": sw("steel_lo")}
    out += octagon(0.86, DRUM_Z0 - 0.26, 0.28, dome)
    out += octagon(0.56, DRUM_Z0 - 0.46, 0.22, dome)
    out.append(cube([-0.26, DRUM_Y - 0.26, MUZZLE_Z + BOX_LEN - 0.10],
                    [0.52, 0.52, DRUM_Z0 - 0.46 - (MUZZLE_Z + BOX_LEN) + 0.10],
                    {"all": sw("steel_lo")}))
    # rear disc plus a modelled ratchet star
    plate_r = 0.98
    out.append(cube([-plate_r, DRUM_Y - plate_r, DRUM_Z1 - 0.02],
                    [plate_r * 2, plate_r * 2, 0.17],
                    {"all": HIDDEN, "south": DRUM_END}))
    for k in range(6):
        out.append(cube([-0.09, DRUM_Y - 0.09, DRUM_Z1 + 0.14], [0.18, 0.42, 0.10],
                        {"all": sw("steel_lo")},
                        rotation=[0, 0, k * 60], pivot=[0, DRUM_Y, DRUM_Z1 + 0.19]))
    # chamber mouths: a hollow rim on the rear face, the card visible inside.
    # The front face is under the dome, so it needs no mouths.
    for i in range(6):
        cx, cy = chamber_axis(i)
        out += ring_cubes(8, 0.195, cx, cy, DRUM_Z1 + 0.15, 0.16, 0.08,
                          {"all": sw("steel_lo")})
    return out


CHAMBERS = {"round7": 0, "round8": 1, "round9": 2,
            "round10": 3, "round11": 4, "round12": 5}
CHAMBER_TIPS = {"bone4": 0, "bone2": 1, "bone6": 2,
                "bone7": 3, "bone8": 4, "bone9": 5}


def chamber_card(index, z0, length):
    """The special rolled card that this gun chambers."""
    cx, cy = chamber_axis(index)
    return rolled_card(cx, cy, z0, length, 0.145, CARD)


def grip_cubes():
    """Banana grip: wide at the top, narrowing into a silver butt cap."""
    seg1 = dict(rotation=[14, 0, 0], pivot=[0, 8.10, 5.40])
    seg2 = dict(rotation=[40, 0, 0], pivot=[0, 6.45, 5.95])
    out = [
        cube([-0.70, 7.30, 4.20], [1.40, 1.95, 2.45],
             {"all": sw("steel"), "east": REAR_SIDE, "west": REAR_SIDE,
              "up": sw("steel_hi")}),
        cube([-0.64, 6.05, 4.55], [1.28, 2.20, 2.25], GRIP, **seg1),
        cube([-0.62, 6.12, 6.72], [1.24, 2.05, 0.26],
             {"all": sw("grip"), "south": GRIP_BACK}, **seg1),
        cube([-0.56, 4.64, 5.30], [1.12, 2.16, 2.10], GRIP, **seg2),
        cube([-0.54, 4.71, 7.34], [1.08, 2.01, 0.24],
             {"all": sw("grip"), "south": GRIP_BACK}, **seg2),
        cube([-0.60, 4.34, 5.24], [1.20, 0.30, 2.22],
             {"all": sw("steel"), "down": BUTT, "up": sw("steel_lo")}, **seg2),
        cube([0.638, 6.55, 5.10], [0.04, 0.66, 0.66],
             {"all": sw("steel_hi"), "east": MEDALLION}, **seg1),
        cube([-0.678, 6.55, 5.10], [0.04, 0.66, 0.66],
             {"all": sw("steel_hi"), "west": MEDALLION_L}, **seg1),
    ]
    # the grip's finger slots, modelled as recessed bars on both flanks
    for k in range(4):
        out.append(cube([-0.655, 6.35 + k * 0.46, 4.70], [1.31, 0.15, 2.05],
                        {"all": sw("grip_deep")}, **seg1))
    for k in range(4):
        out.append(cube([-0.575, 4.85 + k * 0.45, 5.45], [1.15, 0.14, 1.90],
                        {"all": sw("grip_deep")}, **seg2))
    return out


# the hinge sits at the held end of the rolls, so they splay instead of cross
FAN_PIVOT = [0, 9.62, 2.78]
FAN_ANGLES = [-38 + k * 15 for k in range(6)]
# loader_and_round is scaled 10x by the animation, so the rolls are modelled at
# a tenth of life size: a 9cm card beside a 25cm gun is ~4.7 units long here.
ROLL_LEN = 0.47
ROLL_R = 0.046


def loader_cards():
    """Six of the gun's rolled cards, splayed like a hand of cards.

    A roll is only ~0.9 units across once the animation scales this bone, so a
    single box reads the same as an octagon here and keeps the fan rotation and
    the roll's own axis from fighting over one pivot.
    """
    return [[cube([-ROLL_R, 9.62 - ROLL_R, 2.78], [ROLL_R * 2, ROLL_R * 2, ROLL_LEN],
                  CARD, rotation=[a, 0, 0], pivot=FAN_PIVOT)] for a in FAN_ANGLES]


NEW_CUBES = {
    "barrel": barrel_cubes,
    "gun_body": gun_body_cubes,
    "bone5": drum_cubes,
    "grip": grip_cubes,
    "hammer": lambda: [
        cube([-0.20, 10.50, 5.40], [0.40, 0.46, 0.58], {"all": sw("steel_hi")},
             rotation=[-22, 0, 0], pivot=[0, 10.62, 5.53]),
        cube([-0.14, 10.36, 5.35], [0.28, 0.32, 0.56], {"all": sw("steel_lo")}),
        cube([-0.16, 10.86, 5.47], [0.32, 0.12, 0.30], {"all": sw("steel_lo")},
             rotation=[-22, 0, 0], pivot=[0, 10.62, 5.53]),
    ],
    "trigger": lambda: [
        cube([-0.09, 6.95, 1.88], [0.18, 0.72, 0.28], {"all": sw("steel_hi")},
             rotation=[-16, 0, 0], pivot=[0, 7.67, 2.02]),
    ],
    "crane": lambda: [
        cube([-0.64, 7.52, 1.95], [0.18, 0.28, 2.10], {"all": sw("steel_hi")},
             rotation=[22, 0, 0], pivot=[-0.55, 7.94, 3.15]),
        cube([-0.66, 7.70, 3.60], [0.22, 0.38, 0.40], {"all": sw("steel_lo")}),
        cube([-0.65, 7.40, 1.80], [0.20, 0.24, 0.32], {"all": sw("steel_lo")},
             rotation=[22, 0, 0], pivot=[-0.55, 7.94, 3.15]),
    ],
    "ejector": lambda: [],
    "bone11": lambda: [],
    "cylinder_release": lambda: [],
    "bone": lambda: [],
    # the speed loader body is gone; the reload is a bare fan of cards
    "speed_loader": lambda: [],
}
CLEARED = ["rear_sight", "rear_sight_illuminated", "sight_illuminated"]


def build_geometry():
    model = json.loads((TACZ / f"geo_models/gun/{BASE}_geo.json").read_text())
    geometry = model["minecraft:geometry"][0]
    geometry["description"].update({
        "identifier": "geometry.kid1412.card_gun",
        "texture_width": ATLAS_W, "texture_height": ATLAS_H,
    })
    bones = {b["name"]: b for b in geometry["bones"]}

    for name, cubes in NEW_CUBES.items():
        bones[name]["cubes"] = cubes()
    for name in CLEARED:
        bones[name]["cubes"] = []
    for name, index in CHAMBERS.items():
        bones[name]["cubes"] = chamber_card(index, DRUM_Z0 + 0.06, DRUM_Z1 - DRUM_Z0 - 0.12)
    for name, index in CHAMBER_TIPS.items():
        # card ends sitting proud of the rear disc, thrown clear by the reload
        bones[name]["cubes"] = chamber_card(index, DRUM_Z1 + 0.16, 0.14)
    for name, roll in zip(("round1", "round2", "round3", "round4", "round5", "round6"),
                          loader_cards()):
        bones[name]["cubes"] = roll
    for name in ("lefthand_pos", "righthand_pos"):
        for c in bones[name]["cubes"]:
            c["uv"] = {f: {"uv": [HIDDEN[0], HIDDEN[1]],
                           "uv_size": [HIDDEN[2], HIDDEN[3]]} for f in FACES}
            c.pop("inflate", None)
    # the front sight tab is taller than the Rhino's; lift the aim line over it
    bones["iron_view"]["pivot"][1] = 11.42
    # the bore sits at the top chamber now; neither bone is animated
    bones["muzzle_flash"]["pivot"] = [0, BORE_Y, MUZZLE_Z - 0.15]
    return model


def strip_comments(text):
    """TaCZ ships jsonc; drop // comments without touching them inside strings."""
    out, in_string, escape = [], False, False
    i = 0
    while i < len(text):
        c = text[i]
        if in_string:
            out.append(c)
            if escape:
                escape = False
            elif c == "\\":
                escape = True
            elif c == '"':
                in_string = False
        elif c == '"':
            in_string = True
            out.append(c)
        elif c == "/" and i + 1 < len(text) and text[i + 1] == "/":
            while i < len(text) and text[i] != "\n":
                i += 1
            continue
        else:
            out.append(c)
        i += 1
    return "".join(out)


def build_animation():
    """TaCZ's Rhino animation, retimed for cards rather than brass.

    Keyframe timings and sound cues are left alone so the stock state machine
    still lines up; what changes is the loader, which now flourishes like a
    card fan and splays its six cards open as it comes up.
    """
    anim = json.loads(strip_comments(
        (TACZ / f"animations/{BASE}.animation.json").read_text()))

    for name in ("reload_empty", "reload_tactical"):
        bones = anim["animations"][name]["bones"]

        # a magician's flourish as the fan is brought up
        loader = bones.setdefault("loader_and_round", {})
        rotation = loader.setdefault("rotation", {})
        appear = 1.8333 if name == "reload_empty" else 1.1
        rotation[f"{appear:.4f}"] = [0, 0, -150]
        rotation[f"{appear + 0.20:.4f}"] = [0, 0, 12]
        rotation[f"{appear + 0.33:.4f}"] = [0, 0, 0]

        # the cards start stacked and spread open into the fan
        for k, angle in enumerate(FAN_ANGLES):
            card = bones.setdefault(f"round{k + 1}", {})
            card["rotation"] = {
                f"{appear:.4f}": [-angle, 0, 0],
                f"{appear + 0.12 + k * 0.035:.4f}": [-angle * 0.35, 0, 0],
                f"{appear + 0.30 + k * 0.035:.4f}": [0, 0, 0],
            }
    return anim


def build_display():
    display = json.loads((TACZ / f"display/guns/{BASE}_display.json").read_text())
    display["model"] = "kid1412:gun/card_gun_geo"
    display["texture"] = "kid1412:gun/uv/card_gun"
    # No lod entry: with GunLodRenderDistance=0 TaCZ would otherwise draw the
    # low poly model in every context except the GUI, so a dropped or held gun
    # would not match the one in the inventory.
    display.pop("lod", None)
    display["slot"] = "kid1412:gun/slot/card_gun"
    display["hud"] = "kid1412:gun/hud/card_gun"
    display.pop("shell", None)
    display["muzzle_flash"] = {"texture": "tacz:flash/common_muzzle_flash", "scale": 0.12}
    display["animation"] = "kid1412:card_gun"
    display["sounds"].update({
        "shoot": "tacz:deagle/deagle_silence",
        "shoot_3p": "tacz:deagle/deagle_silence_3p",
        "dry_fire": "tacz:dry_fire",
    })
    return display


def main():
    if not TACZ.is_dir():
        sys.exit(f"[error] TaCZ default gun pack not found at {TACZ}. Run the client once.")

    for path in (OUT_MODEL, OUT_TEX, OUT_DISPLAY, OUT_ANIM):
        path.parent.mkdir(parents=True, exist_ok=True)

    if OUT_MODEL.exists() and "--reset" not in sys.argv:
        print(f"model {OUT_MODEL.relative_to(ROOT)}  (hand-edited file kept; "
              "pass --reset to regenerate the shape)")
    else:
        OUT_MODEL.write_text(json.dumps(build_geometry(), ensure_ascii=False, indent=2) + "\n")
        print(f"model {OUT_MODEL.relative_to(ROOT)}  (regenerated)")
    OUT_DISPLAY.write_text(json.dumps(build_display(), ensure_ascii=False, indent=2) + "\n")
    OUT_ANIM.parent.mkdir(parents=True, exist_ok=True)
    OUT_ANIM.write_text(json.dumps(build_animation(), ensure_ascii=False, indent=2) + "\n")

    atlas = build_atlas()
    atlas.save(OUT_TEX)
    build_specular(atlas).save(OUT_TEX_S)
    Image.new("RGBA", atlas.size, (128, 128, 255, 255)).save(OUT_TEX_N)

    print(f"anim  {OUT_ANIM.relative_to(ROOT)}")
    print(f"disp  {OUT_DISPLAY.relative_to(ROOT)}")
    print(f"uv    {OUT_TEX.relative_to(ROOT)} {atlas.size}")


if __name__ == "__main__":
    main()
