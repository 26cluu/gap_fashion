from PIL import Image
from fashion_clip.fashion_clip import FashionCLIP
import numpy as np
import json

fclip = FashionCLIP('fashion-clip')
with open("test_metadata.json") as f:
    catalog = json.load(f)["clothing_items"]

embeddings = []
metadata = []

for item in catalog:
    image = Image.open(item["image_url"]).convert("RGB")
    img_emb = fclip.encode_images([image], batch_size=1)
    txt_emb = fclip.encode_text([item["description"]], batch_size=1)
    combined = (img_emb + txt_emb) / 2
    combined = combined / np.linalg.norm(combined)  # normalize for cosine sim

    embeddings.append(combined[0])
    metadata.append({
        "name": item["name"],
        "description": item["description"],
        "image_url": item["image_url"]
    })

# Save to disk
np.save("gap_embeddings.npy", np.array(embeddings).astype("float32"))
with open("gap_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
