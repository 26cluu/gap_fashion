import os
from PIL import Image
from fashion_clip.fashion_clip import FashionCLIP
import numpy as np
import json
import faiss

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

fclip = FashionCLIP('fashion-clip')

with open("gap_products_updated.json") as f:
    catalog = json.load(f)["products"]

batch_size = 16

images_batch = []
texts_batch = []
metadata_batch = []

embeddings = []
metadata = []

for item in catalog:
    img_path = item["image_path"]
    if "Image not found" in img_path or not os.path.isfile(img_path):
        print(f"Skipping {item['name']} due to missing or invalid image path.")
        continue

    image = Image.open(img_path).convert("RGB")
    text = item["name"] + ": " + item["description"]

    images_batch.append(image)
    texts_batch.append(text)
    metadata_batch.append({
        "name": item["name"],
        "description": item["description"],
        "image_path": img_path,
        "price": item["price"]
    })

    # When batch is full, process it
    if len(images_batch) == batch_size:
        img_emb = fclip.encode_images(images_batch, batch_size=batch_size)
        txt_emb = fclip.encode_text(texts_batch, batch_size=batch_size)
        combined = (img_emb + txt_emb) / 2
        # Normalize each vector individually
        norms = np.linalg.norm(combined, axis=1, keepdims=True)
        combined = combined / norms

        embeddings.extend(combined)
        metadata.extend(metadata_batch)

        images_batch = []
        texts_batch = []
        metadata_batch = []

# Process any remaining items in the last batch
if images_batch:
    img_emb = fclip.encode_images(images_batch, batch_size=len(images_batch))
    txt_emb = fclip.encode_text(texts_batch, batch_size=len(texts_batch))
    combined = (img_emb + txt_emb) / 2
    norms = np.linalg.norm(combined, axis=1, keepdims=True)
    combined = combined / norms

    embeddings.extend(combined)
    metadata.extend(metadata_batch)

# Save to disk
np.save("gap_embeddings.npy", np.array(embeddings).astype("float32"))
with open("gap_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

embeddings = np.load("gap_embeddings.npy")
index = faiss.IndexFlatIP(512)  # Cosine similarity index (IP = Inner Product)
index.add(embeddings)

faiss.write_index(index, "gap_faiss.index")

