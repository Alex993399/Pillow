from PIL import Image
import numpy as np

def generate_lut(size):
  grid = np.linspace(0, 255, size - 1, dtype=np.uint8)
  lut = np.stack(np.meshgrid(grid, grid, grid, indexing="ij"), axis=-1)
  lut = lut.astype(np.uint8)
  N = lut.shape[0]
  cols = 8
  rows = 8
  lut_img = np.zeros((rows * N, cols * N, 3), dtype=lut.dtype)

  for b in range(N):
    col = b % cols
    row = b // cols
    y0 = row * N
    x0 = col * N 
    lut_img[y0:y0 + N, x0:x0 + N] = lut[:, :, b]

  Image.fromarray(lut_img).save("lut.png")

def apply_table(image, lut_image):
  lut_image = np.array(lut_image)
  image_array = np.array(image)
  size = image_array.shape
  N = 64
  cols = 8
  lut = np.zeros((N, N, N, 3), dtype = np.uint8)
  for b in range(N):
    col = b % cols
    row = b // cols
    y0 = row * N
    x0 = col * N 
    lut[:, :, b] = lut_image[y0:y0 + N, x0:x0 + N]
  for y in range(size[0]):
    for x in range(size[1]):
      pixel = image_array[y][x]
      image_array[y][x] = lut[pixel[0] // 4, pixel[1] // 4, pixel[2] // 4]
      
  return image_array
  
