from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


WORKSPACE = Path(__file__).resolve().parents[3]
OUT_DIR = Path(__file__).resolve().parent
TMP_DIR = WORKSPACE / "tmp" / "pdfs" / "wand-card-source"
SOURCE_ART = TMP_DIR / "wand-hi-71.png"
QA_IMAGE = TMP_DIR / "Wand of True Strike - Card Proof.png"
OUT_PDF = OUT_DIR / "Wand of True Strike - Item Card.pdf"

W, H = 750, 1050
SERIF_BOLD = Path(r"C:\Windows\Fonts\georgiab.ttf")
SERIF_ITALIC = Path(r"C:\Windows\Fonts\georgiai.ttf")
SANS = Path(r"C:\Windows\Fonts\arial.ttf")
SANS_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")


def f(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def wrap(draw: ImageDraw.ImageDraw, text: str, face: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if draw.textbbox((0, 0), trial, font=face)[2] <= max_width:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def centered(draw: ImageDraw.ImageDraw, y: int, text: str, face: ImageFont.FreeTypeFont, fill: str) -> None:
    box = draw.textbbox((0, 0), text, font=face)
    draw.text(((W - (box[2] - box[0])) / 2, y), text, font=face, fill=fill)


def make_card() -> Image.Image:
    if not SOURCE_ART.exists():
        raise FileNotFoundError(f"Missing rendered source art: {SOURCE_ART}")

    source = Image.open(SOURCE_ART).convert("RGB")
    card = source.resize((W, H), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(card)

    # Replace the lower rules panel while retaining the original wand illustration
    # and the surrounding Nimble item-card border.
    panel = Image.new("RGB", (650, 426), (247, 243, 229))
    pixels = panel.load()
    random.seed(1701)
    for y in range(panel.height):
        for x in range(panel.width):
            grain = random.choice((-2, -1, 0, 0, 0, 1, 2))
            pixels[x, y] = (247 + grain, 243 + grain, 229 + grain)
    card.paste(panel, (50, 560))
    draw = ImageDraw.Draw(card)

    ink = "#211b1c"
    muted = "#51474a"
    accent = "#8b552f"
    gold = "#c89f4b"

    # Reinforce the item-card frame and panel dividers.
    draw.rounded_rectangle((30, 28, W - 30, H - 28), radius=12, outline=accent, width=3)
    draw.rounded_rectangle((43, 42, W - 43, H - 42), radius=9, outline="#b69570", width=1)
    draw.line((75, 747, W - 75, 747), fill=gold, width=2)
    draw.line((75, 930, W - 75, 930), fill=gold, width=2)

    title = "WAND OF TRUE STRIKE"
    title_face = f(SERIF_BOLD, 47)
    while draw.textbbox((0, 0), title, font=title_face)[2] > 650:
        title_face = f(SERIF_BOLD, title_face.size - 1)
    centered(draw, 585, title, title_face, ink)
    centered(draw, 682, "Uncommon wand, Cantrip (3 charges)", f(SERIF_ITALIC, 25), muted)

    centered(draw, 766, "TRUE STRIKE", f(SANS_BOLD, 27), accent)
    centered(draw, 802, "1 Action - Reach 2 - Single Target", f(SANS_BOLD, 20), muted)

    effect = (
        "Spend 1 charge. Give a creature advantage on the next attack it makes "
        "before the end of its next turn. Multiple castings do not stack."
    )
    effect_face = f(SANS, 23)
    y = 842
    for line in wrap(draw, effect, effect_face, 610):
        centered(draw, y, line, effect_face, ink)
        y += 28

    recharge_label = "RECHARGE:"
    recharge = "Bury the discharged wand in battlefield soil overnight."
    label_face = f(SANS_BOLD, 21)
    body_face = f(SANS, 21)
    label_w = draw.textbbox((0, 0), recharge_label, font=label_face)[2]
    body_w = draw.textbbox((0, 0), recharge, font=body_face)[2]
    total_w = label_w + 10 + body_w
    x = (W - total_w) / 2
    draw.text((x, 947), recharge_label, font=label_face, fill=accent)
    draw.text((x + label_w + 10, 947), recharge, font=body_face, fill=ink)

    return card


def write_pdf(card: Image.Image) -> None:
    QA_IMAGE.parent.mkdir(parents=True, exist_ok=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    card.save(QA_IMAGE, quality=96)

    c = canvas.Canvas(str(OUT_PDF), pagesize=(180, 252))
    c.setTitle("Wand of True Strike - Item Card")
    c.setAuthor("Aetheria Campaign")
    c.setSubject("Front-only Nimble item card with cut edge")
    c.drawImage(str(QA_IMAGE), 0, 0, width=180, height=252, preserveAspectRatio=False, mask="auto")
    c.setStrokeColor(HexColor("#151515"))
    c.setLineWidth(0.45)
    c.rect(0.45, 0.45, 179.1, 251.1, stroke=1, fill=0)
    c.showPage()
    c.save()


if __name__ == "__main__":
    write_pdf(make_card())
    print(OUT_PDF)
