"""
Image 3: Health Recommendations — per member + family tip
"""
from PIL import Image, ImageDraw, ImageFont
import json, textwrap

BG        = "#FFFDF7"
HEADER_BG = "#6A0572"
TEXT_LITE = "#FFFFFF"
TEXT_DARK = "#1B1B1B"
TEXT_MED  = "#3D3D3D"

MEMBER_COLORS = {
    "Dad":     "#D62828",
    "Mom":     "#E07A5F",
    "Sister1": "#F2CC8F",
    "Sister2": "#81B29A",
    "Varun":   "#3D405B",
    "Wife":    "#E07A5F",
}
MEMBER_TEXT = {
    "Dad": "#FFFFFF", "Mom": "#FFFFFF", "Sister1": "#1B1B1B",
    "Sister2": "#1B1B1B", "Varun": "#FFFFFF", "Wife": "#FFFFFF"
}

W, H = 900, 1200

def font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else \
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def generate():
    with open("data/weekly_meal_plan.json") as f:
        data = json.load(f)

    tips       = data["health_tips"]
    family_tip = data["family_tip"]
    month      = data["month"]

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 100], fill=HEADER_BG)
    draw.text((W//2, 36), "💚  Family Health Recommendations", font=font(28, True), fill=TEXT_LITE, anchor="mm")
    draw.text((W//2, 74), f"{month}  ·  Personalised for Each Member", font=font(16), fill="#E0AAFF", anchor="mm")

    y = 120
    for member, tip in tips.items():
        color    = MEMBER_COLORS.get(member, "#888")
        tc       = MEMBER_TEXT.get(member, "#FFF")

        # Card background
        draw.rectangle([40, y, W-40, y+90], fill="#F8F8F8", outline=color, width=3)
        # Name badge
        draw.rectangle([40, y, 180, y+90], fill=color)
        draw.text((110, y+45), member, font=font(18, True), fill=tc, anchor="mm")

        lines = textwrap.wrap(tip, width=48)
        for li, line in enumerate(lines[:2]):
            draw.text((200, y+22+li*28), line, font=font(16), fill=TEXT_DARK)

        y += 104

    # Family tip box
    y += 10
    draw.rectangle([40, y, W-40, y+90], fill="#2D6A4F")
    draw.text((W//2, y+20), "🏠  Family Goal This Week", font=font(18, True), fill=TEXT_LITE, anchor="mm")
    lines = textwrap.wrap(family_tip, width=55)
    for li, line in enumerate(lines[:2]):
        draw.text((W//2, y+52+li*24), line, font=font(15), fill="#B7E4C7", anchor="mm")

    # Footer
    draw.rectangle([0, H-50, W, H], fill=HEADER_BG)
    draw.text((W//2, H-25), "Parivaar Nutrition AI  ·  Small changes, big health",
              font=font(13), fill="#E0AAFF", anchor="mm")

    img.save("health_card.png")
    print("✅ health_card.png saved")

if __name__ == "__main__":
    generate()
