from __future__ import annotations

import json
import math
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import landscape, letter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
WORKSPACE = ROOT.parents[3]
MANIFEST = ROOT / "batch_manifest.json"
SOURCE = ROOT / "source-images"
QA = ROOT / "qa"
QA.mkdir(parents=True, exist_ok=True)

CARD_W_PX, CARD_H_PX = 360, 504
CARD_W_PT, CARD_H_PT = 180, 252

FONT_REG = Path(r"C:\Windows\Fonts\arial.ttf")
FONT_BOLD = Path(r"C:\Windows\Fonts\arialbd.ttf")
FONT_ITALIC = Path(r"C:\Windows\Fonts\ariali.ttf")


def safe_name(value: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "-", value)


def crop_cover(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    tw, th = size
    scale = max(tw / img.width, th / img.height)
    resized = img.resize((round(img.width * scale), round(img.height * scale)), Image.Resampling.LANCZOS)
    x = max(0, (resized.width - tw) // 2)
    y = max(0, (resized.height - th) // 2)
    return resized.crop((x, y, x + tw, y + th))


def font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def fit_title(draw: ImageDraw.ImageDraw, text: str, max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(22, 13, -1):
        f = font(FONT_BOLD, size)
        if draw.textbbox((0, 0), text, font=f)[2] <= max_width:
            return f
    return font(FONT_BOLD, 13)


def wrap(draw: ImageDraw.ImageDraw, text: str, f: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines: list[str] = []
    for para in text.splitlines():
        if not para.strip():
            lines.append("")
            continue
        words = para.split()
        current = words.pop(0)
        for word in words:
            trial = current + " " + word
            if draw.textbbox((0, 0), trial, font=f)[2] <= width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_fitted_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    start_size: int = 13,
    min_size: int = 10,
) -> None:
    x0, y0, x1, y1 = box
    for size in range(start_size, min_size - 1, -1):
        f = font(FONT_REG, size)
        line_h = size + 3
        lines = wrap(draw, text, f, x1 - x0)
        if len(lines) * line_h <= y1 - y0:
            y = y0
            for line in lines:
                draw.text((x0, y), line, font=f, fill=(18, 18, 18))
                y += line_h
            return
    f = font(FONT_REG, min_size)
    line_h = min_size + 2
    y = y0
    for line in wrap(draw, text, f, x1 - x0):
        if y + line_h > y1:
            break
        draw.text((x0, y), line, font=f, fill=(18, 18, 18))
        y += line_h


def build_mei_sources(manifest: dict) -> None:
    mei = next(c for c in manifest["characters"] if c["name"] == "Mei Rong")
    out_dir = SOURCE / "Mei Rong"
    out_dir.mkdir(parents=True, exist_ok=True)
    portrait = Image.open(
        WORKSPACE / "Campaigns" / "Nimble" / "PCs" / "Ability Card Portraits" / "Mei Rong.png"
    ).convert("RGB")
    templates = {
        "Grace": WORKSPACE / "output" / "pdf" / "Daggerheart Ability Cards" / "Skritch - Rebuilt" / "source-images" / "06 - SWEET TALK.jpg",
        "Codex": WORKSPACE / "output" / "pdf" / "Daggerheart Ability Cards" / "Umbrail - Rebuilt" / "source-images" / "01 - TALENTED RESEARCHER.jpg",
        "Splendor": SOURCE / "Cai Lin" / "01 - MERCIFUL HEALING.jpg",
        "Valor": SOURCE / "Cai Lin" / "05 - RELENTLESS.jpg",
    }
    new_art = crop_cover(portrait, (352, 240))
    for index, card in enumerate(mei["cards"], 1):
        template = Image.open(templates[card["domain"]]).convert("RGB").resize(
            (CARD_W_PX, CARD_H_PX), Image.Resampling.LANCZOS
        )
        base = template.copy()
        base.paste(new_art, (4, 3))
        # Restore the creator's domain banner, hope/stress medallion, divider, border, and footer.
        overlay_mask = Image.new("L", (CARD_W_PX, CARD_H_PX), 0)
        mask_draw = ImageDraw.Draw(overlay_mask)
        mask_draw.polygon(
            [(17, 0), (91, 0), (91, 119), (83, 109), (58, 132), (37, 109), (17, 120)],
            fill=255,
        )
        mask_draw.ellipse((320, 14, 359, 59), fill=255)
        base.paste(template, (0, 0), overlay_mask)
        base.paste(template.crop((0, 239, 360, 275)), (0, 239))
        base.paste(template.crop((0, 0, 5, 504)), (0, 0))
        base.paste(template.crop((355, 0, 360, 504)), (355, 0))
        base.paste(template.crop((0, 0, 360, 5)), (0, 0))
        base.paste(template.crop((0, 477, 360, 504)), (0, 477))

        draw = ImageDraw.Draw(base)
        draw.rectangle((5, 271, 354, 477), fill=(255, 255, 253))
        title_f = fit_title(draw, card["title"], 326)
        tb = draw.textbbox((0, 0), card["title"], font=title_f)
        draw.text(((360 - (tb[2] - tb[0])) / 2, 278), card["title"], font=title_f, fill=(12, 12, 12))

        meta_f = font(FONT_REG, 12)
        meta_lines = wrap(draw, card["meta"], meta_f, 324)
        y = 330
        for line in meta_lines:
            draw.text((18, y), line, font=meta_f, fill=(25, 25, 25))
            y += 15
        y += 5
        draw_fitted_block(draw, card["rules"], (18, y, 342, 470), 13, 10)

        draw.rectangle((8, 479, 128, 501), fill=(255, 255, 253))
        draw.text((18, 485), "Mei Rong portrait", font=font(FONT_ITALIC, 8), fill=(45, 45, 45))
        base = base.filter(ImageFilter.UnsharpMask(radius=0.6, percent=45, threshold=3))
        out = out_dir / f"{index:02d} - {safe_name(card['title'])}.jpg"
        base.save(out, quality=96, subsampling=0)


def build_character_pdf(character: dict) -> Path:
    name = character["name"]
    images = sorted((SOURCE / name).glob("*.jpg"))
    if len(images) != len(character["cards"]):
        raise RuntimeError(f"{name}: expected {len(character['cards'])} images, found {len(images)}")
    out = ROOT / f"{name} - Rebuilt Ability Cards.pdf"
    c = canvas.Canvas(str(out), pagesize=(CARD_W_PT, CARD_H_PT))
    c.setTitle(f"{name} - Rebuilt Ability Cards")
    c.setAuthor("Aetheria Campaign")
    c.setSubject("Front-only Daggerheart ability cards with cut edges")
    for img in images:
        c.drawImage(str(img), 0, 0, width=CARD_W_PT, height=CARD_H_PT, preserveAspectRatio=False, mask="auto")
        c.setStrokeColor(HexColor("#111111"))
        c.setLineWidth(0.45)
        c.rect(0.45, 0.45, CARD_W_PT - 0.9, CARD_H_PT - 0.9, stroke=1, fill=0)
        c.showPage()
    c.save()
    return out


def build_proof(manifest: dict) -> Path:
    out = ROOT / "Remaining Characters - Overall Ability Card Proof.pdf"
    page_w, page_h = landscape(letter)
    c = canvas.Canvas(str(out), pagesize=(page_w, page_h))
    c.setTitle("Remaining Characters - Overall Ability Card Proof")
    c.setAuthor("Aetheria Campaign")
    margin_x, top_y = 30, page_h - 52
    cols, rows = 4, 3
    card_h = 151.2
    card_w = card_h * CARD_W_PT / CARD_H_PT
    gap_x = (page_w - 2 * margin_x - cols * card_w) / (cols - 1)
    gap_y = 24
    per_page = cols * rows
    for character in manifest["characters"]:
        images = sorted((SOURCE / character["name"]).glob("*.jpg"))
        for chunk_start in range(0, len(images), per_page):
            chunk = images[chunk_start : chunk_start + per_page]
            c.setFillColor(HexColor("#182238"))
            c.setFont("Helvetica-Bold", 18)
            suffix = "" if len(images) <= per_page else f" — Cards {chunk_start + 1}-{chunk_start + len(chunk)}"
            c.drawString(margin_x, page_h - 28, character["name"] + suffix)
            c.setFont("Helvetica", 8)
            c.setFillColor(HexColor("#4A5568"))
            c.drawRightString(page_w - margin_x, page_h - 26, "Front-only proof • cut-edge border shown")
            for i, img in enumerate(chunk):
                row, col = divmod(i, cols)
                x = margin_x + col * (card_w + gap_x)
                y = top_y - card_h - row * (card_h + gap_y)
                c.drawImage(str(img), x, y, width=card_w, height=card_h, preserveAspectRatio=False, mask="auto")
                c.setStrokeColor(HexColor("#111111"))
                c.setLineWidth(0.35)
                c.rect(x, y, card_w, card_h, stroke=1, fill=0)
                title = character["cards"][chunk_start + i]["title"]
                c.setFillColor(HexColor("#182238"))
                c.setFont("Helvetica", 7)
                c.drawCentredString(x + card_w / 2, y - 10, f"{chunk_start + i + 1}. {title[:28]}")
            c.showPage()
    c.save()
    return out


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    build_mei_sources(manifest)
    outputs = [build_character_pdf(c) for c in manifest["characters"]]
    outputs.append(build_proof(manifest))
    print(f"Built {sum(len(c['cards']) for c in manifest['characters'])} fronts across {len(manifest['characters'])} characters.")
    for output in outputs:
        print(output)


if __name__ == "__main__":
    main()
