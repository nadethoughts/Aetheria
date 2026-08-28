from __future__ import annotations

import io
import subprocess
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor, white
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

import build_accessible_character_packets as source

ROOT = Path(__file__).resolve().parent
PACKET = ROOT / "Session 08 - Temporary Player Characters - Complete Packet.pdf"
PAGE_W, PAGE_H = A4
INK, MUTED, LINE = HexColor("#17212B"), HexColor("#455665"), HexColor("#AAB8C2")
ICE, BLUE, GREEN = HexColor("#E9F2F6"), HexColor("#2F6F95"), HexColor("#39715D")
GOLD, RED = HexColor("#A56F19"), HexColor("#914B44")

MOTIVATIONS = {
    "Skritch": ("Survive, earn protection, and make the Black Fang pay for leaving you under the ice.", "Win kobolds safe territory and respect; do not trade one mountain ruler for another.", "The giant who sat on me. This is either very good luck or very bad luck."),
    "Da Long": ("Protect Quickfeather, repay Lil Chang for saving you, and prove your warning was worth hearing.", "Bring Frostvein into the resistance while preserving the Cloud Seers' honor and freedom of action.", "I was spying. I will not insult you by pretending otherwise. Razor's people shot first."),
    "Feng Rui": ("Keep your wardens and Cai Lin alive; never let outsiders turn your pass into their battlefield.", "Defend Frostvein sovereignty: An Yue controls the passes and foreign troops enter only by permission.", "Name what you want from our pass - and what you will give when winter closes behind you."),
    "Cai Lin": ("Save lives first, especially injured climbers and anyone abandoned because of politics.", "Choose the alliance that protects Frostvein people in deeds, not the side that wins the argument.", "Show me whom you protect when helping us costs you something."),
    "Jian Bo": ("Keep Frostvein fed, equipped, and moving through winter; demand concrete commitments.", "Avoid a war that empties the stores. Support only a pact backed by routes, supplies, labor, and mutual defense.", "Honor does not fill a storehouse. What arrives before the first deep snow?"),
    "Mei Rong": ("Make the full history heard; do not let Razor's threat erase the harm the Erie caused.", "Secure recognition of Frostvein independence and a formal hearing for its grievances.", "We can resist Razor without pretending the old order was just."),
}

FRONT_STATS = {
    "Skritch": ("S", "6", "+2", "6", "3d6", "21", "0 / 6"),
    "Da Long": ("M", "6", "+2", "5", "4d8", "28", "0 / 6"),
    "Feng Rui": ("M", "6", "-1", "14", "3d10", "34", "0 / 6"),
    "Cai Lin": ("M", "6", "-1", "10", "3d10", "34", "0 / 6"),
    "Jian Bo": ("M", "6", "+3", "1", "3d12", "42", "0 / 6"),
    "Mei Rong": ("M", "6", "+1", "5", "3d8", "26", "0 / 6"),
}

BODY = ParagraphStyle("compact-body", fontName="Helvetica", fontSize=8.55, leading=10.15, textColor=INK, alignment=TA_LEFT)
TAG = ParagraphStyle("compact-tag", parent=BODY, fontName="Helvetica-Bold", fontSize=7.15, leading=8.25, textColor=MUTED)
TITLE = ParagraphStyle("compact-title", parent=BODY, fontName="Helvetica-Bold", fontSize=9.1, leading=10.2)

def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\u2013", "-").replace("\u2014", "-").replace("\u00b7", " - ")

def ph(text, style, width):
    return Paragraph(text, style).wrap(width, PAGE_H)[1]

def draw_para(c, text, style, x, top, width):
    p = Paragraph(text, style); _, h = p.wrap(width, PAGE_H); p.drawOn(c, x, top-h); return h

def card_height(title, tag, bullets, width):
    inner = width - 14
    bt = "<br/>".join(f"<b>&#8226;</b> {esc(b)}" for b in bullets)
    return 14 + ph(esc(title), TITLE, inner) + ph(esc(tag), TAG, inner) + ph(bt, BODY, inner)

def draw_card(c, x, top, width, title, tag, bullets, accent):
    height = card_height(title, tag, bullets, width)
    c.setFillColor(white); c.setStrokeColor(LINE); c.setLineWidth(.55)
    c.roundRect(x, top-height, width, height, 4, fill=1, stroke=1)
    c.setFillColor(accent); c.roundRect(x, top-height, 4, height, 4, fill=1, stroke=0)
    y = top-6
    y -= draw_para(c, esc(title), TITLE, x+8, y, width-14)+1
    y -= draw_para(c, esc(tag), TAG, x+8, y, width-14)+2
    draw_para(c, "<br/>".join(f"<b>&#8226;</b> {esc(b)}" for b in bullets), BODY, x+8, y, width-14)
    return height

def draw_header(c, name, char):
    c.setFillColor(INK); c.rect(0, PAGE_H-55, PAGE_W, 55, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 18); c.drawString(25, PAGE_H-25, name.upper())
    c.setFont("Helvetica-Bold", 8.5); c.drawString(25, PAGE_H-42, esc(char["subtitle"]))
    c.setFillColor(ICE); c.setFont("Helvetica-Bold", 7.2)
    c.drawRightString(PAGE_W-25, PAGE_H-22, "COMPLETE PLAY RULES")
    c.drawRightString(PAGE_W-25, PAGE_H-39, esc(char["stats"]))

def draw_motivation_band(c, name):
    personal, tribal, line = MOTIVATIONS[name]
    x, top, width = 25, PAGE_H-65, PAGE_W-50; col = (width-12)/2
    c.setFillColor(HexColor("#FFF8E8")); c.setStrokeColor(GOLD); c.roundRect(x, top-83, width, 83, 5, fill=1, stroke=1)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 8)
    c.drawString(x+8, top-13, "PERSONAL MOTIVATION"); c.drawString(x+col+12, top-13, "TRIBAL MOTIVATION")
    draw_para(c, esc(personal), BODY, x+8, top-18, col-12); draw_para(c, esc(tribal), BODY, x+col+12, top-18, col-12)
    c.setStrokeColor(HexColor("#D8BF8C")); c.line(x+8, top-55, x+width-8, top-55)
    draw_para(c, f"<b>OPEN WITH:</b> {esc(line)}", BODY, x+8, top-61, width-16)
    return top-91

def ability_accent(title):
    if any(k in title for k in ("HEAL", "PROTECT", "SHIELD", "RELENTLESS", "REST")): return GREEN
    if any(k in title for k in ("ATTACK", "STRIKE", "THROAT", "MOCKERY", "LANCE", "TOUCH", "RAGE")): return RED
    return BLUE

def category_for(title, tag, bullets):
    text = " ".join([title, tag, *bullets]).upper()
    if any(k in text for k in ("HEAL", "INSPIRE", "FIELD MEDIC", "TEMP HP", "ALLY REROLLS", "SONG OF REST")):
        return "SUPPORT"
    if any(k in title for k in ("SHIELD", "PROTECT", "RELENTLESS", "WILY", "ARMOR", "HOLD THE LINE", "TENACITY", "FEARLESS", "THAT ALL")):
        return "DEFENSE"
    if any(k in title for k in ("REPOSITION", "ROLL & STRIKE", "BLOODLUST", "HIDING", "FEATHER FALL", "ICE DISK", "PROTECT ME")):
        return "MOVEMENT"
    if any(k in text for k in ("DAMAGE", "ATTACK", "CRIT", "WEAPON", "CANTRIP", "THRILL", "FURY", "RAGE", "TRAP")):
        return "ATTACK"
    return "PASSIVE / UTILITY"

def category_color(category):
    return {"ATTACK": RED, "DEFENSE": GREEN, "MOVEMENT": BLUE, "SUPPORT": GOLD, "PASSIVE / UTILITY": MUTED}[category]

def draw_icon(c, category, x, y, size, color=white):
    c.saveState(); c.setStrokeColor(color); c.setFillColor(color); c.setLineWidth(1.4)
    if category == "ATTACK":
        c.line(x+3, y+3, x+size-3, y+size-3); c.line(x+size-7, y+size-3, x+size-3, y+size-3); c.line(x+size-3, y+size-7, x+size-3, y+size-3)
        c.line(x+2, y+6, x+6, y+2)
    elif category == "DEFENSE":
        p=c.beginPath(); p.moveTo(x+size/2,y+size-2); p.lineTo(x+size-2,y+size-5); p.lineTo(x+size-4,y+4); p.lineTo(x+size/2,y+1); p.lineTo(x+4,y+4); p.lineTo(x+2,y+size-5); p.close(); c.drawPath(p,fill=0,stroke=1)
    elif category == "MOVEMENT":
        c.line(x+2,y+size/2,x+size-3,y+size/2); c.line(x+size-7,y+size-4,x+size-3,y+size/2); c.line(x+size-7,y+4,x+size-3,y+size/2)
    elif category == "SUPPORT":
        c.rect(x+size*.4,y+2,size*.2,size-4,fill=1,stroke=0); c.rect(x+2,y+size*.4,size-4,size*.2,fill=1,stroke=0)
    else:
        c.circle(x+size/2,y+size/2,size*.28,fill=0,stroke=1); c.circle(x+size/2,y+size/2,1.4,fill=1,stroke=0)
    c.restoreState()

def draw_category_header(c, x, top, width, category):
    color=category_color(category); h=22
    c.setFillColor(color); c.roundRect(x, top-h, width, h, 4, fill=1, stroke=0)
    draw_icon(c, category, x+7, top-h+4, 14)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 9.2); c.drawString(x+27, top-15, category)
    return h

def draw_rules_page(name, char):
    out = io.BytesIO(); c = canvas.Canvas(out, pagesize=A4, pageCompression=1)
    draw_header(c, name, char); start_top = draw_motivation_band(c, name)
    margin, gutter = 25, 10; col_w = (PAGE_W-2*margin-gutter)/2
    cols = [[margin+i*(col_w+gutter), start_top] for i in range(2)]
    plan = ("TURN PLAN", "DO THESE IN ORDER", [s.replace("<b>", "").replace("</b>", "") for s in char["quick"]], GOLD)
    grouped = {k: [] for k in ("ATTACK", "DEFENSE", "MOVEMENT", "SUPPORT", "PASSIVE / UTILITY")}
    for t, tag, bullets in char["abilities"]:
        grouped[category_for(t, tag, bullets)].append((t, tag, bullets))
    grouped["PASSIVE / UTILITY"].insert(0, plan[:3])
    for category in grouped:
        if not grouped[category]: continue
        group_height = 27 + sum(card_height(t, tag, bullets, col_w)+5 for t, tag, bullets in grouped[category])
        idx = max(range(2), key=lambda i: cols[i][1]); x, y = cols[idx]
        cols[idx][1] -= draw_category_header(c, x, y, col_w, category)+5
        for title, tag, bullets in grouped[category]:
            y = cols[idx][1]
            cols[idx][1] -= draw_card(c, x, y, col_w, title, tag, bullets, category_color(category))+5
    lowest = min(v[1] for v in cols)
    if lowest < 22: raise RuntimeError(f"{name} rules overflow page by {22-lowest:.1f} points")
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 6.2)
    c.drawString(25, 10, "Icons: attack / defense / movement / support / passive or utility.")
    c.drawRightString(PAGE_W-25, 10, "Session 08 temporary character")
    c.save(); out.seek(0); return PdfReader(out).pages[0]

def draw_front_identity_overlay(name, char):
    out = io.BytesIO(); c = canvas.Canvas(out, pagesize=A4, pageCompression=1)
    # Slim banner replaces only the original class bar; the subclass line and
    # illustrated Size-Wounds row remain untouched below it.
    c.setFillColor(white); c.rect(150, 800, PAGE_W-150, 42, fill=1, stroke=0)
    c.rect(540, 790, PAGE_W-540, 52, fill=1, stroke=0)
    c.setFillColor(INK); c.rect(158, 812, PAGE_W-175, 24, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 14); c.drawString(168, 820, name.upper())
    c.setFillColor(ICE); c.setFont("Helvetica-Bold", 6.2); c.drawRightString(PAGE_W-28, 821, esc(char["subtitle"]))
    c.setFillColor(white); c.rect(150, 0, PAGE_W-150, 300, fill=1, stroke=0)
    c.setFillColor(MUTED); c.setFont("Helvetica-Oblique", 6.2); c.drawRightString(PAGE_W-18, 8, "Character abilities continue on page 2.")
    c.save(); out.seek(0); return PdfReader(out).pages[0]

def clean_head_first_page(char):
    repo = ROOT.parents[2]
    rel = f"output/pdf/Session 08 Temporary Characters/{char['file']}"
    blob = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=repo, check=True, capture_output=True).stdout
    return PdfReader(io.BytesIO(blob)).pages[0]

def build_one(name, char):
    target = ROOT/char["file"]; first = clean_head_first_page(char)
    first.merge_page(draw_front_identity_overlay(name, char))
    writer = PdfWriter(); writer.add_page(first); writer.add_page(draw_rules_page(name, char))
    for page in writer.pages: page.compress_content_streams()
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    writer.add_metadata({"/Title": f"{name} - Level 3 Temporary PC", "/Subject": "Compact, accessible two-page Nimble character sheet", "/Creator": "Codex using local Nimble-Rules sources"})
    staged = ROOT/(target.stem+".staged.pdf")
    with staged.open("wb") as f: writer.write(f)
    staged.replace(target)

def build_packet():
    writer = PdfWriter()
    for char in source.CHARACTERS.values():
        reader = PdfReader(str(ROOT/char["file"]))
        for page in reader.pages: writer.add_page(page)
    for page in writer.pages: page.compress_content_streams()
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    writer.add_metadata({"/Title": "Session 08 - Temporary Player Characters - Complete Packet", "/Subject": "Six compact, accessible two-page Nimble character sheets"})
    staged = ROOT/(PACKET.stem+".staged.pdf")
    with staged.open("wb") as f: writer.write(f)
    staged.replace(PACKET)

if __name__ == "__main__":
    for character_name, character in source.CHARACTERS.items(): build_one(character_name, character)
    build_packet(); print(f"Built {len(source.CHARACTERS)} compact two-page character sheets and complete packet.")
