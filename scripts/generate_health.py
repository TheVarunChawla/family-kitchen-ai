from PIL import Image, ImageDraw

img = Image.new("RGB", (1200, 1400), "#f5f7f9")
draw = ImageDraw.Draw(img)

text = """
💪 FAMILY HEALTH MISSION

Dad
✓ Extra Hung Curd

Mom
✓ Limit Fried Snacks

Sister
✓ Add Sprouts Twice

Family Goal
✓ Add Soya 2 Times
✓ Add Green Veg Once
✓ Replace Biscuits With Chana
"""

draw.text((40,40), text, fill="black")

img.save("health_mission.png")

print("Health Mission Created")
