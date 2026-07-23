from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image, ImageEnhance, ImageFilter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "Campaigns" / "Nimble" / "Items"
TMP = ROOT / "tmp" / "pdfs" / "shadow-axe"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(parents=True, exist_ok=True)

W, H = 3.5 * 72, 5 * 72
CREAM = HexColor("#F3E6BF")
PAPER = HexColor("#FAF3DD")
INK = HexColor("#18212B")
TEAL = HexColor("#0C9B9A")
GOLD = HexColor("#F3B51B")
MINT = HexColor("#9CD2C2")
SHADOW = HexColor("#332A44")


def prep_art():
    src = ROOT / "img" / "Warren's Want" / "Snaggletooth the Destroyer.webp"
    im = Image.open(src).convert("RGB")
    # Crop around the shadow axe and wielder, then mute it into the established card palette.
    crop = im.crop((0, 345, 700, 1045)).resize((900, 900), Image.Resampling.LANCZOS)
    crop = ImageEnhance.Color(crop).enhance(0.58)
    crop = ImageEnhance.Contrast(crop).enhance(1.08)
    crop = crop.filter(ImageFilter.GaussianBlur(0.3))
    path = TMP / "shadow-axe-art.jpg"
    crop.save(path, quality=92)
    return path


def fit_lines(c, text, font, size, width):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if c.stringWidth(trial, font, size) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def paragraph(c, text, x, y, width, font="Helvetica", size=7.25, leading=8.6, color=INK):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in fit_lines(c, text, font, size, width):
        c.drawString(x, y, line)
        y -= leading
    return y


def base(c, title, subtitle, side_label=None):
    c.setFillColor(CREAM); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setStrokeColor(HexColor("#8A7956")); c.setLineWidth(2); c.rect(9, 9, W-18, H-18, fill=0, stroke=1)
    c.setStrokeColor(INK); c.setLineWidth(.7); c.rect(12, 12, W-24, H-24, fill=0, stroke=1)
    c.setStrokeColor(TEAL); c.setLineWidth(1.25)
    c.line(17, 20, 17, 40); c.line(17, 20, 38, 20)
    c.line(W-17, 20, W-17, 40); c.line(W-38, 20, W-17, 20)
    c.line(17, H-20, 17, H-40); c.line(17, H-20, 38, H-20)
    c.line(W-17, H-20, W-17, H-40); c.line(W-38, H-20, W-17, H-20)
    c.setFillColor(TEAL); c.rect(7, H-24, W-14, 15, fill=1, stroke=0)
    c.setFillColor(INK); c.rect(16, H-104, W-32, 76, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Times-Bold", 16)
    lines = title.split("\n")
    y = H-55 if len(lines) == 2 else H-67
    for line in lines:
        c.drawCentredString(W/2, y, line); y -= 19
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 5.6)
    c.drawCentredString(W/2, H-96, subtitle)
    if side_label:
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 5.3)
        c.drawRightString(W-20, H-16, side_label)


def section_box(c, y_top, y_bottom, label, accent=TEAL):
    c.setFillColor(PAPER); c.setStrokeColor(INK); c.setLineWidth(1)
    c.rect(18, y_bottom, W-36, y_top-y_bottom, fill=1, stroke=1)
    c.setFillColor(accent); c.rect(18, y_top-25, W-36, 25, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Times-Bold", 9)
    c.drawString(25, y_top-17, label)


def draw_front(c, art):
    base(c, "AXE OF\nSNAGGLETOOTH", "LEGENDARY ARTIFACT  |  BATTLEAXE  |  BERSERKER", "FRONT")
    # Art panel
    c.saveState()
    c.setFillColor(MINT); c.circle(W/2, 200, 55, fill=1, stroke=0)
    c.circle(W/2, 200, 48, fill=0, stroke=0)
    c.drawImage(ImageReader(str(art)), W/2-47, 153, 94, 94, preserveAspectRatio=True, mask='auto')
    c.setStrokeColor(TEAL); c.setLineWidth(1.3); c.circle(W/2, 200, 49, fill=0, stroke=1)
    c.restoreState()
    c.setFillColor(SHADOW); c.setFont("Helvetica-Oblique", 6.8)
    c.drawCentredString(W/2, 139, '"Welcome, friend. Let\'s drink the light together."')
    section_box(c, 126, 39, "WEAPON POWER")
    y = 92
    y = paragraph(c, "3d4 slashing. Two-handed. Requires STR 2.", 27, y, W-54, "Helvetica-Bold", 7.6, 9.2)
    y -= 4
    y = paragraph(c, "BONDED RETURN: After a thrown attack, the axe dissolves into shadow and returns to your hand at the end of the turn.", 27, y, W-54, size=7.15, leading=8.2)
    y -= 3
    paragraph(c, "THROWN RANGE: STR spaces (improvised weapon ruling).", 27, y, W-54, size=7.15, leading=8.2)
    c.setFillColor(SHADOW); c.setFont("Helvetica-Oblique", 5.7)
    c.drawCentredString(W/2, 24, "It feels safe. That is part of the danger.")
    c.setFillColor(TEAL); c.setFont("Helvetica-Bold", 4.8)
    c.drawString(18, 14, "INDEPENDENT NIMBLE HOMEBREW")
    c.showPage()


def stage(c, y, n, name, text, fill):
    c.setFillColor(fill); c.roundRect(24, y-17, 28, 16, 4, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 6.2); c.drawCentredString(38, y-12, n)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 6.2); c.drawString(58, y-7, name)
    paragraph(c, text, 58, y-16, W-82, size=5.25, leading=5.9)


def draw_back(c):
    base(c, "THE SHADOW\nBOND", "CURSED ARTIFACT  |  SHADOW POINTS  |  GM RULES", "BACK")
    c.setFillColor(SHADOW); c.setFont("Helvetica-Oblique", 6.7)
    c.drawCentredString(W/2, H-118, "The blade grows stronger as its friendship deepens.")
    section_box(c, H-130, 26, "CORRUPTION TRACK", accent=SHADOW)
    y = H-163
    y = paragraph(c, "GAIN 1 SHADOW POINT when the bonded bearer is reduced to 0 HP (maximum once per encounter).", 27, y, W-54, "Helvetica-Bold", 6.05, 6.8)
    y -= 2
    y = paragraph(c, "TEMPTATION (1/encounter): After rolling damage, accept +1d4 damage and gain 1 Shadow Point.", 27, y, W-54, size=5.85, leading=6.6)
    y -= 4
    stage(c, y, "0-1", "FRIEND", "3d4; telepathy; Bonded Return.", TEAL); y -= 24
    stage(c, y, "2-3", "HUNGER", "Temptation also grants temporary HP equal to STR.", HexColor("#69778A")); y -= 26
    stage(c, y, "4-5", "ASCENSION", "4d4. Rage start: DC 12 Will or pursue the nearest visible foe this turn.", HexColor("#584A68")); y -= 29
    stage(c, y, "6", "ECLIPSE", "The axe speaks through you. Encounter start: DC 12 Will or the GM chooses your first action.", SHADOW)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 6.2)
    c.drawString(27, 45, "BREAKING THE BOND")
    paragraph(c, "Cannot be discarded willingly. The Shadow Well can strip its power; cost set by the GM.", 27, 37, W-54, size=4.85, leading=5.2)
    c.setFillColor(TEAL); c.setFont("Helvetica-Bold", 4.8)
    c.drawString(18, 14, "INDEPENDENT NIMBLE HOMEBREW")
    c.showPage()


def make_card_pdf(path):
    art = prep_art(); c = canvas.Canvas(str(path), pagesize=(W, H), pageCompression=1)
    draw_front(c, art); draw_back(c); c.save()


def make_letter_pdf(path, card_path):
    from pypdf import PdfReader, PdfWriter, Transformation
    src = PdfReader(str(card_path)); writer = PdfWriter()
    for page in src.pages:
        sheet = writer.add_blank_page(width=letter[0], height=letter[1])
        x = (letter[0]-W)/2; y = (letter[1]-H)/2
        sheet.merge_transformed_page(page, Transformation().translate(x, y))
    with open(path, "wb") as f: writer.write(f)


if __name__ == "__main__":
    card = OUT / "axe-of-snaggletooth-card-3.5x5.pdf"
    letter_path = OUT / "axe-of-snaggletooth-card-letter.pdf"
    make_card_pdf(card); make_letter_pdf(letter_path, card)
    print(card); print(letter_path)
