import { useState } from "react";
import defaultImage from "./assets/preview.png";
import './index.css';

function App() {
  const BACKEND_URL = "http://localhost:8000";

  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(defaultImage);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    if (selectedFile) {
      setPreviewUrl(URL.createObjectURL(selectedFile));
    } else {
      setPreviewUrl(defaultImage);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const droppedFile = e.dataTransfer.files[0];
      setFile(droppedFile);
      setPreviewUrl(URL.createObjectURL(droppedFile));
      e.dataTransfer.clearData();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Please select an image before submitting.");
      return;
    }

    setLoading(true);
    setError(null);
    setProducts([]);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${BACKEND_URL}/upload-image/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.statusText}`);
      }

      const data = await response.json();
      setProducts(data.product || []);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  if (!started) {
    return (
      <div
        className="h-screen w-screen flex flex-col justify-center items-center p-8 text-center box-border"
      >
        <h1 className="text-4xl font-bold mb-4">Welcome to Fitting Gap</h1>
        <p className="mb-8">Find recommended outfits based on your uploaded inspiration photo.</p>
        <button
          onClick={() => setStarted(true)}
          className="px-8 py-3 text-xl rounded-lg bg-gray-900 text-white hover:bg-gray-700 transition-colors duration-300"
        >
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="p-8 box-border w-screen h-screen">
      <div className="flex gap-12 mx-auto box-border" style={{ maxWidth: "1200px" }}>
        <div className="flex-1">
          <h1 className="text-3xl font-semibold mb-6">Upload Your Inspiration Photo</h1>

          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => document.getElementById("fileInput").click()}
            className={`
              relative group cursor-pointer rounded-lg border-2 border-dashed
              transition-colors duration-300 mb-4
              ${isDragging ? "border-gray-800 bg-gray-100" : "border-gray-300 bg-transparent"}
              hover:bg-gray-600
            `}
          >
            <p className="p-8 text-center">
              {file ? file.name : "Drag and drop an image here, or click to browse."}
            </p>
            <input
              id="fileInput"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="hidden"
            />
          </div>

          <form onSubmit={handleSubmit} className="mb-8">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors duration-300"
            >
              {loading ? "Uploading..." : "Get Recommendations"}
            </button>
          </form>

          {error && <p className="text-red-600 mb-4">{error}</p>}

          {products.length > 0 && (
            <>
              <h2 className="text-2xl font-semibold mb-4">Recommended Products</h2>
              <div className="grid grid-cols-3 gap-4 w-full">
                {products.map((product, index) => {
                  const imageUrl = `${BACKEND_URL}/${product.image_path.replace(/\\/g, "/")}`;
                  return (
                    <div
                      key={index}
                      className="border border-gray-300 p-4 rounded-md text-left"
                    >
                      <strong>{product.name}</strong>
                      <p className="whitespace-pre-line">{product.price}</p>
                      <p className="whitespace-pre-line">{product.description}</p>
                      <img
                        src={imageUrl}
                        alt={product.name}
                        width={150}
                        className="rounded mt-2"
                      />
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        <div
          className="w-[500px] flex-shrink-0 overflow-hidden text-center rounded-lg shadow-md h-fit ml-auto"
        >
          <h2 className="text-2xl font-semibold mb-4">Photo</h2>
          <img
            src={previewUrl}
            alt="Preview"
            className="w-full h-auto object-contain rounded"
          />
        </div>
      </div>
    </div>
  );
}

export default App;
