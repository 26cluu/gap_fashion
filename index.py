import faiss
import numpy as np

embeddings = np.load("gap_embeddings.npy")
index = faiss.IndexFlatIP(512)  # Cosine similarity index (IP = Inner Product)
index.add(embeddings)

faiss.write_index(index, "gap_faiss.index")
