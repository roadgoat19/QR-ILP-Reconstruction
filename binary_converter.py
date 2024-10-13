import cv2
import numpy as np

# Path to your PNG image
image_path = 'hello_world.png'

# Desired size (N x N)
N = 29

# Read the image in grayscale
img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

# Apply a binary threshold to get a binary image
_, binary_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

# Resize the image to N x N
resized_img = cv2.resize(binary_img, (N, N))

# Convert the resized image to a binary matrix (0s and 1s)
binary_matrix = np.where(resized_img > 127, 0, 1)

print(binary_matrix)
