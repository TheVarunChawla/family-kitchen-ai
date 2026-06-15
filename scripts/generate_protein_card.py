"""
Image 4: Protein Score Card
Reads weekly_meal_plan.json + nutrition_database.json
Detects protein foods in scored meal sections
Calculates real weekly protein points -> realistic score out of 10
"""
from PIL import Image, ImageDraw, ImageFont
import json

BG        = "#FFFDF7"
HEADER_BG = "#023E8A"
TEXT_LITE = "#FFFFFF"
TEXT_DARK = "#1B1B1B"
TEXT_MED  = "#555555"
BAR_FILL  = "#0096C7"
BAR_BG    = "#CAF0F8"
GOLD      = "#FFB703"
GREEN     = "#2D6A4F"
GREEN_LT  = "#B7E4C7"

W, H = 900, 1120

def font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else \
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        return ImageFont.truetype(path, size)
    except:
        return ImageFont.load_default()

def detect_protein_in_text(text, nutrition_db):
    """
    Scan a meal string for any food that exists in nutrition_database.
    Returns list of (food_name, protein_g) matches found.
    """
    found = []
    text_lower = text.lower()
    for food, info in nutrition_db.items():
        if food.lower() in text_lower:
            found.append((food, info["protein"]))
    return found

def calculate_weekly_protein(plan, nutrition_db):
    """
    Go through every day and the sections counted by the meal engine.
    Detect protein foods. Sum up total weekly protein points.
    """
    sections = ["breakfast", "dinner", "protein_add"]
    weekly_total = 0
    daily_totals = {}
    detected_log = []  # (day, section, food, protein_g)

    for day, meals in plan.items():
        day_total = 0
        for section in sections:
            meal_text = meals.get(section, "")
            matches = detect_protein_in_text(meal_text, nutrition_db)
            for food, protein_g in matches:
                day_total    += protein_g
                weekly_total += protein_g
                detected_log.append((day, section, food, protein_g))
        daily_totals[day] = day_total

    return weekly_total, daily_totals, detected_log

def calculate_score(weekly_total):
    """
    Realistic score out of 10.
    A well-planned vegetarian family of 6 should aim for ~400-500g
    total detected protein per week across all meals.
    Score is proportional — not inflated.
    """
    TARGET = 420  # realistic weekly target for this family profile
    ratio  = weekly_total / TARGET
    score  = round(min(ratio * 10, 10), 1)
    return score

def draw_bar(draw, y, label, value, max_value, color):
    draw.text((55, y), label, font=font(16, True), fill=TEXT_DARK)
    # Background bar
    draw.rectangle([55, y+28, 780, y+56], fill=BAR_BG)
    # Fill bar
    fill_w = int(725 * min(value / max_value, 1.0))
    if fill_w > 0:
        draw.rectangle([55, y+28, 55+fill_w, y+56], fill=color)
    # Value label
    draw.text((790, y+42), f"{value}g", font=font(14, True), fill=TEXT_DARK, anchor="lm")

def generate():
    with open("data/weekly_meal_plan.json") as f:
        meal_data = json.load(f)
    with open("data/nutrition_database.json") as f:
        nutrition_db = json.load(f)

    # Support both flat structure {Monday: ...} and wrapped {"plan": {Monday: ...}}
    if "plan" in meal_data:
        plan  = meal_data["plan"]
        month = meal_data.get("month", "This Week")
    else:
        days  = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        plan  = {k: v for k, v in meal_data.items() if k in days}
        month = meal_data.get("month", "This Week")

    # ── Core calculation ──────────────────────────────────────────────
    weekly_total, daily_totals, detected_log = calculate_weekly_protein(plan, nutrition_db)
    score     = calculate_score(weekly_total)
    avg_daily = round(weekly_total / 7)

    # Which foods were detected and how many times
    food_counts = {}
    for _, _, food, pg in detected_log:
        if food not in food_counts:
            food_counts[food] = {"count": 0, "total_g": 0}
        food_counts[food]["count"]   += 1
        food_counts[food]["total_g"] += pg
    top_foods = sorted(food_counts.items(), key=lambda x: x[1]["total_g"], reverse=True)[:4]

    # ── Draw ─────────────────────────────────────────────────────────
    img  = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Header
    draw.rectangle([0, 0, W, 100], fill=HEADER_BG)
    draw.text((W//2, 36), "Weekly Protein Score", font=font(30, True), fill=TEXT_LITE, anchor="mm")
    draw.text((W//2, 74), f"{month}  |  Real Protein Tracking from Meals", font=font(16), fill="#90E0EF", anchor="mm")

    # Score circle
    cx, cy, r = W//2, 215, 88
    draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=HEADER_BG)
    draw.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], fill="#012A5E")
    draw.text((cx, cy-16), f"{score}", font=font(52, True), fill=GOLD, anchor="mm")
    draw.text((cx, cy+36), "/ 10", font=font(20), fill="#90E0EF", anchor="mm")
    draw.text((cx, cy+70),  "Weekly Score", font=font(14), fill=TEXT_LITE, anchor="mm")

    # Stats row
    draw.rectangle([55, 320, 395, 390], fill="#EBF5FB")
    draw.rectangle([415, 320, 845, 390], fill="#EBF5FB")
    draw.text((225, 343), f"{weekly_total}g", font=font(22, True), fill=HEADER_BG, anchor="mm")
    draw.text((225, 372), "Total Weekly Protein Detected", font=font(13), fill=TEXT_MED, anchor="mm")
    draw.text((630, 343), f"{avg_daily}g / day", font=font(22, True), fill=HEADER_BG, anchor="mm")
    draw.text((630, 372), "Average Daily Protein", font=font(13), fill=TEXT_MED, anchor="mm")

    # Daily breakdown bars
    draw.text((55, 410), "Daily Protein Detected", font=font(17, True), fill=TEXT_DARK)
    max_day = max(daily_totals.values()) if daily_totals else 1
    colors  = ["#0096C7","#00B4D8","#48CAE4","#023E8A","#0077B6","#90E0EF","#ADE8F4"]
    y = 440
    for i, (day, total) in enumerate(daily_totals.items()):
        draw_bar(draw, y, day[:3], total, max(max_day, 1), colors[i % len(colors)])
        y += 70

    # Top protein sources detected
    y += 5
    draw.rectangle([40, y, W-40, y+44], fill=HEADER_BG)
    draw.text((W//2, y+22), "Top Protein Sources Detected This Week",
              font=font(16, True), fill=TEXT_LITE, anchor="mm")
    y += 52
    for i, (food, info) in enumerate(top_foods):
        col = 55 + (i % 2) * 420
        row = y + (i // 2) * 42
        draw.text((col, row), f"- {food}", font=font(15, True), fill=GREEN)
        draw.text((col+260, row), f"{info['total_g']}g over {info['count']}x",
                  font=font(14), fill=TEXT_MED)

    # Footer
    draw.rectangle([0, H-50, W, H], fill=HEADER_BG)
    draw.text((W//2, H-25),
              "Parivaar Nutrition AI  |  Protein detected from breakfast, dinner, and boosters",
              font=font(13), fill="#90E0EF", anchor="mm")

    img.save("protein_card.png")
    print(f"protein_card.png saved  |  Score: {score}/10  |  Weekly: {weekly_total}g  |  Avg: {avg_daily}g/day")
    print(f"   Detected {len(detected_log)} protein matches across {len(plan)} days")

if __name__ == "__main__":
    generate()
