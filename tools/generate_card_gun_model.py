"""Build the Kid card gun on TaCZ's Rhino skeleton without referencing its model directly."""

import copy
import json
from pathlib import Path
from PIL import Image, ImageEnhance

ROOT = Path(__file__).resolve().parents[1]
TA = ROOT / "run/tacz/tacz_default_gun/assets/tacz"
OUT_MODEL = ROOT / "assets/kid1412/geo_models/gun/card_gun_geo.json"
OUT_TEXTURE = ROOT / "assets/kid1412/textures/gun/uv/card_gun.png"
OUT_SPECULAR = ROOT / "assets/kid1412/textures/gun/uv/card_gun_s.png"
OUT_NORMAL = ROOT / "assets/kid1412/textures/gun/uv/card_gun_n.png"


def cube(origin, size, uv=(384, 0), pivot=None, rotation=None):
    value = {"origin": origin, "size": size, "uv": list(uv)}
    if pivot is not None:
        value["pivot"] = pivot
    if rotation is not None:
        value["rotation"] = rotation
    return value


def main():
    source_model = TA / "geo_models/gun/rhino357_geo.json"
    source_texture = TA / "textures/gun/uv/rhino357.png"
    data = json.loads(source_model.read_text())
    geometry = data["minecraft:geometry"][0]
    geometry["description"]["identifier"] = "geometry.kid1412.card_gun"
    geometry["description"]["texture_width"] = 512
    geometry["description"]["texture_height"] = 512

    # Thin stepped armour plates preserve the detailed Rhino underneath. Unlike
    # the previous solid cuboid they do not cover the cylinder or fill the muzzle.
    shell = []
    segments = [
        (-5.48, 1.12, 8.35, 2.00), (-4.36, 1.12, 8.22, 2.20),
        (-3.24, 1.12, 8.12, 2.38), (-2.12, 1.12, 8.08, 2.48),
        (-1.00, 0.92, 8.18, 2.38),
    ]
    for index, (z, depth, y, height) in enumerate(segments):
        shell.append(cube([-0.57, y, z], [0.08, height, depth], (384, index * 18)))
        shell.append(cube([0.49, y, z], [0.08, height, depth], (400, index * 18)))
    shell.extend([
        cube([-0.48, 10.55, -5.35], [0.96, 0.16, 4.9], (416, 0)),
        cube([-0.46, 8.04, -5.25], [0.92, 0.14, 4.7], (416, 12)),
        cube([-0.61, 8.62, -4.75], [0.06, 0.22, 3.4], (416, 24)),
        cube([0.55, 8.62, -4.75], [0.06, 0.22, 3.4], (416, 24)),
    ])
    geometry["bones"].append({"name": "kid_front_shell", "parent": "base_gun", "pivot": [0, 9.4, -2.6], "cubes": shell})

    # Card guide/folding mechanism visible above the rear of the receiver.
    geometry["bones"].append({"name": "kid_card_guide", "parent": "base_gun", "pivot": [0, 10.6, 2.2], "cubes": [
        cube([-0.48, 10.62, 1.65], [0.14, 1.28, 0.22], (448, 0), [-0.4, 10.7, 1.8], [12, 0, -6]),
        cube([-0.12, 10.72, 1.58], [0.14, 1.42, 0.22], (452, 0), [-0.05, 10.8, 1.75], [8, 0, 0]),
        cube([0.24, 10.62, 1.65], [0.14, 1.28, 0.22], (456, 0), [0.32, 10.7, 1.8], [12, 0, 6]),
        cube([-0.55, 10.48, 1.48], [1.1, 0.18, 0.62], (448, 20)),
        cube([-0.42, 11.58, 1.7], [0.84, 0.12, 0.42], (448, 28)),
    ]})

    # Black monocle engraving assembled as a small octagonal relief on the grip.
    mark = []
    for angle in (0, 45, 90, 135):
        mark.append(cube([0.626, 5.55, 5.15], [0.035, 0.08, 0.78], (480, 0), [0.64, 5.94, 5.54], [angle, 0, 0]))
    mark.append(cube([0.626, 5.08, 5.75], [0.035, 0.08, 0.72], (488, 0), [0.64, 5.4, 5.76], [-35, 0, 0]))
    geometry["bones"].append({"name": "kid_monocle_mark", "parent": "grip", "pivot": [0.64, 5.9, 5.55], "cubes": mark})

    OUT_MODEL.parent.mkdir(parents=True, exist_ok=True)
    OUT_MODEL.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    image = Image.open(source_texture).convert("RGBA")
    rgb = image.convert("RGB")
    rgb = ImageEnhance.Color(rgb).enhance(0.18)
    rgb = ImageEnhance.Brightness(rgb).enhance(1.16)
    rgb.putalpha(image.getchannel("A"))
    OUT_TEXTURE.parent.mkdir(parents=True, exist_ok=True)
    rgb.save(OUT_TEXTURE)
    specular_source = TA / "textures/gun/uv/rhino357_s.png"
    Image.open(specular_source).convert("RGBA").save(OUT_SPECULAR)
    Image.new("RGBA", (512, 512), (128, 128, 255, 255)).save(OUT_NORMAL)


if __name__ == "__main__":
    main()
