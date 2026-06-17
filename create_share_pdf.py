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


def wrapped_text(text: str, font, max_width: int, draw: ImageDraw.ImageDraw) -> str:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


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

    tag_box = (260, 154, 980, 218)
    draw.rounded_rectangle(tag_box, radius=20, fill=(225, 204, 169, 255))
    tag_font = load_font(28, bold=True)
    centered_text(draw, tag_box, "CONVITE OFICIAL", tag_font, (93, 56, 33, 255))

    title_font = load_font(44, bold=True)
    body_font = load_font(27)
    sign_font = load_font(30, bold=True)

    centered_text(draw, (180, 258, 1060, 332), "O de casa, vaqueiro(a)!", title_font, (102, 64, 38, 255))

    message_1 = (
        "Prepare o chapeu, a bota e a animacao para viver um dia especial, cheio de alegria, "
        "diversao e boas lembrancas no Haras GB. E para deixar a festa ainda mais bonita e no "
        "clima da comemoracao, convidamos voce a vir com seu traje country. Mas nao se preocupe "
        "se nao tiver um look no estilo: sua presenca e o que realmente faz essa festa acontecer!"
    )
    message_2 = (
        "Agradecemos por fazer parte desse momento tao importante na vida do nosso pequeno "
        "vaqueiro. Sera uma honra celebrar ao seu lado essa data tao especial!"
    )
    max_text_width = 770
    wrapped_1 = wrapped_text(message_1, body_font, max_text_width, draw)
    wrapped_2 = wrapped_text(message_2, body_font, max_text_width, draw)

    text_box_1 = (200, 370, 1040, 1010)
    centered_text(draw, text_box_1, wrapped_1, body_font, (112, 77, 50, 255), spacing=12)

    divider_y = 1046
    draw.line((320, divider_y, 920, divider_y), fill=(198, 169, 128, 255), width=2)

    text_box_2 = (220, 1086, 1020, 1288)
    centered_text(draw, text_box_2, wrapped_2, body_font, (112, 77, 50, 255), spacing=12)

    centered_text(draw, (240, 1320, 1000, 1366), "Com carinho,", body_font, (112, 77, 50, 255))
    centered_text(draw, (220, 1382, 1020, 1470), "Familia do Gael", sign_font, (98, 62, 38, 255))
    centered_text(draw, (220, 1450, 1020, 1512), "Haras GB", load_font(40, script=True), (109, 118, 51, 255))

    button_rect = (274, 1558, 966, 1632)
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
