from PIL import Image, ImageDraw

img = Image.new("RGB", (1200, 1400), "#f5f7f9")
draw = ImageDraw.Draw(img)

text = """
🛒 GROCERY LIST

Vegetables
✓ Lauki
✓ Bhindi
✓ Tori
✓ Kakdi

Protein Sources
✓ Paneer
✓ Dahi
✓ Soya Granules
✓ Roasted Chana

Kitchen Essentials
✓ Milk
✓ Mixed Dal
✓ Peanuts
"""

draw.text((40,40), text, fill="black")

img.save("grocery_list.png")

print("Grocery List Created")
