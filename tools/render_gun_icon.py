"""Render the card gun's bedrock model to a flat PNG, UV texturing and all.

This feeds the ammo HUD, which is always a 2D texture in TaCZ.  Inventory slots
are handled differently: kid_gun_1412.client.CardGunSlotRenderer draws the live
model there, so the gun pack's `slot` texture is written out blank to keep TaCZ
from painting flat art underneath it.

    python3 tools/render_gun_icon.py
"""

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets/kid1412/geo_models/gun/card_gun_geo.json"
TEXTURE = ROOT / "assets/kid1412/textures/gun/uv/card_gun.png"
OUT_SLOT = ROOT / "assets/kid1412/textures/gun/slot/card_gun.png"
OUT_HUD = ROOT / "assets/kid1412/textures/gun/hud/card_gun.png"

OUT_SIZE = 256
SS = 4                                   # supersample factor
YAW, PITCH, ROLL = -118.0, 15.0, -6.0
LIGHT = (-0.42, 0.78, -0.46)
AMBIENT, DIFFUSE = 0.62, 0.38

# hands are placeholders for the player's arms; the speed loader only exists
# mid-reload, so neither belongs in a still of the gun.
SKIP_SUBTREES = {"lefthand_pos", "righthand_pos", "loader_and_round"}

FACE_CORNERS = {                          # texture top-left first, clockwise
    "north": [(1, 1, 0), (0, 1, 0), (0, 0, 0), (1, 0, 0)],
    "south": [(0, 1, 1), (1, 1, 1), (1, 0, 1), (0, 0, 1)],
    "east":  [(1, 1, 0), (1, 1, 1), (1, 0, 1), (1, 0, 0)],
    "west":  [(0, 1, 1), (0, 1, 0), (0, 0, 0), (0, 0, 1)],
    "up":    [(0, 1, 0), (1, 1, 0), (1, 1, 1), (0, 1, 1)],
    "down":  [(0, 0, 1), (1, 0, 1), (1, 0, 0), (0, 0, 0)],
}
NORMALS = {"north": (0, 0, -1), "south": (0, 0, 1), "west": (-1, 0, 0),
           "east": (1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0)}


def rot(v, axis, deg):
    a = math.radians(-deg)               # bedrock turns the opposite way to math
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    if axis == 0:
        return (x, y * c - z * s, y * s + z * c)
    if axis == 1:
        return (x * c + z * s, y, -x * s + z * c)
    return (x * c - y * s, x * s + y * c, z)


def rot_dir(v, rotation):
    """Rotate a direction vector through a bedrock rotation triple."""
    rx, ry, rz = rotation
    if rx:
        v = rot(v, 0, rx)
    if ry:
        v = rot(v, 1, ry)
    if rz:
        v = rot(v, 2, rz)
    return v


def apply(v, rotation, pivot):
    v = tuple(v[i] - pivot[i] for i in range(3))
    rx, ry, rz = rotation
    if rx:
        v = rot(v, 0, rx)
    if ry:
        v = rot(v, 1, ry)
    if rz:
        v = rot(v, 2, rz)
    return tuple(v[i] + pivot[i] for i in range(3))


def solve(matrix, rhs):
    n = len(rhs)
    m = [row[:] + [rhs[i]] for i, row in enumerate(matrix)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-12:
            return None
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        m[col] = [v / div for v in m[col]]
        for r in range(n):
            if r != col and m[r][col]:
                factor = m[r][col]
                m[r] = [v - factor * w for v, w in zip(m[r], m[col])]
    return [m[i][n] for i in range(n)]


def perspective_coeffs(dest, src):
    """Coefficients PIL needs to sample `src` quad for each pixel of `dest` quad."""
    rows, rhs = [], []
    for (dx, dy), (sx, sy) in zip(dest, src):
        rows.append([dx, dy, 1, 0, 0, 0, -sx * dx, -sx * dy])
        rhs.append(sx)
        rows.append([0, 0, 0, dx, dy, 1, -sy * dx, -sy * dy])
        rhs.append(sy)
    return solve(rows, rhs)


def collect_faces(model_path):
    geo = json.load(open(model_path))["minecraft:geometry"][0]
    bones = {b["name"]: b for b in geo["bones"]}

    def ancestry(name):
        chain = []
        while name:
            chain.append(bones[name])
            name = bones[name].get("parent")
        return chain

    faces = []
    for name, bone in bones.items():
        chain = ancestry(name)
        if any(b["name"] in SKIP_SUBTREES for b in chain):
            continue
        for c in bone.get("cubes", []):
            grow = c.get("inflate", 0)
            o = [c["origin"][i] - grow for i in range(3)]
            s = [c["size"][i] + 2 * grow for i in range(3)]
            if min(s) <= 0:
                continue
            for face, corners in FACE_CORNERS.items():
                rect = c["uv"].get(face)     # the stock model omits culled faces
                if rect is None:
                    continue
                u, v = rect["uv"]
                uw, vh = rect["uv_size"]
                pts = []
                for cx, cy, cz in corners:
                    p = (o[0] + s[0] * cx, o[1] + s[1] * cy, o[2] + s[2] * cz)
                    if "rotation" in c:
                        p = apply(p, c["rotation"], c["pivot"])
                    for b in chain:
                        if b.get("rotation"):
                            p = apply(p, b["rotation"], b["pivot"])
                    p = rot(p, 1, YAW)
                    p = rot(p, 0, PITCH)
                    p = rot(p, 2, ROLL)
                    pts.append(p)
                # the normal must ride through the same rotations as the corners
                n = NORMALS[face]
                if "rotation" in c:
                    n = rot_dir(n, c["rotation"])
                for b in chain:
                    if b.get("rotation"):
                        n = rot_dir(n, b["rotation"])
                n = rot(rot(rot(n, 1, YAW), 0, PITCH), 2, ROLL)
                if n[2] >= -0.02:                       # back face
                    continue
                lum = AMBIENT + DIFFUSE * max(0.0, sum(n[i] * LIGHT[i] for i in range(3)))
                faces.append((sum(p[2] for p in pts) / 4, pts,
                              [(u, v), (u + uw, v), (u + uw, v + vh), (u, v + vh)], lum))
    faces.sort(key=lambda f: f[0], reverse=True)
    return faces


def render(faces, texture, size, margin=0.045):
    xs = [p[0] for _, pts, _, _ in faces for p in pts]
    ys = [p[1] for _, pts, _, _ in faces for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys))
    scale = size * (1 - 2 * margin) / span
    cx = size / 2 - (min(xs) + max(xs)) / 2 * scale
    cy = size / 2 + (min(ys) + max(ys)) / 2 * scale

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    for _, pts, uv, lum in faces:
        dest = [(cx + p[0] * scale, cy - p[1] * scale) for p in pts]
        x0 = math.floor(min(p[0] for p in dest))
        y0 = math.floor(min(p[1] for p in dest))
        x1 = math.ceil(max(p[0] for p in dest))
        y1 = math.ceil(max(p[1] for p in dest))
        w, h = max(1, x1 - x0), max(1, y1 - y0)
        local = [(p[0] - x0, p[1] - y0) for p in dest]
        coeffs = perspective_coeffs(local, uv)
        if coeffs is None:
            continue
        tile = texture.transform((w, h), Image.PERSPECTIVE, coeffs, Image.BILINEAR)
        shaded = Image.merge("RGBA", tuple(
            tile.getchannel(k).point(lambda v: min(255, int(v * lum))) for k in "RGB"
        ) + (tile.getchannel("A"),))
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon(local, fill=255)
        mask = Image.composite(shaded.getchannel("A"), Image.new("L", (w, h), 0), mask)
        canvas.paste(shaded, (x0, y0), mask)
    return canvas


def main():
    texture = Image.open(TEXTURE).convert("RGBA")
    faces = collect_faces(MODEL)
    big = render(faces, texture, OUT_SIZE * SS)
    icon = big.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)
    OUT_SLOT.parent.mkdir(parents=True, exist_ok=True)
    OUT_HUD.parent.mkdir(parents=True, exist_ok=True)
    icon.save(OUT_HUD)
    # The inventory draws the real model; TaCZ still insists on a slot texture.
    Image.new("RGBA", (16, 16), (0, 0, 0, 0)).save(OUT_SLOT)
    print(f"hud   {OUT_HUD.relative_to(ROOT)}  ({len(faces)} faces)")
    print(f"slot  {OUT_SLOT.relative_to(ROOT)}  (blank: the model is drawn live)")


if __name__ == "__main__":
    main()
