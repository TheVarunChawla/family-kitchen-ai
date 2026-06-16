from PIL import Image, ImageDraw, ImageFont
import json
import textwrap


BG = "#FFFDF7"
HEADER_BG = "#123B7A"
TEXT_DARK = "#1B1B1B"
TEXT_MED = "#555555"
GREEN = "#2D6A4F"
RED = "#9D0208"
GOLD = "#FFB703"
BLUE_LT = "#E8F3FB"
BAR_BG = "#D8EEF7"
BAR_FILL = "#0096C7"

W, H = 900, 1450


def font(size, bold=False):
    try:
        path = (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            if bold else
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        )
        return ImageFont.truetype(path, size)
    except Exception:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except Exception:
            return ImageFont.load_default()


def draw_wrapped(draw, text, xy, width_chars, line_height, fill, font_obj):
    x, y = xy
    for line in textwrap.wrap(text, width=width_chars):
        draw.text((x, y), line, fill=fill, font=font_obj)
        y += line_height
    return y


def draw_bar(draw, x, y, label, value, max_value):
    draw.text((x, y), label, font=font(14, True), fill=TEXT_DARK)
    draw.rectangle([x, y + 26, x + 300, y + 46], fill=BAR_BG)
    fill_w = int(300 * min(value / max_value, 1))
    draw.rectangle([x, y + 26, x + fill_w, y + 46], fill=BAR_FILL)
    draw.text((x + 314, y + 36), f"{value:g}", font=font(13, True), fill=TEXT_DARK, anchor="lm")


def generate():
    with open("data/weekly_meal_plan.json", "r") as f:
        data = json.load(f)

    health = data["health_analysis"]
    score = health["health_score"]
    grade = health["grade"]
    achievements = health.get("achievements", [])
    alerts = health.get("alerts", [])
    focus_areas = health.get("focus_areas", [])
    recommendations = health.get("member_recommendations", {})
    components = health.get("component_scores", {})

    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, W, 110], fill=HEADER_BG)
    draw.text((W // 2, 38), "AI Weekly Health Intelligence", font=font(30, True), fill="white", anchor="mm")
    draw.text((W // 2, 76), "Protein, diabetes, BP, variety, and family-risk scoring", font=font(15), fill="#BDE0FE", anchor="mm")

    cx, cy, r = W // 2, 230, 92
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill="#0B3B80")
    draw.text((cx, cy - 18), str(score), fill=GOLD, font=font(54, True), anchor="mm")
    draw.text((cx, cy + 32), "/100", fill="#BDE0FE", font=font(18, True), anchor="mm")
    draw.text((cx, cy + 70), grade, fill="white", font=font(16, True), anchor="mm")

    draw.rectangle([55, 350, 845, 422], fill=BLUE_LT)
    draw.text((180, 376), f"{health.get('average_daily_protein_g', 0)}g/day", font=font(22, True), fill=HEADER_BG, anchor="mm")
    draw.text((180, 404), "Average Protein", font=font(13), fill=TEXT_MED, anchor="mm")
    draw.text((450, 376), f"{health.get('vegetable_variety_count', 0)}", font=font(22, True), fill=HEADER_BG, anchor="mm")
    draw.text((450, 404), "Vegetables", font=font(13), fill=TEXT_MED, anchor="mm")
    draw.text((720, 376), f"{health.get('diabetes_friendly_breakfast_days', 0)}/7", font=font(22, True), fill=HEADER_BG, anchor="mm")
    draw.text((720, 404), "Diabetes-Friendly Breakfasts", font=font(13), fill=TEXT_MED, anchor="mm")

    draw.text((55, 455), "Score Components", font=font(19, True), fill=TEXT_DARK)
    component_rows = [
        ("Protein", components.get("protein", 0), 35),
        ("Diabetes", components.get("diabetes", 0), 20),
        ("Vegetables", components.get("vegetables", 0), 15),
        ("BP Support", components.get("bp_support", 0), 10),
        ("Boosters", components.get("protein_boosters", 0), 8),
        ("Variety", components.get("variety", 0), 16),
    ]
    y = 490
    for i, (label, value, max_value) in enumerate(component_rows):
        x = 55 if i % 2 == 0 else 485
        if i and i % 2 == 0:
            y += 70
        draw_bar(draw, x, y, label, value, max_value)

    y += 98
    draw.rectangle([40, y, W - 40, y + 42], fill=HEADER_BG)
    draw.text((W // 2, y + 21), "What Went Well", font=font(17, True), fill="white", anchor="mm")
    y += 58
    for item in achievements[:4]:
        draw.text((65, y), "- " + item, fill=GREEN, font=font(15, True))
        y += 32

    y += 14
    draw.rectangle([40, y, W - 40, y + 42], fill="#7A1F1F")
    draw.text((W // 2, y + 21), "Focus Areas", font=font(17, True), fill="white", anchor="mm")
    y += 58
    if alerts:
        for item in alerts[:2]:
            draw.text((65, y), "- " + item, fill=RED, font=font(15, True))
            y += 32
    if focus_areas:
        for item in focus_areas[:3]:
            draw.text((65, y), "- " + item, fill=TEXT_DARK, font=font(15, True))
            y += 32
    if not alerts and not focus_areas:
        draw.text((65, y), "- Keep this pattern steady next week", fill=TEXT_DARK, font=font(15, True))
        y += 32

    y += 14
    draw.rectangle([40, y, W - 40, y + 42], fill=HEADER_BG)
    draw.text((W // 2, y + 21), "Family-Specific Coach Notes", font=font(17, True), fill="white", anchor="mm")
    y += 58

    for name in ["Dad", "Mom", "Sister1", "Varun"]:
        if name in recommendations:
            draw.text((65, y), f"{name}:", fill=HEADER_BG, font=font(15, True))
            y = draw_wrapped(
                draw,
                recommendations[name],
                (150, y),
                72,
                25,
                TEXT_DARK,
                font(14),
            )
            y += 8

    draw.rectangle([0, H - 58, W, H], fill=HEADER_BG)
    draw.text((W // 2, H - 29), "Parivaar Nutrition AI  |  Real weekly family health scoring", fill="#BDE0FE", font=font(13), anchor="mm")

    img.save("ai_health_report.png")
    print(f"AI Health Card Generated | Score: {score}/100 | Grade: {grade}")


if __name__ == "__main__":
    generate()
