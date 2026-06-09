from PIL import Image, ImageDraw
import json

with open("data/weekly_meal_plan.json", "r") as f:
weekly_plan = json.load(f)

img = Image.new("RGB", (1400, 1800), "#f5f7f9")
draw = ImageDraw.Draw(img)

draw.text(
(40, 20),
"PARIVAAR NUTRITION AI - WEEKLY MEAL PLAN",
fill="black"
)

y = 100

for day, meals in weekly_plan.items():

```
text = f"""
```

{day}

Breakfast: {meals['breakfast']}
Lunch: {meals['lunch']}
Dinner: {meals['dinner']}
"""

```
draw.text(
    (40, y),
    text,
    fill="black"
)

y += 220
```

img.save("weekly_meal_plan.png")

print("Weekly Meal Plan Created")
