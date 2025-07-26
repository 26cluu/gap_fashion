from cropper import crop_images
from search import search_items_batch  # Import the batch function
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/gap_images", StaticFiles(directory="gap_images"), name="gap_images")

# ✅ Allow React frontend (localhost:3000) to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 🔍 Example root endpoint (health check)
@app.get("/")
def read_root():
    return {"message": "FastAPI is ready for React!"}

# --- Optimized Image Upload Endpoint with Batch Processing ---

@app.post("/upload-image/")
async def upload_image(
    file: UploadFile = File(None),
    description: str = Form(None)  # Accept description optionally
):
    images = None
    file_location = None

    if file is not None:
        file_location = os.path.join(UPLOAD_DIR, file.filename)

        # Save the uploaded image
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Crop and process
        cropped_images = crop_images(file_location)
        images = [crop[2] for crop in cropped_images]

    # Call search with images if available, plus description
    batch_results = search_items_batch(
        images=images,
        descriptions=[description] if description else None
    )

    # Clean up product image paths
    products = []
    for found_products in batch_results:
        for product in found_products:
            product["image_path"] = product["image_path"].replace("\\", "/")
        products.extend(found_products)

    return JSONResponse(content={
        "filename": file.filename if file else None,
        "message": "Upload successful",
        "file_path": file_location,
        "product": products
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=int(os.environ.get("PORT", 8000)),
        reload=False
    )