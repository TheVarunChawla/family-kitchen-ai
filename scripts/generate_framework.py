from PIL import Image, ImageDraw

# Create image
img = Image.new("RGB", (1200, 1600), "#f5f7f9")

draw = ImageDraw.Draw(img)

# Title
draw.text(
    (40, 30),
    "PARIVAAR NUTRITION AI",
    fill="black"
)

draw.text(
    (40, 80),
    "Delhi Summer Week",
    fill="black"
)

# Weekly Framework
content = """
📅 WEEKLY KITCHEN FRAMEWORK

🍳 Breakfast Options
✓ Moong Chilla
✓ Besan Chilla
✓ Poha + Peanuts

🥬 Lunch Options
✓ Bhindi
✓ Lauki
✓ Tori

🍲 Dinner Options
✓ Mixed Dal
✓ Rajma
✓ Chole

💪 Protein Mission
✓ Hung Curd
✓ Soya Granules
✓ Paneer

🌿 Seasonal Vegetables
✓ Bhindi
✓ Lauki
✓ Kakdi
"""

draw.text(
    (40, 150),
    content,
    fill="black"
)

img.save("weekly_framework.png")

print("Framework Created")
