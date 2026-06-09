from PIL import Image

img = Image.new("RGB", (500, 500), "white")

img.save("weekly_framework.png")

print("Image Created")
