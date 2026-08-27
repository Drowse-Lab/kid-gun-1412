"""Generate the editable pixel textures and inventory icons for kid_gun_1412_pack."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1] / "assets" / "kid1412" / "textures"


def save(image: Image.Image, relative: str) -> None:
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)


def gun_uv() -> None:
    image = Image.new("RGBA", (128, 128), (225, 229, 232, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 45, 35), fill=(202, 209, 215, 255))
    draw.rectangle((0, 36, 127, 71), fill=(184, 192, 201, 255))
    draw.rectangle((40, 36, 77, 70), fill=(216, 220, 224, 255))
    draw.rectangle((78, 36, 127, 70), fill=(151, 161, 171, 255))
    draw.rectangle((0, 72, 39, 91), fill=(91, 101, 111, 255))
    draw.rectangle((40, 72, 127, 91), fill=(167, 176, 185, 255))
    draw.rectangle((0, 92, 31, 107), fill=(116, 126, 136, 255))
    draw.rectangle((32, 92, 91, 127), fill=(24, 27, 32, 255))
    draw.rectangle((58, 92, 81, 127), fill=(39, 43, 49, 255))
    draw.rectangle((92, 92, 99, 107), fill=(75, 81, 88, 255))
    draw.rectangle((100, 92, 127, 107), fill=(245, 244, 237, 255))
    draw.rectangle((0, 108, 31, 127), fill=(238, 238, 233, 255))
    for x in range(6, 124, 12):
        draw.line((x, 40, x + 7, 40), fill=(236, 240, 243, 255), width=1)
    draw.line((4, 64, 120, 64), fill=(112, 122, 132, 255), width=2)
    save(image, "gun/uv/card_gun.png")


def card_uv() -> None:
    image = Image.new("RGBA", (32, 32), (248, 247, 240, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 30, 30), radius=2, outline=(164, 21, 43, 255), width=2)
    draw.polygon([(16, 6), (10, 14), (16, 20), (22, 14)], fill=(20, 22, 26, 255))
    draw.polygon([(16, 18), (12, 25), (20, 25)], fill=(20, 22, 26, 255))
    draw.text((4, 3), "A", fill=(164, 21, 43, 255))
    draw.rectangle((20, 0, 31, 31), fill=(180, 20, 42, 255))
    save(image, "ammo/uv/playing_card.png")


def gun_icon() -> Image.Image:
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    edge = (35, 41, 48, 255)
    silver = (206, 213, 220, 255)
    light = (236, 239, 241, 255)
    dark = (28, 31, 37, 255)
    draw.rounded_rectangle((22, 73, 126, 151), radius=9, fill=silver, outline=edge, width=5)
    draw.polygon([(116, 86), (206, 86), (225, 112), (206, 151), (116, 151)], fill=(180, 188, 197, 255), outline=edge)
    draw.line((38, 92, 110, 92), fill=light, width=7)
    draw.ellipse((30, 99, 74, 143), fill=(80, 90, 100, 255), outline=edge, width=5)
    draw.ellipse((40, 109, 64, 133), fill=(15, 17, 20, 255))
    draw.polygon([(178, 145), (215, 145), (234, 224), (192, 229), (165, 158)], fill=dark, outline=edge)
    draw.rectangle((189, 221, 239, 235), fill=silver, outline=edge, width=4)
    draw.rectangle((119, 66, 205, 82), fill=silver, outline=edge, width=4)
    draw.rectangle((125, 56, 134, 72), fill=light, outline=edge, width=3)
    for y in (169, 184, 199, 214):
        draw.line((190, y, 218, y + 4), fill=(75, 80, 88, 255), width=3)
    return image


def card_icon() -> Image.Image:
    image = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((57, 24, 199, 232), radius=12, fill=(250, 249, 242, 255), outline=(166, 20, 42, 255), width=8)
    draw.text((73, 39), "A", fill=(166, 20, 42, 255), stroke_width=1)
    draw.polygon([(128, 67), (86, 124), (128, 170), (170, 124)], fill=(22, 24, 28, 255))
    draw.polygon([(128, 154), (101, 205), (155, 205)], fill=(22, 24, 28, 255))
    return image


if __name__ == "__main__":
    gun_uv()
    card_uv()
    icon = gun_icon()
    save(icon, "gun/slot/card_gun.png")
    save(icon, "gun/hud/card_gun.png")
    save(card_icon(), "ammo/slot/playing_card.png")
