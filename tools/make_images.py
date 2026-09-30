"""Generate the site's raster images: og-image.png (1200x630), icon-512.png, apple-touch-icon.png.

Run from the repo root:  python tools/make_images.py
Drawn at 3x and downsampled for smooth edges. Text containing the ʻokina (U+02BB)
must use Segoe UI: Georgia has no glyph for it, and Pillow doesn't do font fallback.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path("C:/Windows/Fonts")
NAVY_DEEP, NAVY, GOLD, MIST = (10, 30, 54), (15, 42, 71), (243, 169, 60), (214, 228, 241)
S = 3  # supersample factor


def font(name, px):
    return ImageFont.truetype(str(FONTS / name), px * S)


def draw_logo(d, x, y, size):
    """Gold rounded square with a navy F and two signal arcs (same geometry as favicon.svg)."""
    u = size / 32  # favicon.svg is on a 32-unit grid
    d.rounded_rectangle([x, y, x + size, y + size], radius=7 * u, fill=GOLD)
    f = [(8, 7), (21, 7), (21, 11), (12, 11), (12, 15), (20, 15), (20, 19), (12, 19), (12, 26), (8, 26)]
    d.polygon([(x + px * u, y + py * u) for px, py in f], fill=NAVY_DEEP)
    for r in (4, 7.5):
        cx, cy = x + 19.4 * u, y + 20 * u
        d.arc([cx - r * u, cy - r * u, cx + r * u, cy + r * u], -40, 40, fill=NAVY_DEEP, width=max(1, round(2 * u)))


def gradient(w, h):
    img = Image.new("RGB", (w, h))
    px = img.load()
    for yy in range(h):
        t = yy / (h - 1)
        c = tuple(round(a + (b - a) * t) for a, b in zip(NAVY_DEEP, NAVY))
        for xx in range(w):
            px[xx, yy] = c
    return img


def og_image():
    W, H = 1200 * S, 630 * S
    img = gradient(1200, 630).resize((W, H))
    # faint signal waves, right side
    waves = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(waves)
    cx, cy = 1040 * S, 430 * S  # right of the title's end so the arcs never cross ".LIVE"
    wd.ellipse([cx - 22 * S, cy - 22 * S, cx + 22 * S, cy + 22 * S], fill=GOLD + (60,))
    for r in (70, 130, 190, 250, 310):
        wd.arc([cx - r * S, cy - r * S, cx + r * S, cy + r * S], -58, 58, fill=GOLD + (48,), width=14 * S)
    img = Image.alpha_composite(img.convert("RGBA"), waves)
    d = ImageDraw.Draw(img)

    draw_logo(d, 80 * S, 80 * S, 76 * S)
    title = font("georgiab.ttf", 88)
    d.text((80 * S, 200 * S), "FURST MEDIA", font=title, fill=(255, 255, 255))
    w = d.textlength("FURST MEDIA ", font=title)
    d.text((80 * S + w, 200 * S), ".LIVE", font=title, fill=GOLD)
    d.text((82 * S, 318 * S), "AI help & hometown radio", font=font("segoeui.ttf", 46), fill=MIST)
    d.text((82 * S, 468 * S), "PĀHOA  ·  PUNA  ·  HAWAIʻI ISLAND", font=font("segoeuib.ttf", 28), fill=GOLD)
    d.text((82 * S, 518 * S), "furstmedia.live", font=font("segoeui.ttf", 28), fill=(155, 179, 201))
    img.convert("RGB").resize((1200, 630), Image.LANCZOS).save(ROOT / "og-image.png", optimize=True)


def icon(px, name, full_bleed=False):
    # iOS rounds the corners itself and turns transparency black, so its icon is full-bleed gold.
    big = Image.new("RGBA", (px * S, px * S), GOLD + (255,) if full_bleed else (0, 0, 0, 0))
    draw_logo(ImageDraw.Draw(big), 0, 0, px * S)
    big.resize((px, px), Image.LANCZOS).save(ROOT / name, optimize=True)


if __name__ == "__main__":
    og_image()
    icon(512, "icon-512.png")
    icon(180, "apple-touch-icon.png", full_bleed=True)
    print("wrote og-image.png, icon-512.png, apple-touch-icon.png")
