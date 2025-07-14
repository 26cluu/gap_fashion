from cropper import crop_images
from search import search_items

image_path = "test_images/outfit.webp"

images = crop_images(image_path)

for image in images:
    picture = image[2]
    search_items(picture, description="brown hoodie and brown sweatpants")