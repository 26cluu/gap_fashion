from fashion_clip.fashion_clip import FashionCLIP
from PIL import Image
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

fclip = FashionCLIP("fashion-clip")

# GAP product
imageA = Image.open("test_images/baggy_shorts.avif")
text = "The roomiest pair in your rotation. Extra loose, seriously cool & brings all the vibes. Fit: Extra roomy through the hip & thigh with a baggy, slightly tapered leg. Fabric: 100% Regenerative Cotton. Stretch: No Stretch. Authentic rigid denim that gets better with every wear. Made to wear all day & break in over time.​ Look: Five-pocket denim shorts in a black wash. Details: Zip fly & five-pocket styling."

imageB = Image.open("test_images/baggy_black.webp")

# print("Image A mode:", imageA.mode, "size:", imageA.size)
# print("Image B mode:", imageB.mode, "size:", imageB.size)
# imageA.show()

# Get embeddings
imageA_emb = fclip.encode_images([imageA], batch_size=1)  # shape: (1, 512)
text_emb = fclip.encode_text([text], batch_size=1)             # shape: (1, 512)

# Combine (simple average)
combined_emb = (imageA_emb + text_emb) / 2

imageB_emb = fclip.encode_images([imageB], batch_size=1)  # shape: (1, 512)





similarity = cosine_similarity(combined_emb, imageB_emb)
#similarity = cosine_similarity(imageA_emb, imageB_emb)

print(f"Similarity Score: {similarity[0][0]:.4f}")


# Or weighted: combined_emb = 0.7 * image_emb + 0.3 * text_emb
