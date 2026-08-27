"""Generate the editable pixel textures and inventory icons for kid_gun_1412_pack."""

from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1] / "assets" / "kid1412" / "textures"
MOD_CARD_ROOT = Path(__file__).resolve().parents[1] / "src" / "main" / "resources" / "assets" / "kid_gun_1412" / "textures" / "entity" / "cards"


def save(image: Image.Image, relative: str) -> None:
    target = ROOT / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    image.save(target)
    if relative.startswith("ammo/cards/"):
        mod_target = MOD_CARD_ROOT / Path(relative).name
        mod_target.parent.mkdir(parents=True, exist_ok=True)
        image.save(mod_target)


def gun_uv() -> None:
    image = Image.new("RGBA", (256, 256), (210, 216, 222, 255))
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 255, 111), fill=(202, 209, 216, 255))
    draw.rectangle((0, 32, 255, 47), fill=(239, 242, 245, 255))
    draw.rectangle((0, 48, 151, 75), fill=(182, 190, 199, 255))
    draw.rectangle((38, 76, 127, 111), fill=(161, 170, 179, 255))
    draw.rectangle((122, 76, 143, 96), fill=(70, 76, 83, 255))
    draw.rectangle((0, 112, 31, 127), fill=(245, 244, 238, 255))
    draw.rectangle((0, 128, 89, 159), fill=(21, 24, 29, 255))
    draw.rectangle((90, 128, 107, 145), fill=(8, 9, 11, 255))
    draw.rectangle((108, 128, 191, 159), fill=(126, 135, 144, 255))
    draw.rectangle((0, 160, 47, 191), fill=(246, 246, 241, 255))
    draw.rectangle((18, 160, 47, 191), fill=(35, 74, 142, 255))
    for y in (8, 24, 56, 88):
        draw.line((4, y, 244, y), fill=(238, 242, 245, 255), width=2)
    save(image, "gun/uv/card_gun.png")

    normal = Image.new("RGBA", image.size, (128, 128, 255, 255))
    save(normal, "gun/uv/card_gun_n.png")
    specular = Image.new("RGBA", image.size, (205, 205, 205, 255))
    spec = ImageDraw.Draw(specular)
    spec.rectangle((0, 128, 107, 159), fill=(35, 35, 35, 255))
    save(specular, "gun/uv/card_gun_s.png")


def card_uv() -> None:
    image = Image.new("RGBA", (32, 32), (248, 247, 240, 255))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 30, 30), radius=2, fill=(32, 72, 148, 255), outline=(238, 241, 244, 255), width=2)
    for offset in range(-24, 40, 6):
        draw.line((2, offset, 29, offset + 27), fill=(107, 151, 210, 255), width=1)
        draw.line((2, offset + 27, 29, offset), fill=(220, 232, 247, 255), width=1)
    save(image, "ammo/uv/playing_card.png")


def draw_suit(draw: ImageDraw.ImageDraw, suit: str, center: tuple[int, int], size: int, color: tuple[int, int, int, int]) -> None:
    """Draw real suit silhouettes without depending on an installed symbol font."""
    cx, cy = center
    r = max(1, size // 4)
    if suit == "D":
        draw.polygon([(cx, cy - size // 2), (cx + size // 2, cy),
                      (cx, cy + size // 2), (cx - size // 2, cy)], fill=color)
    elif suit == "H":
        draw.ellipse((cx - size // 2, cy - size // 3, cx, cy + size // 6), fill=color)
        draw.ellipse((cx, cy - size // 3, cx + size // 2, cy + size // 6), fill=color)
        draw.polygon([(cx - size // 2, cy), (cx + size // 2, cy),
                      (cx, cy + size // 2)], fill=color)
    elif suit == "S":
        draw.ellipse((cx - size // 2, cy - size // 6, cx, cy + size // 3), fill=color)
        draw.ellipse((cx, cy - size // 6, cx + size // 2, cy + size // 3), fill=color)
        draw.polygon([(cx, cy - size // 2), (cx - size // 2, cy + size // 8),
                      (cx + size // 2, cy + size // 8)], fill=color)
        draw.rectangle((cx - r // 2, cy + size // 5, cx + r // 2, cy + size // 2), fill=color)
        draw.polygon([(cx - r, cy + size // 2), (cx + r, cy + size // 2),
                      (cx, cy + size // 3)], fill=color)
    else:  # Clubs
        draw.ellipse((cx - r, cy - size // 2, cx + r, cy), fill=color)
        draw.ellipse((cx - size // 2, cy - size // 8, cx, cy + size // 3), fill=color)
        draw.ellipse((cx, cy - size // 8, cx + size // 2, cy + size // 3), fill=color)
        draw.rectangle((cx - r // 2, cy + size // 5, cx + r // 2, cy + size // 2), fill=color)
        draw.polygon([(cx - r, cy + size // 2), (cx + r, cy + size // 2),
                      (cx, cy + size // 3)], fill=color)


def card_faces() -> None:
    suits = [("S", (20, 22, 26, 255)), ("H", (180, 24, 45, 255)),
             ("D", (180, 24, 45, 255)), ("C", (20, 22, 26, 255))]
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    for suit, color in suits:
        for rank in ranks:
            image = Image.new("RGBA", (63, 88), (249, 248, 242, 255))
            draw = ImageDraw.Draw(image)
            draw.rounded_rectangle((0, 0, 62, 87), radius=4, outline=(210, 210, 205, 255), width=1)
            draw.text((4, 3), rank, fill=color)
            draw_suit(draw, suit, (7, 19), 8, color)
            draw_suit(draw, suit, (31, 44), 25, color)
            draw_suit(draw, suit, (55, 70), 8, color)
            draw.text((51 if rank != "10" else 46, 76), rank, fill=color)
            save(image, f"ammo/cards/{rank.lower()}_{suit.lower()}.png")
    for name, color in (("joker_color", (32, 92, 184, 255)), ("joker_mono", (24, 24, 27, 255))):
        image = Image.new("RGBA", (63, 88), (249, 248, 242, 255))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((0, 0, 62, 87), radius=4, outline=(210, 210, 205, 255), width=1)
        draw.text((8, 8), "JOKER", fill=color)
        draw.polygon([(31, 25), (18, 58), (44, 58)], fill=color)
        save(image, f"ammo/cards/{name}.png")

    back = Image.new("RGBA", (63, 88), (245, 245, 240, 255))
    draw = ImageDraw.Draw(back)
    draw.rounded_rectangle((1, 1, 61, 86), radius=4, fill=(31, 70, 145, 255), outline=(240, 240, 235, 255), width=2)
    for offset in range(-70, 80, 8):
        draw.line((2, offset, 61, offset + 59), fill=(98, 145, 207, 255), width=2)
        draw.line((2, offset + 59, 61, offset), fill=(225, 235, 247, 255), width=1)
    save(back, "ammo/cards/back_blue.png")

    message = Image.new("RGBA", (63, 88), (252, 252, 248, 255))
    draw = ImageDraw.Draw(message)
    draw.rounded_rectangle((0, 0, 62, 87), radius=4, outline=(190, 190, 188, 255), width=1)
    draw.text((8, 38), "MESSAGE", fill=(30, 30, 34, 255))
    save(message, "ammo/cards/message.png")


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
    card_faces()
    icon = gun_icon()
    save(icon, "gun/slot/card_gun.png")
    save(icon, "gun/hud/card_gun.png")
    save(card_icon(), "ammo/slot/playing_card.png")
