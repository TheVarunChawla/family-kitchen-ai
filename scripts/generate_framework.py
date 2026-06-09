from PIL import Image, ImageDraw
import json
from datetime import datetime

# -------------------------

# Load Seasonal Vegetables

# -------------------------

current_month = datetime.now().strftime("%B")

with open("data/seasonal_vegetables.json", "r") as f:
seasonal_data = json.load(f)

vegetables = seasonal_data.get(current_month, [])

# -------------------------

# Create Image

# -------------------------

img = Image.new("RGB", (1200, 1600), "#f5f7f9")

draw = ImageDraw.Draw(img)

# -------------------------

# Header

# -------------------------

draw.text(
(40, 30),
"PARIVAAR NUTRITION AI",
fill="black"
)

draw.text(
(40, 80),
f"Delhi NCR | {current_month}",
fill="black"
)

# -------------------------

# Main Framework

# -------------------------

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
"""

draw.text(
(40, 150),
content,
fill="black"
)

# -------------------------

# Seasonal Vegetables

# -------------------------

seasonal_text = "🌿 Seasonal Vegetables\n\n"

for veg in vegetables:
seasonal_text += f"✓ {veg}\n"

draw.text(
(40, 700),
seasonal_text,
fill="black"
)

# -------------------------

# Save Image

# -------------------------

img.save("weekly_framework.png")

print(f"Framework Created For {current_month}")
