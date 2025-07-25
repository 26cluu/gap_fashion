import time
from PIL import Image
from fashion_clip.fashion_clip import FashionCLIP
import torch

# Load model
print("Loading FashionCLIP model...")
fclip = FashionCLIP('fashion-clip')
fclip.device = 'cpu'
fclip.model = fclip.model.to('cpu')

device = fclip.device
print(f"Using device: {device}")
if device == "mps":
    print("✅ MPS acceleration is ENABLED.")
elif device == "cuda":
    print("✅ CUDA acceleration is ENABLED.")
else:
    print("⚠️ Running on CPU.")

# Load a test image
image_path = "gap_images/page1_id1.jpg"  # Replace with your test image path
image = Image.open(image_path).convert("RGB")

# Warm-up run (helps avoid first-run overhead)
_ = fclip.encode_images([image], batch_size=1)

# Timed encoding
start_time = time.time()
embedding = fclip.encode_images([image], batch_size=1)
end_time = time.time()

print("Model tensor device:", next(fclip.model.parameters()).device)
print(f"Encoding time for 1 image: {end_time - start_time:.4f} seconds")
