from cropper import crop_images
from search import search_items
from fastapi import FastAPI, File, UploadFile
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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev server
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


# --- Image Upload Endpoint ---
@app.post("/upload-image/")
async def upload_image(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded image
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    cropped_images = crop_images(file_location)

    products = []

    for image in cropped_images:
        picture = image[2]
        found_product = search_items(picture)

        for product in found_product:
            product["image_path"] = product["image_path"].replace("\\", "/")

        products.extend(found_product)

    return JSONResponse(content={
        "filename": file.filename,
        "message": "Upload successful",
        "file_path": file_location,
        "product": products
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", reload=True, port=8000)