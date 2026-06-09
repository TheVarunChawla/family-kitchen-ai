from PIL import Image, ImageDraw
import json
from datetime import datetime

# Load Seasonal Vegetables

current_month = datetime.now().strftime("%B")

with open("data/seasonal_vegetables.json", "r") as f:
seasonal_data = json.load(f)

vegetables = seasonal_data.get(current_month, [])

# Load Meal Plan

with open("data/meal_plan.json", "r") as f:
meal_plan = json.load(f)

breakfast = meal_plan["breakfast"]
lunch = meal_plan["lunch"]
dinner = meal_plan["dinner"]
protein = meal_plan["protein_mission"]

# Create Image

img = Image.new("RGB", (1200, 1600), "#f5f7f9")
draw = ImageDraw.Draw(img)

# Header

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

# Build Report Text

content = "📅 WEEKLY KITCHEN FRAMEWORK\n\n"

content += "🍳 Breakfast Options\n"
for item in breakfast:
content += f"✓ {item}\n"

content += "\n🥬 Lunch Options\n"
for item in lunch:
content += f"✓ {item}\n"

content += "\n🍲 Dinner Options\n"
for item in dinner:
content += f"✓ {item}\n"

content += "\n💪 Protein Mission\n"
for item in protein:
content += f"✓ {item}\n"

draw.text(
(40, 150),
content,
fill="black"
)

# Seasonal Vegetables

seasonal_text = "🌿 Seasonal Vegetables\n\n"

for veg in vegetables:
seasonal_text += f"✓ {veg}\n"

draw.text(
(40, 800),
seasonal_text,
fill="black"
)

# Save Image

img.save("weekly_framework.png")

print("Framework Created")
