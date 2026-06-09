from PIL import Image, ImageDraw

img = Image.new("RGB", (1000, 600), "white")

draw = ImageDraw.Draw(img)

draw.text(
    (50, 50),
    "Family Kitchen AI\n\nPhase 2 Working!\n\nTelegram Image Test",
    fill="black"
)

img.save("test.png")

print("Image Created")
