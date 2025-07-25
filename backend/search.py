from PIL import Image
import numpy as np
from fashion_clip.fashion_clip import FashionCLIP
import faiss
import json
import os
import matplotlib.pyplot as plt
import torch

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Global variables to cache loaded models and data
_fclip = None
_faiss_index = None
_metadata = None

def load_models_and_data():
    """Load models and data once and cache them"""
    global _fclip, _faiss_index, _metadata
    
    if _fclip is None:
        print("Loading FashionCLIP model...")
        _fclip = FashionCLIP('fashion-clip')
        _fclip.device = 'cpu'
        _fclip.model = _fclip.model.to('cpu')
        device = _fclip.device
        print(f"FashionCLIP is using device: {device}")
        # Extra confirmation:
        if device == "mps":
            print("🎉 MPS acceleration is ENABLED and being used.")
        elif device == "cuda":
            print("🎉 CUDA GPU acceleration is ENABLED and being used.")
        else:
            print("⚠️ Using CPU only.")
    
    if _faiss_index is None:
        print("Loading FAISS index...")
        _faiss_index = faiss.read_index("gap_faiss.index")
    
    if _metadata is None:
        print("Loading metadata...")
        with open("gap_metadata.json") as f:
            _metadata = json.load(f)

def search_items(image, description=None):
    # Load models and data (cached after first call)
    load_models_and_data()
    
    # Use cached model
    fclip = _fclip
    
    # Load user image
    query_img = image.convert("RGB")
    query_img_emb = fclip.encode_images([query_img], batch_size=1)
    
    # Optional: combine with user description
    if description:
        query_text = description
        query_txt_emb = fclip.encode_text([query_text], batch_size=1)
        
        # Vectorized operations
        query_emb = (query_img_emb + query_txt_emb) * 0.5  # Slightly faster than /2
        query_emb = query_emb / np.linalg.norm(query_emb)
        query_emb = query_emb.astype("float32")
    else:
        query_emb = query_img_emb
    
    # Use cached index and metadata
    faiss_index = _faiss_index
    metadata = _metadata
    
    # Run similarity search
    D, I = faiss_index.search(query_emb, k=5)
    
    # Optimize result processing
    items = []
    scores = D[0]
    indices = I[0]
    
    for score, idx in zip(scores, indices):
        item = metadata[idx]
        print(f"{item['name']} — {item['image_path']} — score: {score:.4f}")
        items.append(item)
    
    return items

import torch
from PIL import Image

def search_items_batch(images=None, descriptions=None):
    """Search using image embeddings, text embeddings, or both (averaged)."""
    load_models_and_data()

    fclip = _fclip
    faiss_index = _faiss_index
    metadata = _metadata

    # Safety fallback if both inputs are None
    if not images and not descriptions:
        raise ValueError("At least one of 'images' or 'descriptions' must be provided.")

    results = []
    query_img_embs = []
    query_txt_embs = []

    # Process image embeddings if provided
    if images:
        query_imgs = [img.convert("RGB").resize((224, 224)) for img in images]
        with torch.no_grad():
            query_img_embs = fclip.encode_images(query_imgs, batch_size=len(query_imgs))

    # Process text embeddings if provided
    if descriptions:
        with torch.no_grad():
            query_txt_embs = fclip.encode_text(descriptions, batch_size=len(descriptions))

    num_queries = max(len(query_img_embs), len(query_txt_embs))

    for i in range(num_queries):
        has_image = i < len(query_img_embs)
        has_text = i < len(query_txt_embs)

        if has_image and has_text:
            # Combine image + text
            emb = (query_img_embs[i] + query_txt_embs[i]) * 0.5
        elif has_image:
            emb = query_img_embs[i]
        elif has_text:
            emb = query_txt_embs[i]
        else:
            continue  # Skip if no embedding available (shouldn't happen)

        emb = emb / np.linalg.norm(emb)
        emb = emb.astype("float32")

        D, I = faiss_index.search(emb.reshape(1, -1), k=5)
        items = [metadata[idx] for score, idx in zip(D[0], I[0])]
        results.append(items)

    return results




# Optional: Preload everything when module is imported
# Uncomment the line below if you want to preload on import
# load_models_and_data()


