from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import math
from app.config import ASSETS_DIR


def _font(size: int):
    for path in ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                 "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def generate_bmi_gif(bmi: float, out_path: Path) -> Path:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames = []
    w, h = 720, 520
    cx, cy, radius = 360, 365, 245
    start_deg, end_deg = 200, 340
    target = max(10, min(bmi, 50))
    frac = (target - 10) / 40
    target_deg = start_deg + frac * (end_deg - start_deg)

    for i in range(18):
        progress = i / 17
        angle = start_deg + progress * (target_deg - start_deg)
        im = Image.new("RGB", (w, h), (245, 249, 247))
        d = ImageDraw.Draw(im)
        d.rounded_rectangle((30, 25, w-30, h-25), 35, fill=(255,255,255), outline=(216,230,224), width=3)
        d.text((w/2, 70), "BMI", font=_font(42), fill=(39,75,61), anchor="mm")
        d.text((w/2, 125), f"{bmi:.2f}", font=_font(58), fill=(24,58,45), anchor="mm")

        segments = [
            (200, 235, (58,166,110)),
            (235, 270, (116,190,90)),
            (270, 305, (242,190,64)),
            (305, 325, (238,132,55)),
            (325, 340, (214,66,56)),
        ]
        for a1, a2, color in segments:
            d.arc((cx-radius, cy-radius, cx+radius, cy+radius), a1, a2, fill=color, width=38)

        rad = math.radians(angle)
        ex = cx + (radius-55) * math.cos(rad)
        ey = cy + (radius-55) * math.sin(rad)
        d.line((cx, cy, ex, ey), fill=(31,45,39), width=10)
        d.ellipse((cx-18, cy-18, cx+18, cy+18), fill=(31,45,39))
        frames.append(im)

    frames[0].save(out_path, save_all=True, append_images=frames[1:], duration=70, loop=0)
    return out_path
