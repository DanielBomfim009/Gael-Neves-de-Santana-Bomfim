from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
ART_PATH = ROOT / "assets" / "foto-1.jpg"
OUTPUT_PDF = ROOT / "Convite-Oficial-Gael.pdf"
PREVIEW_PNG = ROOT / "tmp" / "share-pdf-preview.png"
PAGE_SIZE = (1240, 1754)
TARGET_URL = "https://danielbomfim009.github.io/Gael-Neves-de-Santana-Bomfim/"


def ensure_dirs() -> None:
    PREVIEW_PNG.parent.mkdir(parents=True, exist_ok=True)


def load_font(size: int, bold: bool = False, script: bool = False):
    candidates = []
    if script:
        candidates.extend(
            [
                r"C:\Windows\Fonts\GABRIOLA.TTF",
                r"C:\Windows\Fonts\segoesc.ttf",
                r"C:\Windows\Fonts\georgiai.ttf",
            ]
        )
    elif bold:
        candidates.extend(
            [
                r"C:\Windows\Fonts\georgiab.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
            ]
        )
    else:
        candidates.extend(
            [
                r"C:\Windows\Fonts\georgia.ttf",
                r"C:\Windows\Fonts\arial.ttf",
            ]
        )
    for font_path in candidates:
        path = Path(font_path)
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def centered_text(draw: ImageDraw.ImageDraw, box, text, font, fill, spacing=6):
    x0, y0, x1, y1 = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = x0 + (x1 - x0 - width) / 2
    y = y0 + (y1 - y0 - height) / 2
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing, align="center")


def build_cover_image() -> tuple[Image.Image, tuple[int, int, int, int]]:
    source = Image.open(ART_PATH).convert("RGB")
    background = ImageOps.fit(source, PAGE_SIZE, method=Image.Resampling.LANCZOS, centering=(0.5, 0.35))
    background = background.filter(ImageFilter.GaussianBlur(10))
    background = Image.blend(background, Image.new("RGB", PAGE_SIZE, (108, 73, 46)), 0.38)

    canvas = background.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    panel = (90, 90, 1150, 1664)
    draw.rounded_rectangle((panel[0] + 10, panel[1] + 14, panel[2] + 10, panel[3] + 14), radius=42, fill=(48, 26, 14, 74))
    draw.rounded_rectangle(panel, radius=42, fill=(251, 244, 231, 240), outline=(145, 100, 62, 255), width=4)
    draw.rounded_rectangle((116, 116, 1124, 1638), radius=34, outline=(205, 176, 137, 255), width=2)

    art = Image.open(ART_PATH).convert("RGB")
    art_card = ImageOps.fit(art, (760, 1140), method=Image.Resampling.LANCZOS, centering=(0.5, 0.48))
    art_card = art_card.convert("RGBA")
    art_shadow = Image.new("RGBA", (800, 1180), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(art_shadow)
    shadow_draw.rounded_rectangle((18, 18, 782, 1162), radius=28, fill=(0, 0, 0, 72))
    canvas.alpha_composite(art_shadow, (220, 170))
    draw.rounded_rectangle((240, 188, 1000, 1328), radius=28, fill=(255, 250, 243, 255), outline=(180, 141, 96, 255), width=3)
    canvas.alpha_composite(art_card, (240, 188))

    tag_box = (260, 1348, 980, 1412)
    draw.rounded_rectangle(tag_box, radius=20, fill=(225, 204, 169, 255))
    tag_font = load_font(28, bold=True)
    centered_text(draw, tag_box, "CONVITE OFICIAL", tag_font, (93, 56, 33, 255))

    title_font = load_font(50, bold=True)
    script_font = load_font(76, script=True)
    body_font = load_font(28)

    centered_text(draw, (200, 1436, 1040, 1490), "Toque no botao abaixo para", body_font, (115, 79, 51, 255))
    centered_text(draw, (190, 1490, 1050, 1558), "abrir o convite interativo", load_font(42, bold=True), (107, 67, 39, 255))
    centered_text(draw, (260, 1530, 980, 1592), "do Gael", load_font(58, script=True), (112, 121, 52, 255))

    button_rect = (274, 1588, 966, 1662)
    draw.rounded_rectangle((button_rect[0] + 4, button_rect[1] + 8, button_rect[2] + 4, button_rect[3] + 8), radius=26, fill=(63, 31, 15, 110))
    draw.rounded_rectangle(button_rect, radius=26, fill=(109, 66, 39, 255), outline=(67, 37, 20, 255), width=3)
    draw.rounded_rectangle((button_rect[0] + 6, button_rect[1] + 6, button_rect[2] - 6, button_rect[1] + 30), radius=20, fill=(188, 142, 95, 170))
    button_font = load_font(30, bold=True)
    centered_text(draw, button_rect, "ABRIR CONVITE OFICIAL", button_font, (251, 241, 222, 255))

    footer_font = load_font(20, bold=True)
    centered_text(draw, (200, 1670, 1040, 1714), "HARAS GB", footer_font, (116, 78, 49, 210))

    return canvas.convert("RGB"), button_rect


def create_pdf(image: Image.Image, button_rect: tuple[int, int, int, int]) -> None:
    temp_cover = ROOT / "tmp" / "share-pdf-cover.jpg"
    image.save(temp_cover, quality=90, optimize=True)

    doc = fitz.open()
    page_rect = fitz.paper_rect("a4")
    page = doc.new_page(width=page_rect.width, height=page_rect.height)
    page.insert_image(page_rect, filename=str(temp_cover))

    scale_x = page_rect.width / PAGE_SIZE[0]
    scale_y = page_rect.height / PAGE_SIZE[1]
    x0, y0, x1, y1 = button_rect
    link_rect = fitz.Rect(x0 * scale_x, y0 * scale_y, x1 * scale_x, y1 * scale_y)
    page.insert_link({"kind": fitz.LINK_URI, "from": link_rect, "uri": TARGET_URL})

    doc.set_metadata(
        {
            "title": "Convite Oficial - Primeira Vaquejada do Gael",
            "author": "Codex",
            "subject": "Abertura do convite oficial",
            "keywords": "convite,pdf,vaquejada,gael,haras gb",
        }
    )
    doc.save(str(OUTPUT_PDF), garbage=4, deflate=True)
    doc.close()


def render_preview() -> None:
    doc = fitz.open(OUTPUT_PDF)
    page = doc[0]
    pix = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
    pix.save(str(PREVIEW_PNG))
    doc.close()


def main() -> None:
    ensure_dirs()
    image, button_rect = build_cover_image()
    create_pdf(image, button_rect)
    render_preview()
    print(OUTPUT_PDF)
    print(PREVIEW_PNG)


if __name__ == "__main__":
    main()
