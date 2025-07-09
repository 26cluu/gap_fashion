from PIL import Image
import numpy as np
from fashion_clip.fashion_clip import FashionCLIP
import faiss
import json



# Load FashionCLIP
fclip = FashionCLIP('fashion-clip')

# Load user image
query_img = Image.open("test_images/white_polo.webp").convert("RGB")
query_img_emb = fclip.encode_images([query_img], batch_size=1)

# Optional: combine with user description
query_text = "white polo shirt"
query_txt_emb = fclip.encode_text([query_text], batch_size=1)

query_emb = (query_img_emb + query_txt_emb) / 2
query_emb = query_emb / np.linalg.norm(query_emb)
query_emb = query_emb.astype("float32")


faiss_index = faiss.read_index("gap_faiss.index")



with open("gap_metadata.json") as f:
    metadata = json.load(f)

# Run similarity search
D, I = faiss_index.search(query_emb, k=5)

# Print results
for score, idx in zip(D[0], I[0]):
    item = metadata[idx]
    print(f"{item['name']} — {item['image_url']} — score: {score:.4f}")