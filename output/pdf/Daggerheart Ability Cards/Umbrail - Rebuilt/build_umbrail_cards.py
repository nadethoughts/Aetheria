from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from pypdf import PdfReader, PdfWriter


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "source-images"
QA = ROOT / "qa"
QA.mkdir(parents=True, exist_ok=True)

CARDS = [
    ("01 - TALENTED RESEARCHER", "Talented Researcher"),
    ("02 - FORCE OF CHAOS", "Force of Chaos"),
    ("03 - HOLLOW BONES", "Hollow Bones"),
    ("04 - MADE A BAD CHOICE", "Made a Bad Choice"),
]

CARD_W_PT = 180.0
CARD_H_PT = 252.0
PRINT_W_PX = 750
PRINT_H_PX = 1050


def prepared_image(source: Path, destination: Path) -> None:
    with Image.open(source) as image:
        image = image.convert("RGB")
        image = image.resize((PRINT_W_PX, PRINT_H_PX), Image.Resampling.LANCZOS)
        image = image.filter(ImageFilter.UnsharpMask(radius=1.0, percent=65, threshold=3))
        image.save(destination, "PNG", optimize=True)


def make_card_pdf(image_path: Path, destination: Path, title: str) -> None:
    doc = canvas.Canvas(str(destination), pagesize=(CARD_W_PT, CARD_H_PT), pageCompression=1)
    doc.setTitle(f"Umbrail - {title}")
    doc.setSubject("Front-only print card rebuilt in the Daggerheart Card Creator")
    doc.setAuthor("Daggerheart Card Creator")
    doc.drawImage(ImageReader(str(image_path)), 0, 0, CARD_W_PT, CARD_H_PT, preserveAspectRatio=False)
    doc.setStrokeColorRGB(0.12, 0.12, 0.12)
    doc.setLineWidth(0.45)
    doc.rect(0.4, 0.4, CARD_W_PT - 0.8, CARD_H_PT - 0.8, stroke=1, fill=0)
    doc.showPage()
    doc.save()


def make_contact_sheet(prepared: list[tuple[Path, str]]) -> None:
    thumb_w, thumb_h = 375, 525
    label_h = 34
    margin = 24
    sheet = Image.new("RGB", (margin * 3 + thumb_w * 2, margin * 3 + (thumb_h + label_h) * 2), "#dedbd2")
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.load_default(size=20)
    for index, (image_path, title) in enumerate(prepared):
        with Image.open(image_path) as image:
            thumb = image.convert("RGB").resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        column = index % 2
        row = index // 2
        x = margin + column * (thumb_w + margin)
        y = margin + row * (thumb_h + label_h + margin)
        sheet.paste(thumb, (x, y))
        draw.text((x, y + thumb_h + 5), f"{index + 1:02d}  {title}", fill="#1d1d1d", font=font)
    sheet.save(QA / "Umbrail - Card Proof Sheet.png", optimize=True)


def main() -> None:
    prepared = []
    pdfs = []
    for stem, title in CARDS:
        source = SOURCE / f"{stem}.jpg"
        print_image = QA / f"{stem}.png"
        pdf_path = ROOT / f"{stem}.pdf"
        prepared_image(source, print_image)
        make_card_pdf(print_image, pdf_path, title)
        prepared.append((print_image, title))
        pdfs.append(pdf_path)

    make_contact_sheet(prepared)

    writer = PdfWriter()
    for pdf_path in pdfs:
        writer.append(PdfReader(str(pdf_path)))
    writer.add_metadata({
        "/Title": "Umbrail - Rebuilt Ability Cards",
        "/Subject": "Four front-only, card-sized print pages with cut edges",
        "/Author": "Daggerheart Card Creator",
    })
    with (ROOT / "Umbrail - Rebuilt Ability Cards.pdf").open("wb") as output:
        writer.write(output)


if __name__ == "__main__":
    main()
