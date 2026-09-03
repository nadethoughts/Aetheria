from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import portrait
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Paragraph


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "Shadow Axe - Kharum Vhar Tarot Card.pdf"
AXE_ART = ROOT / "output" / "imagegen" / "Shadow Axe" / "Kharum Vhar - Ink and Watercolor.png"
PAGE = portrait((70 * mm, 120 * mm))
W, H = PAGE

INK = colors.HexColor("#E7E1D2")
MUTED = colors.HexColor("#A89F8D")
SHADOW = colors.HexColor("#080A0D")
PANEL = colors.HexColor("#11151A")
PANEL_2 = colors.HexColor("#171C21")
IRON = colors.HexColor("#46505B")
RUNE = colors.HexColor("#8E2F35")
EMBER = colors.HexColor("#C35A38")
FROST = colors.HexColor("#7FA9BA")
STORM = colors.HexColor("#8B79B7")
STONE = colors.HexColor("#8A7E68")


def pstyle(name, size, leading=None, color=INK, align=TA_LEFT, font="Helvetica"):
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=leading or size * 1.18,
        textColor=color,
        alignment=align,
        spaceAfter=0,
        spaceBefore=0,
    )


BODY = pstyle("body", 6.8, 8.1)
SMALL = pstyle("small", 5.9, 7.0, MUTED)
SMALL_INK = pstyle("small_ink", 5.9, 7.0, INK)
LABEL = pstyle("label", 6.5, 7.5, colors.HexColor("#D79B75"), font="Helvetica-Bold")
TITLE = pstyle("title", 14, 15, INK, TA_CENTER, "Times-Bold")
BACK_TITLE = pstyle("back_title", 12.2, 13.0, INK, TA_CENTER, "Times-Bold")
SUBTITLE = pstyle("subtitle", 6.2, 7.2, MUTED, TA_CENTER, "Helvetica-Bold")
QUOTE = pstyle("quote", 7.3, 8.5, colors.HexColor("#E4C7A2"), TA_CENTER, "Times-Italic")


def rounded_panel(c, x, y, w, h, fill=PANEL, stroke=IRON, radius=2.2 * mm, width=0.55):
    c.setLineWidth(width)
    c.setFillColor(fill)
    c.setStrokeColor(stroke)
    c.roundRect(x, y, w, h, radius, fill=1, stroke=1)


def paragraph(c, html, style, x, y_top, w, h):
    para = Paragraph(html, style)
    pw, ph = para.wrap(w, h)
    para.drawOn(c, x, y_top - ph)
    return ph


def centered_text(c, text, font, size, x, y, color=INK):
    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(x - stringWidth(text, font, size) / 2, y, text)


def background(c):
    c.setFillColor(SHADOW)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Subtle rising shadow rays.
    c.setFillColor(colors.HexColor("#0E1217"))
    c.wedge(-28 * mm, -28 * mm, 55 * mm, 55 * mm, 15, 18, fill=1, stroke=0)
    c.wedge(22 * mm, -22 * mm, 100 * mm, 65 * mm, 125, 16, fill=1, stroke=0)

    # Double border sized to remain visible after trimming.
    c.setStrokeColor(colors.HexColor("#5D3235"))
    c.setLineWidth(1.1)
    c.roundRect(2.1 * mm, 2.1 * mm, W - 4.2 * mm, H - 4.2 * mm, 3 * mm, fill=0, stroke=1)
    c.setStrokeColor(IRON)
    c.setLineWidth(0.45)
    c.roundRect(3.1 * mm, 3.1 * mm, W - 6.2 * mm, H - 6.2 * mm, 2.5 * mm, fill=0, stroke=1)


def draw_axe_art(c):
    if not AXE_ART.exists():
        raise FileNotFoundError(f"Missing generated axe artwork: {AXE_ART}")

    # The source was generated as a wide parchment artifact illustration. Crop it
    # slightly to the card panel while preserving the hand-painted proportions.
    x, y, w, h = 4 * mm, 68 * mm, 62 * mm, 29 * mm
    c.saveState()
    clip = c.beginPath()
    clip.roundRect(x, y, w, h, 1.6 * mm)
    c.clipPath(clip, fill=0, stroke=0)
    c.drawImage(ImageReader(str(AXE_ART)), x, y, width=w, height=h,
                preserveAspectRatio=False, mask="auto")

    # Gentle edge shading integrates the pale parchment with the dark card.
    c.setFillColor(colors.Color(0.03, 0.04, 0.05, alpha=0.10))
    c.rect(x, y, w, 1.1 * mm, fill=1, stroke=0)
    c.rect(x, y + h - 1.1 * mm, w, 1.1 * mm, fill=1, stroke=0)
    c.restoreState()

    c.setStrokeColor(colors.HexColor("#6E5A50"))
    c.setLineWidth(0.55)
    c.roundRect(x, y, w, h, 1.6 * mm, fill=0, stroke=1)


def front(c):
    background(c)
    paragraph(c, "KHARUM VHAR", TITLE, 5 * mm, H - 7 * mm, W - 10 * mm, 18 * mm)
    paragraph(c, "THE MOUNTAIN'S FINAL WORD", SUBTITLE, 5 * mm, H - 18.5 * mm, W - 10 * mm, 9 * mm)
    draw_axe_art(c)

    rounded_panel(c, 5 * mm, 54.3 * mm, 60 * mm, 11.2 * mm, colors.HexColor("#151319"), colors.HexColor("#63333B"))
    paragraph(c, '"Welcome, friend. Let\'s drink the light together."', QUOTE,
              7 * mm, 62.2 * mm, 56 * mm, 8 * mm)

    # Weapon stat line.
    rounded_panel(c, 5 * mm, 43.0 * mm, 60 * mm, 8.8 * mm, PANEL_2, IRON)
    paragraph(c, "<b>GIANT-FORGED BATTLEAXE</b>  |  <b>3d4 + STR</b> slashing<br/>"
                 "Darkvision 6. Resizes to its bearer. Returns in about 30 minutes.",
              SMALL_INK, 7 * mm, 49.7 * mm, 56 * mm, 7 * mm)

    paragraph(c, "THE AXE'S BARGAINS", pstyle("front_label", 6.1, 7.0, colors.HexColor("#D79B75"), font="Helvetica-Bold"),
              6 * mm, 42.1 * mm, 58 * mm, 6 * mm)
    rounded_panel(c, 5 * mm, 12.8 * mm, 60 * mm, 26.3 * mm, PANEL, IRON)
    y = 36.8 * mm
    items = [
        ("CERTAINTY OF STONE", "After an axe miss, reroll it."),
        ("THE GIANT MOVES", "Gain 1 Action immediately."),
        ("ASCENDANT EDGE", "After an axe crit, next attack becomes 3d6."),
        ("NO ROOM FOR PAIN", "On gaining Wounds: Rage free and move half Speed."),
    ]
    for title, desc in items:
        h = paragraph(c, f"<b>{title}</b> - {desc}", BODY, 7 * mm, y, 56 * mm, 8 * mm)
        y -= h + 1.0 * mm

    rounded_panel(c, 5 * mm, 5 * mm, 60 * mm, 5.7 * mm, colors.HexColor("#211418"), colors.HexColor("#7E3842"), 1.8 * mm)
    paragraph(c, "Each bargain: <b>+1 SHADOW POINT</b> | 1/encounter each",
              pstyle("costline", 5.4, 6.0, INK, TA_CENTER), 7 * mm, 9.0 * mm, 56 * mm, 4.5 * mm)


def tier_box(c, y, number, title, threshold, gift, accent, height=13.2 * mm):
    rounded_panel(c, 5 * mm, y, 60 * mm, height, PANEL, accent, 1.8 * mm, 0.7)
    c.setFillColor(accent)
    c.circle(9.6 * mm, y + height - 4.1 * mm, 2.7 * mm, fill=1, stroke=0)
    centered_text(c, str(number), "Helvetica-Bold", 6.4, 9.6 * mm, y + height - 5.9 * mm, SHADOW)
    paragraph(c, f"<b>{title}</b>  <font color='#A89F8D'>{threshold}</font>",
              LABEL, 13.5 * mm, y + height - 2.0 * mm, 49 * mm, 7 * mm)
    paragraph(c, gift, SMALL_INK, 7 * mm, y + height - 7.0 * mm, 56 * mm, height - 7 * mm)


def back(c):
    background(c)
    paragraph(c, "THE SHADOW WITHIN", BACK_TITLE, 5 * mm, H - 10.5 * mm, W - 10 * mm, 15 * mm)
    paragraph(c, "KHARUM VHAR'S PROMISE OF ASCENSION", SUBTITLE, 5 * mm, H - 21.5 * mm, W - 10 * mm, 8 * mm)

    # Current track marker.
    rounded_panel(c, 5 * mm, 86.8 * mm, 60 * mm, 8.7 * mm, colors.HexColor("#211418"), colors.HexColor("#7E3842"))
    paragraph(c, "<b>CURRENT: 3 SHADOW POINTS</b>  |  Next awakening at 7",
              pstyle("current", 7.1, 8.3, colors.HexColor("#F0D0B7"), TA_CENTER, "Helvetica-Bold"),
              7 * mm, 93.0 * mm, 56 * mm, 6 * mm)

    tier_box(c, 73.5 * mm, 1, "THE WELCOME", "0-6", "Darkvision 6; bargains; Soul Draught after the axe feeds.", RUNE, 11.2 * mm)
    tier_box(c, 59.7 * mm, 2, "WEIGHT OF STONE", "7-12", "Count as one size larger for feats of strength. Max damage to objects. Push through foes.", STONE)
    tier_box(c, 45.9 * mm, 3, "ELEMENTAL CROWN", "13-17", "On Rage choose Ash, Frost, Storm, or Stone. Ascendant Edge can become 3d8.", STORM)
    tier_box(c, 32.1 * mm, 4, "WORLDBREAKER", "18-21", "Become immovable while Raging. Sweep every chosen creature within Reach 2.", EMBER)
    tier_box(c, 18.3 * mm, 5, "THE UNMADE SUN", "22-24", "Grow one size on Rage; wield two elements; Drink the Day to heal through ruin.", FROST)

    rounded_panel(c, 5 * mm, 4.2 * mm, 60 * mm, 11.3 * mm, colors.HexColor("#251015"), colors.HexColor("#A23F49"), 2 * mm, 1.0)
    paragraph(c, "<b>25 - THE MOUNTAIN'S FINAL WORD</b>",
              pstyle("lost", 7.1, 8.0, colors.HexColor("#F2C4B9"), TA_CENTER, "Helvetica-Bold"),
              7 * mm, 13.4 * mm, 56 * mm, 5 * mm)
    paragraph(c, "The ascension completes. Rubius becomes an elemental-shadow giant and a campaign antagonist.",
              pstyle("lost2", 6.1, 7.0, INK, TA_CENTER),
              8 * mm, 9.3 * mm, 54 * mm, 5 * mm)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(OUT), pagesize=PAGE, pageCompression=1)
    c.setTitle("Shadow Axe - Kharum Vhar Tarot Card")
    c.setAuthor("Aetheria Campaign")
    c.setSubject("Nimble item card for Kharum Vhar, the Shadow Axe")

    front(c)
    c.showPage()
    back(c)
    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
