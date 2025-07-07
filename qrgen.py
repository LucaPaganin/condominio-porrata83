import qrcode
from PIL import Image, ImageDraw, ImageFont

# Data to encode
data = "https://viaporrata83.streamlit.app"

# Create QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# Create QR image
qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

# Text to add
text = "Scan Me"

# Load default font
# You can specify a TTF font file here if you want a different style
try:
    font = ImageFont.truetype("arial.ttf", 24)
except IOError:
    font = ImageFont.load_default()

# Get size of QR code
qr_width, qr_height = qr_img.size

# Create new image with extra height for text
text_height = 40
new_img = Image.new("RGB", (qr_width, qr_height + text_height), "white")

# Paste QR code into new image
new_img.paste(qr_img, (0, 0))

# Draw text centered (Pillow >= 10: use textbbox)
draw = ImageDraw.Draw(new_img)

# Calculate text dimensions first
if hasattr(draw, "textbbox"):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
else:
    text_width, _ = draw.textsize(text, font=font)
text_x = (qr_width - text_width) // 2
text_y = qr_height + 5  # small margin

# Now draw the text
draw.text((text_x, text_y), text, fill="black", font=font)

# Save final image
new_img.save("qrcode_with_text.png")

# Optionally display it
new_img.show()
