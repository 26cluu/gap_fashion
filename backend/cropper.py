import torch
from transformers import YolosImageProcessor, YolosForObjectDetection
from PIL import Image

# Load model and processor once globally
processor = YolosImageProcessor.from_pretrained("valentinafeve/yolos-fashionpedia")
model = YolosForObjectDetection.from_pretrained("valentinafeve/yolos-fashionpedia")

def crop_images(path):
    # Load image
    image = Image.open(path).convert("RGB")

    # Inference
    inputs = processor(images=image, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([image.size[::-1]])
    results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.3)[0]

    # Labels to skip or keep
    sleeve_labels = {"sleeve", "sleeveless", "short sleeve", "long sleeve"}
    interested_labels = {"shirt", "pants", "jacket", "t-shirt", "top", "sweatshirt"}

    cropped_images = []

    for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
        category = model.config.id2label[label.item()]
        split_labels = [c.strip().lower() for c in category.split(",")]

        if any(label in sleeve_labels for label in split_labels):
            continue

        xmin, ymin, xmax, ymax = box.tolist()

        if any(label in interested_labels for label in split_labels):
            cropped = image.crop((int(xmin), int(ymin), int(xmax), int(ymax)))
            cropped_images.append((category, round(score.item(), 2), cropped))

    return cropped_images






