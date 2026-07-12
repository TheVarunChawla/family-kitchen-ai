"""
Image 2: Weekly Shopping List.
"""
from PIL import Image, ImageDraw, ImageFont
import json
from theme import get_theme

THEME = get_theme()
BG = THEME["bg"]
HEADER_BG = THEME["header_bg"]
SEC_GREEN = "#2D6A4F"
SEC_ORG = "#E76F51"
SEC_BLUE = "#457B9D"
SEC_PURP = "#6A4C93"
TEXT_LITE = "#FFFFFF"
TEXT_DARK = "#1B1B1B"

W, H = 900, 1300


def font(size, bold=False):
    try:
        path = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def draw_section(draw, y, title, items, color):
    draw.rectangle([40, y, W - 40, y + 44], fill=color)
    draw.text((60, y + 22), title, font=font(18, True), fill=TEXT_LITE, anchor="lm")
    y += 50

    for item in items:
        draw.ellipse([60, y + 8, 74, y + 22], fill=color)
        draw.text((85, y + 6), item, font=font(16), fill=TEXT_DARK)
        y += 34
    return y + 14


def generate():
    with open("data/weekly_meal_plan.json") as f:
        data = json.load(f)

    shopping = data["shopping"]
    month = data["month"]

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 100], fill=HEADER_BG)
    draw.text((W // 2, 36), "Weekly Shopping List", font=font(30, True), fill=TEXT_LITE, anchor="mm")
    draw.text((W // 2, 76), f"{month}  |  Family of 6  |  Vegetarian", font=font(16), fill=THEME["header_sub"], anchor="mm")

    y = 120
    y = draw_section(draw, y, "Vegetables", shopping["vegetables"], SEC_GREEN)
    y = draw_section(draw, y, "Dals & Legumes", shopping["dals_legumes"], SEC_ORG)
    y = draw_section(draw, y, "Protein Sources", shopping["protein_sources"], SEC_BLUE)
    y = draw_section(draw, y, "Kitchen Essentials", shopping["kitchen_essentials"], SEC_PURP)

    draw.rectangle([0, H - 50, W, H], fill=HEADER_BG)
    draw.text((W // 2, H - 25), "Parivaar Nutrition AI  |  Auto-generated every Sunday", font=font(13), fill=THEME["header_sub"], anchor="mm")

    img.save("shopping_list.png")
    print("shopping_list.png saved")


if __name__ == "__main__":
    generate()
