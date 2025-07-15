from PIL import Image
import numpy as np
from fashion_clip.fashion_clip import FashionCLIP
import faiss
import json
import os
import matplotlib.pyplot as plt

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

def search_items(image, description=None):

    # Load FashionCLIP
    fclip = FashionCLIP('fashion-clip')

    # Load user image
    query_img = image.convert("RGB")
    query_img_emb = fclip.encode_images([query_img], batch_size=1)

    # Optional: combine with user description

    if description:
        query_text = description
        query_txt_emb = fclip.encode_text([query_text], batch_size=1)

        query_emb = (query_img_emb + query_txt_emb) / 2
        query_emb = query_emb / np.linalg.norm(query_emb)
        query_emb = query_emb.astype("float32")

    else:
       query_emb = query_img_emb


    faiss_index = faiss.read_index("gap_faiss.index")



    with open("gap_metadata.json") as f:
        metadata = json.load(f)

    # Run similarity search
    D, I = faiss_index.search(query_emb, k=5)
    items = []

    # Print results
    for score, idx in zip(D[0], I[0]):
        item = metadata[idx]
        print(f"{item['name']} — {item['image_path']} — score: {score:.4f}")
        
        items.append(item)

    return items





        # plt.imshow(Image.open(match).convert("RGB"))
        # plt.axis('off')  # Hide axis ticks
        # plt.title(f"{item['name']} (score: {score:.4f})")
        # plt.show()


