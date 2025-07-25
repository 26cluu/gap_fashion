import time
import shutil
import os

# Import your functions or modules here
from cropper import crop_images
from search import search_items_batch  # adjust import as needed

UPLOAD_DIR = "uploads"  # set your upload dir

def benchmark_process(file_path):
    timings = {}

    start_total = time.time()

    # 1. Simulate saving the uploaded image by copying it to UPLOAD_DIR
    start = time.time()
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = os.path.basename(file_path)
    dest_path = os.path.join(UPLOAD_DIR, filename)
    shutil.copyfile(file_path, dest_path)
    timings['save_uploaded_image'] = time.time() - start

    # 2. Crop images
    start = time.time()
    cropped_images = crop_images(dest_path)
    timings['crop_images'] = time.time() - start

    # 3. Extract images from cropped_images for batch processing
    start = time.time()
    images = [cropped_image[2] for cropped_image in cropped_images]
    timings['extract_images'] = time.time() - start

    # 4. Run batch search
    start = time.time()
    batch_results = search_items_batch(images)
    timings['batch_search'] = time.time() - start

    # 5. Flatten results and fix paths
    start = time.time()
    products = []
    for found_products in batch_results:
        for product in found_products:
            product["image_path"] = product["image_path"].replace("\\", "/")
        products.extend(found_products)
    timings['flatten_results'] = time.time() - start

    total_time = time.time() - start_total

    # Print timings
    print("Benchmark results (seconds):")
    for step, t in timings.items():
        print(f"  {step}: {t:.3f}")
    print(f"Total elapsed time: {total_time:.3f}")

    return products


if __name__ == "__main__":
    test_image_path = "uploaded_images/more.jpg"  # Replace with your test image path
    benchmark_process(test_image_path)
