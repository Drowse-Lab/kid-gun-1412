"""Apply a hand-edited card gun model: repair the rig, refresh icon and pack.

The single source of truth for the gun's shape is
    assets/kid1412/geo_models/gun/card_gun_geo.json
Open it in Blockbench (File > Open Model), sculpt the cubes freely, save, then

    python3 tools/apply_model.py            # repair + hud icon + pack zip
    python3 tools/apply_model.py --watch    # do that automatically on save

What "repair" fixes after an edit session:
  * bones renamed or deleted in Blockbench are restored (TaCZ's rhino357
    animation needs every one of them, at exactly these pivots)
  * pivots, parents and bone rotations are forced back to the animation rig;
    cubes -- the actual shape -- are kept exactly as edited
  * degenerate (zero-size) cubes are dropped
  * the geometry identifier and texture size TaCZ expects are re-applied

The refreshed pack is written to run/tacz/kid_gun_1412.zip, so a running dev
client picks the change up with /tacz reload; the next `bash run.sh` re-embeds
it in the mod automatically.
"""

import io
import json
import sys
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / "assets/kid1412/geo_models/gun/card_gun_geo.json"
RIG = Path(__file__).resolve().parent / "card_gun_rig.json"
PACK_ZIP = ROOT / "run/tacz/kid_gun_1412.zip"


def repair(report):
    rig = json.loads(RIG.read_text())
    model = json.loads(MODEL.read_text())
    geo = model["minecraft:geometry"][0]

    desc = geo.setdefault("description", {})
    desc["identifier"] = rig["identifier"]
    desc["texture_width"] = rig["texture_width"]
    desc["texture_height"] = rig["texture_height"]

    by_name = {b.get("name"): b for b in geo.get("bones", [])}
    bones = []
    for name, spec in rig["bones"].items():
        bone = by_name.pop(name, None)
        if bone is None:
            bone = {"name": name, "cubes": []}
            report.append(f"restored missing bone: {name}")
        if bone.get("parent") != spec["parent"] or bone.get("pivot") != spec["pivot"]:
            report.append(f"re-rigged bone: {name}")
        bone["name"] = name
        if spec["parent"] is None:
            bone.pop("parent", None)
        else:
            bone["parent"] = spec["parent"]
        bone["pivot"] = spec["pivot"]
        if "rotation" in spec:
            bone["rotation"] = spec["rotation"]
        else:
            bone.pop("rotation", None)

        kept = []
        for cube in bone.get("cubes", []) or []:
            if min(cube.get("size", [0, 0, 0])) <= 0:
                report.append(f"dropped zero-size cube in {name}")
                continue
            kept.append(cube)
        bone["cubes"] = kept
        bones.append(bone)

    for name, bone in by_name.items():          # user-added extra bones
        parent = bone.get("parent")
        if parent not in rig["bones"] and parent not in by_name:
            bone["parent"] = "base_gun" if "base_gun" in rig["bones"] else None
            report.append(f"extra bone {name}: parent fixed to base_gun")
        else:
            report.append(f"kept extra bone: {name}")
        bones.append(bone)

    geo["bones"] = bones
    MODEL.write_text(json.dumps(model, ensure_ascii=False, indent=2) + "\n")
    return sum(len(b["cubes"]) for b in bones)


def refresh_icon():
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import render_gun_icon
    render_gun_icon.main()


def rebuild_pack():
    """Same layout as gradle's buildGunPack, so /tacz reload sees the edit."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as pack:
        for base in ("assets", "data"):
            for path in sorted((ROOT / base).rglob("*")):
                if path.is_file() and path.name != ".DS_Store":
                    pack.write(path, path.relative_to(ROOT))
        pack.write(ROOT / "gunpack.meta.json", "gunpack.meta.json")
    PACK_ZIP.parent.mkdir(parents=True, exist_ok=True)
    PACK_ZIP.write_bytes(buffer.getvalue())


def apply():
    report = []
    cubes = repair(report)
    refresh_icon()
    rebuild_pack()
    for line in report:
        print(f"  fix: {line}")
    print(f"applied: {cubes} cubes | icon refreshed | {PACK_ZIP.relative_to(ROOT)}")


def main():
    if "--watch" not in sys.argv:
        apply()
        return
    print(f"watching {MODEL.relative_to(ROOT)} -- save in Blockbench to apply, Ctrl+C to stop")
    last = MODEL.stat().st_mtime
    while True:
        time.sleep(1)
        mtime = MODEL.stat().st_mtime
        if mtime != last:
            last = mtime
            time.sleep(0.3)                      # let Blockbench finish writing
            try:
                apply()
                last = MODEL.stat().st_mtime     # our own rewrite
            except Exception as error:           # keep watching through bad saves
                print(f"error: {error}")


if __name__ == "__main__":
    main()
