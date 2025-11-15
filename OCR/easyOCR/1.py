from pdf2image import convert_from_path
from PIL import Image
import matplotlib.pyplot as plt

pdf_path = "lenderFee2.pdf"

# Convert first page to image
images = convert_from_path(pdf_path, dpi=300)
image = images[0]
image_path = '/content/page.png'
image.save(image_path)

# Show preview
plt.imshow(image)
plt.axis('off')
plt.title("Uploaded PDF - Page 1")
plt.show()

import easyocr
from PIL import ImageDraw

# Initialize reader
reader = easyocr.Reader(['en'])

# Run OCR
result = reader.readtext(image_path)