"""
Image 4: Protein Score Card
"""
from PIL import Image, ImageDraw, ImageFont
import json

BG        = "#FFFDF7"
HEADER_BG = "#023E8A"
TEXT_LITE = "#FFFFFF"
TEXT_DARK = "#1B1B1B"
BAR_FILL  = "#0096C7"
BAR_BG    = "#CAF0F8"
GOLD      = "#FFB703"

W, H = 900, 1000

def font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else \
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def draw_bar(draw, y, label, current, target, color):
    draw.text((60, y), label, font=font(17, True), fill=TEXT_DARK)
    # Bar background
    draw.rectangle([60, y+30, 820, y+62], fill=BAR_BG)
    # Bar fill
    fill_w = int(760 * min(current / target, 1.0))
    draw.rectangle([60, y+30, 60+fill_w, y+62], fill=color)
    # Labels
    draw.text((835, y+46), f"{current}g / {target}g", font=font(14), fill=TEXT_DARK, anchor="lm")
    pct = int(100 * current / target)
    draw.text((60+fill_w-5, y+46), f"{pct}%", font=font(12, True), fill=TEXT_LITE, anchor="rm")

def generate():
    with open("data/weekly_meal_plan.json") as f:
        data = json.load(f)
    with open("data/protein_options.json") as f:
        pdata = json.load(f)

    score    = data["protein_score"]
    avg      = data["protein_avg_daily_g"]
    month    = data["month"]
    targets  = pdata["target_daily_grams"]
    proteins = [p["name"] for p in pdata["daily_protein_options"]]

    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 100], fill=HEADER_BG)
    draw.text((W//2, 36), "💪  Weekly Protein Score", font=font(30, True), fill=TEXT_LITE, anchor="mm")
    draw.text((W//2, 74), f"{month}  ·  Family Protein Tracking", font=font(16), fill="#90E0EF", anchor="mm")

    # Big score circle
    cx, cy, r = W//2, 220, 90
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=HEADER_BG)
    draw.text((cx, cy-18), str(score), font=font(56, True), fill=GOLD, anchor="mm")
    draw.text((cx, cy+38), "/ 10", font=font(20), fill="#90E0EF", anchor="mm")
    draw.text((cx, cy+72), "Weekly Score", font=font(15), fill=TEXT_DARK, anchor="mm")
    draw.text((cx, cy+100), f"Avg {avg}g protein/day added", font=font(14), fill="#555", anchor="mm")

    # Per-member bars
    draw.text((60, 340), "Per Member Daily Target vs Estimated", font=font(18, True), fill=TEXT_DARK)
    y = 375
    colors = ["#0096C7","#00B4D8","#48CAE4","#90E0EF","#023E8A","#0077B6"]
    for i, (member, target) in enumerate(targets.items()):
        est = min(avg + (10 if member in ["Dad","Varun"] else 0), target)
        draw_bar(draw, y, member, est, target, colors[i % len(colors)])
        y += 88

    # Suggestions
    y += 10
    draw.rectangle([40, y, W-40, y+44], fill=HEADER_BG)
    draw.text((W//2, y+22), "💡  Top Protein Boosters This Week", font=font(17, True), fill=TEXT_LITE, anchor="mm")
    y += 50
    for i, p in enumerate(proteins[:4]):
        draw.text((80 + (i % 2)*420, y + (i//2)*38), f"✓  {p}", font=font(16), fill=TEXT_DARK)

    # Footer
    draw.rectangle([0, H-50, W, H], fill=HEADER_BG)
    draw.text((W//2, H-25), "Parivaar Nutrition AI  ·  Protein is the priority",
              font=font(13), fill="#90E0EF", anchor="mm")

    img.save("protein_card.png")
    print("✅ protein_card.png saved")

if __name__ == "__main__":
    generate()
