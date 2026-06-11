from PIL import Image, ImageDraw, ImageFont
import json


# =============================
# LOAD DATA
# =============================

with open("data/weekly_meal_plan.json", "r") as f:
    data = json.load(f)


health = data["health_analysis"]


score = health["health_score"]
grade = health["grade"]
achievements = health["achievements"]
alerts = health["alerts"]


# =============================
# CREATE CANVAS
# =============================

WIDTH = 900
HEIGHT = 1200

img = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    "#F5F5F0"
)

draw = ImageDraw.Draw(img)


# =============================
# FONTS
# =============================

try:
    title_font = ImageFont.truetype(
        "arial.ttf",
        42
    )
    heading_font = ImageFont.truetype(
        "arial.ttf",
        28
    )
    text_font = ImageFont.truetype(
        "arial.ttf",
        22
    )
    big_font = ImageFont.truetype(
        "arial.ttf",
        90
    )

except:
    title_font = heading_font = text_font = big_font = ImageFont.load_default()



# =============================
# HEADER
# =============================

draw.rectangle(
    [0, 0, WIDTH, 110],
    fill="#123B7A"
)

draw.text(
    (180, 25),
    "🧠 AI Weekly Health Report",
    fill="white",
    font=title_font
)


# =============================
# SCORE CIRCLE
# =============================

draw.ellipse(
    [320, 150, 580, 410],
    fill="#0B3B80"
)


draw.text(
    (390, 210),
    str(score),
    fill="#FFC300",
    font=big_font
)

draw.text(
    (420, 310),
    "/100",
    fill="white",
    font=heading_font
)

draw.text(
    (360, 350),
    grade,
    fill="#A5D6A7",
    font=heading_font
)


# =============================
# ACHIEVEMENTS
# =============================

y = 470


draw.text(
    (60, y),
    "🏆 Achievements",
    fill="#1B5E20",
    font=heading_font
)

y += 50


for item in achievements:
    draw.text(
        (80, y),
        "✓ " + item,
        fill="black",
        font=text_font
    )
    y += 40


# =============================
# ALERTS
# =============================

y += 30


draw.text(
    (60, y),
    "⚠ Areas To Improve",
    fill="#B71C1C",
    font=heading_font
)

y += 50


if alerts:
    for item in alerts:
        draw.text(
            (80, y),
            "• " + item,
            fill="black",
            font=text_font
        )
        y += 40

else:
    draw.text(
        (80, y),
        "No major health concerns this week 🎉",
        fill="black",
        font=text_font
    )


# =============================
# FOOTER
# =============================

draw.rectangle(
    [0, HEIGHT - 70, WIDTH, HEIGHT],
    fill="#123B7A"
)

draw.text(
    (180, HEIGHT - 50),
    "Parivaar Nutrition AI • Your Family Health Coach",
    fill="white",
    font=text_font
)


# =============================
# SAVE IMAGE
# =============================

img.save(
    "ai_health_report.png"
)


print(
    "✅ AI Health Card Generated"
)
