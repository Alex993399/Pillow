import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageChops, ImageFilter
import numpy as np
from map import apply_table

FILTERS = {"black_and_white": 0, "saturation" : 1, "brightness" : 1, "contrast" : 1, "sharpness": 1, "contour": 2, "threshold": 1, "kuwahara": 1, "invert": 0, "lut_filter": 1}

def main(argc, argv):
    filepath = Path(argv[1])
    image = Image.open(filepath)
    index = 2
    while index < argc:
        filter_name = argv[index]
        if filter_name in FILTERS:
            index += 1
            image, index = apply_filter(filter_name, image, index, *argv[index:index + FILTERS[filter_name]])
    image.save(filepath.stem + "changed" + ".png")
    print(image.size)

def black_and_white(image):
    grey = image.convert("L")
    return grey

def saturation(image, value):
    enhancer = ImageEnhance.Color(image)
    edited = enhancer.enhance(float(value))
    return edited

def brightness(image, value):
    enhancer = ImageEnhance.Brightness(image)
    edited = enhancer.enhance(float(value))
    return edited

def contrast(image, value):
    enhancer = ImageEnhance.Contrast(image)
    edited = enhancer.enhance(float(value))
    return edited

def sharpness(image, value):
    enhancer = ImageEnhance.Sharpness(image)
    edited = enhancer.enhance(float(value))
    return edited

def threshold(image, value):
    value = float(value)
    img_gray = image.convert("L")
    img_gray = img_gray.point(lambda a: 255 if a > value else 0)
    return img_gray.convert("RGB")

def contour(image, value, colour):
    image_blur = image.filter(ImageFilter.GaussianBlur(radius=float(value)))
    contour = ImageChops.difference(image, image_blur)
    contour = threshold(image, 64)
    colour = Image.new("RGB", image.size, colour)
    contour = ImageChops.multiply(contour, colour)
    return contour

def kuwahara(image, radius):
    image_array = np.array(image.convert("RGB"))
    radius = int(radius)
    combined = np.zeros_like(image_array)
    for channel in range(3):
        h, w = image_array[:,:,channel].shape
        padded = np.pad(image_array[:,:,channel], radius, mode="reflect")
        result = np.zeros_like(image_array[:,:,channel])
        for y in range(h):
            for x in range(w):
                window = padded[y:y + 2 * radius + 1, x:x + 2 * radius + 1]
                regions = [
                    window[0:radius + 1, 0:radius + 1],
                    window[0:radius + 1, radius:],
                    window[radius:, 0:radius + 1],
                    window[radius:, radius:]
                ]
                means = []
                variances = []
                for region in regions:
                    means.append(np.mean(region))
                    variances.append(np.var(region))
                best_region = np.argmin(variances)
                result[y, x] = means[best_region]
        combined[:,:,channel] = result
    return Image.fromarray(combined)

def invert(image):
    image = image.convert("RGB")
    image_array = np.array(image)
    lut = np.array([[r, g, 0]for r in range(256) for g in range(256)])
    # lut = np.array([[i for i in range(256)], [255 for i in range(256)], [i for i in range(256)]], dtype=np.uint8)
    negative_image = lut[image_array]
    return Image.fromarray(negative_image)

def lut_filter(image, lut_image):
    image = image.convert("RGB")
    lut = Image.open(f"filters/{lut_image}").convert("RGB")
    return Image.fromarray(apply_table(image,  lut))

def apply_filter(filter_name, image, index, *args):
    filter_name = eval(filter_name)
    index += len(args)
    return filter_name(image, *args), index

if __name__ == "__main__":
    args = sys.argv
    main(len(args), args)

