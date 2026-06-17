from __future__ import annotations

from pathlib import Path

import fitz
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent
ART_PATH = ROOT / "assets" / "foto-1.jpg"
LOGO_PATH = ROOT / "assets" / "logo-haras-gb.png"
OUTPUT_PDF = ROOT / "Convite-Oficial-Gael.pdf"
PREVIEW_PNG = ROOT / "tmp" / "share-pdf-preview.png"
PAGE_SIZE = (1240, 1754)
TARGET_URL = "https://danielbomfim009.github.io/Gael-Neves-de-Santana-Bomfim/"


def ensure_dirs() -> None:
    PREVIEW_PNG.parent.mkdir(parents=True, exist_ok=True)


def load_font(size: int, *, bold: bool = False, script: bool = False, emoji: bool = False):
    candidates: list[str] = []
    if emoji:
        candidates.extend(
            [
                r"C:\Windows\Fonts\seguiemj.ttf",
                r"C:\Windows\Fonts\SegoeUIEmoji.ttf",
            ]
        )
    elif script:
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


def trim_logo(image: Image.Image) -> Image.Image:
    rgba = image.convert("RGBA")
    pixels = rgba.load()
    for y in range(rgba.height):
        for x in range(rgba.width):
            r, g, b, a = pixels[x, y]
            if r > 245 and g > 245 and b > 245:
                pixels[x, y] = (255, 255, 255, 0)

    bbox = rgba.getbbox()
    if bbox:
        rgba = rgba.crop(bbox)
    return rgba


def centered_text(draw: ImageDraw.ImageDraw, box, text, font, fill, *, spacing=6):
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
        candidate = word if not current else f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
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
    background = background.filter(ImageFilter.GaussianBlur(12))
    background = Image.blend(background, Image.new("RGB", PAGE_SIZE, (108, 73, 46)), 0.42)

    canvas = background.convert("RGBA")
    draw = ImageDraw.Draw(canvas)

    panel = (94, 88, 1146, 1668)
    draw.rounded_rectangle((panel[0] + 10, panel[1] + 14, panel[2] + 10, panel[3] + 14), radius=42, fill=(48, 26, 14, 78))
    draw.rounded_rectangle(panel, radius=42, fill=(251, 246, 236, 238), outline=(145, 100, 62, 255), width=3)
    draw.rounded_rectangle((120, 114, 1120, 1642), radius=34, outline=(211, 186, 150, 255), width=2)

    logo = trim_logo(Image.open(LOGO_PATH))
    logo.thumbnail((700, 300), Image.Resampling.LANCZOS)
    logo_x = int((PAGE_SIZE[0] - logo.width) / 2)
    canvas.alpha_composite(logo, (logo_x, 96))

    title_font = load_font(48, bold=True)
    body_font = load_font(31)
    sign_font = load_font(35, bold=True)
    accent_font = load_font(33, emoji=True)

    centered_text(draw, (170, 350, 1070, 390), "\U0001F920 \U0001F40E", accent_font, (96, 59, 35, 255))
    centered_text(draw, (150, 392, 1090, 474), "\u00d4 de casa, vaqueiro(a)!", title_font, (96, 59, 35, 255))

    opening = (
        "Estamos felizes demais em saber que voc\u00ea vai participar da primeira grande vaquejada "
        "do nosso pequeno Gael!\n\n"
        "Prepare o chap\u00e9u, a bota e a anima\u00e7\u00e3o para viver um dia especial, cheio de alegria, "
        "divers\u00e3o e boas lembran\u00e7as no Haras GB. E para deixar a festa ainda mais bonita e no "
        "clima da comemora\u00e7\u00e3o, convidamos voc\u00ea a vir com seu traje country. Mas n\u00e3o se preocupe "
        "se n\u00e3o tiver um look no estilo: sua presen\u00e7a \u00e9 o que realmente faz essa festa acontecer!"
    )
    thanks = (
        "Agradecemos por fazer parte desse momento t\u00e3o importante na vida do nosso pequeno "
        "vaqueiro. Ser\u00e1 uma honra celebrar ao seu lado essa data t\u00e3o especial!"
    )

    max_text_width = 796
    wrapped_opening = "\n\n".join(
        wrapped_text(paragraph, body_font, max_text_width, draw) for paragraph in opening.split("\n\n")
    )
    wrapped_thanks = wrapped_text(thanks, body_font, max_text_width, draw)

    main_panel = (166, 506, 1074, 1458)
    draw.rounded_rectangle((main_panel[0] + 8, main_panel[1] + 10, main_panel[2] + 8, main_panel[3] + 10), radius=34, fill=(97, 61, 35, 34))
    draw.rounded_rectangle(main_panel, radius=34, fill=(255, 251, 244, 180), outline=(216, 191, 152, 255), width=2)

    centered_text(draw, (218, 562, 1022, 1050), wrapped_opening, body_font, (112, 77, 50, 255), spacing=10)

    divider_y = 1102
    draw.line((326, divider_y, 914, divider_y), fill=(202, 173, 133, 255), width=2)
    draw.ellipse((611, divider_y - 8, 629, divider_y + 8), fill=(168, 128, 88, 255))

    centered_text(draw, (218, 1138, 1022, 1278), wrapped_thanks, body_font, (112, 77, 50, 255), spacing=10)
    centered_text(draw, (218, 1288, 1022, 1320), "Com carinho,", body_font, (112, 77, 50, 255))
    centered_text(draw, (218, 1322, 1022, 1350), "\u2665", accent_font, (125, 84, 58, 255))
    centered_text(draw, (218, 1350, 1022, 1392), "Fam\u00edlia do Gael", sign_font, (98, 62, 38, 255))
    centered_text(draw, (218, 1392, 1022, 1424), "Haras GB", body_font, (109, 118, 51, 255))

    button_rect = (286, 1498, 954, 1588)
    draw.rounded_rectangle((button_rect[0] + 4, button_rect[1] + 8, button_rect[2] + 4, button_rect[3] + 8), radius=26, fill=(63, 31, 15, 110))
    draw.rounded_rectangle(button_rect, radius=26, fill=(109, 66, 39, 255), outline=(67, 37, 20, 255), width=3)
    draw.rounded_rectangle((button_rect[0] + 6, button_rect[1] + 6, button_rect[2] - 6, button_rect[1] + 34), radius=20, fill=(188, 142, 95, 170))
    button_font = load_font(32, bold=True)
    centered_text(draw, button_rect, "ABRIR CONVITE OFICIAL", button_font, (251, 241, 222, 255))

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
