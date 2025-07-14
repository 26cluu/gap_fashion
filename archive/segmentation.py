import torch
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import requests

# ------------------------------
# 1. Load YOLOS-Fashionpedia Model and Processor
# ------------------------------
processor = YolosImageProcessor.from_pretrained("valentinafeve/yolos-fashionpedia")
model = YolosForObjectDetection.from_pretrained("valentinafeve/yolos-fashionpedia")

# ------------------------------
# 2. Load an Image (from URL or local)
# ------------------------------
# Option A: Load from URL
image = Image.open("test_images/test.jpg").convert("RGB")

# Option B: Load local file
# image = Image.open("your_image.jpg").convert("RGB")

# ------------------------------
# 3. Run Inference
# ------------------------------
inputs = processor(images=image, return_tensors="pt")
outputs = model(**inputs)

target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.3)[0]

# ------------------------------
# 4. Visualize Results
# ------------------------------
sleeve_labels = {"sleeve", "sleeveless", "short sleeve", "long sleeve"}
plt.figure(figsize=(12, 8))
plt.imshow(image)
ax = plt.gca()

# To collect cropped shirt/pants
interested_labels = {"shirt", "pants", "jacket", "t-shirt", "top", "sweatshirt"}
cropped_images = []

for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
    category = model.config.id2label[label.item()]
    print(category)

    # Handle comma-separated labels
    split_labels = [c.strip().lower() for c in category.split(",")]

    # Skip if any part is a sleeve label
    if any(label in sleeve_labels for label in split_labels):
        continue

    # Draw box
    xmin, ymin, xmax, ymax = box.tolist()
    ax.add_patch(patches.Rectangle((xmin, ymin), xmax - xmin, ymax - ymin,
                                   linewidth=2, edgecolor='red', facecolor='none'))
    ax.text(xmin, ymin, f'{category}: {round(score.item(), 2)}',
            bbox=dict(facecolor='red', alpha=0.5), color='white')

    # Crop if any part matches interested clothing
    if any(label in interested_labels for label in split_labels):
        cropped = image.crop((int(xmin), int(ymin), int(xmax), int(ymax)))
        cropped_images.append((category, round(score.item(), 2), cropped))


plt.axis('off')
plt.title("YOLOS-Fashionpedia Detection")
plt.show()

# ------------------------------
# 5. Show Cropped Shirt and Pants
# ------------------------------
if cropped_images:
    num_images = len(cropped_images)
    cols = min(4, num_images)        # max 4 columns per row
    rows = (num_images + cols - 1) // cols  # number of rows needed

    plt.figure(figsize=(4 * cols, 5 * rows))

    for i, (category, confidence, cropped_img) in enumerate(cropped_images):
        plt.subplot(rows, cols, i + 1)
        plt.imshow(cropped_img)
        plt.title(f"{category}\n{confidence:.2f}")
        plt.axis("off")

    plt.tight_layout()
    plt.show()
else:
    print("No shirts or pants detected.")
