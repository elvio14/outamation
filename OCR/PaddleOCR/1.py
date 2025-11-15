from paddleocr import PaddleOCR
from pdf2image import convert_from_path
import cv2
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

# Convert first page to image
images = convert_from_path("lenderFees.pdf", dpi=300)
image_path = "page_1.png"
images[0].save(image_path, "PNG")

ocr = PaddleOCR(use_textline_orientation=True, lang='en')
result = ocr.ocr(image_path)

# Debug: Print the structure of the result
print("Result structure:")
if result and result[0]:
    print(f"Number of detected text lines: {len(result[0])}")
    if len(result[0]) > 0:
        # print(f"First line structure: {result[0][0]}")
        # print(f"Type of line[1]: {type(result[0][0][1])}")
        # print(f"Content of line[1]: {result[0][0][1]}")
        print(result[0])

# Load image using OpenCV
img = cv2.imread(image_path)

# Draw boxes
if result and result[0]:
    for line in result[0]:
        box = line[0]  # Bounding box coordinates
        text_info = line[1]  # Text info
        
        # Handle different possible structures
        if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
            text = text_info[0]  # Text content
            score = text_info[1]  # Confidence score
        elif isinstance(text_info, str):
            text = text_info
            score = 1.0  # Default score if not available
        else:
            text = str(text_info)
            score = 1.0
        
        box = [(int(pt[0]), int(pt[1])) for pt in box]
        cv2.polylines(img, [np.array(box)], isClosed=True, color=(255, 0, 0), thickness=2)
        cv2.putText(img, text, box[0], cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        print(f"Text: '{text}', Score: {score}")
else:
    print("No text detected in the image")

# Convert and display the result
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
plt.figure(figsize=(12, 12))
plt.imshow(img_rgb)
plt.axis("off")
plt.show()