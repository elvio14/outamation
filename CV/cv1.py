import cv2
import numpy as np

image = cv2.imread('noisy.jpg')

bilateral = cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)

denoised = cv2.fastNlMeansDenoisingColored(bilateral, None, h=15, hColor=15, templateWindowSize=7, searchWindowSize=21)
cv2.imshow("denoised", denoised)
cv2.imwrite("denoised.jpg", denoised)
cv2.waitKey(0)
cv2.destroyAllWindows()
