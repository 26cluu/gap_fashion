import { useState, useRef, useEffect } from "react";
import { HiOutlineCamera } from "react-icons/hi";
import defaultImage from "./assets/preview.png";
import './index.css';

function LoadingBar() {
  return (
    <div className="w-full h-1 bg-gray-200 relative overflow-hidden mb-4">
      <div className="absolute inset-0 bg-blue-500 animate-loading-bar"></div>
    </div>
  );
}

function CameraCapture({ stream, stopCamera, onCapture }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  const takePhoto = () => {
    const video = videoRef.current;
    if (!video) return;

    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      if (blob) {
        const photoUrl = URL.createObjectURL(blob);
        onCapture(blob, photoUrl);
        stopCamera();
      }
    }, "image/jpeg");
  };

  return (
    <div className="camera-capture mb-6">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="w-full rounded mb-2"
        style={{ maxHeight: 400, objectFit: "contain" }}
      />
      <div className="flex flex-col sm:flex-row gap-4 mb-4">
        <button
          onClick={takePhoto}
          className="w-full sm:w-auto px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
        >
          Take Photo
        </button>
        <button
          onClick={stopCamera}
          className="w-full sm:w-auto px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
        >
          Cancel
        </button>
      </div>
    </div>
  );
}

function App() {
  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

  const [cameraActive, setCameraActive] = useState(false);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(defaultImage);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [expandedIndex, setExpandedIndex] = useState(null);
  const [description, setDescription] = useState("");

  const startCamera = async () => {
    setError(null);
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
      setStream(mediaStream);
      setCameraActive(true);
    } catch (err) {
      setError("Could not access camera");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach((track) => track.stop());
      setStream(null);
    }
    setCameraActive(false);
  };

  const handleCameraCapture = (blob, url) => {
    setFile(new File([blob], "camera-photo.jpg", { type: blob.type }));
    setPreviewUrl(url);
  };

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
      setExpandedIndex(null);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!file && !description.trim()) {
      alert("Please provide either an image or a description.");
      return;
    }

    setLoading(true);
    setError(null);
    setProducts([]);
    setExpandedIndex(null);

    const formData = new FormData();
    if (file){
      formData.append("file", file);
    }
    formData.append("description", description);

    try {
      const response = await fetch(`${BACKEND_URL}/api/upload-image/`, {
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
      <div className="h-screen w-screen flex flex-col justify-center items-center p-6 text-center">
        <h1 className="text-5xl sm:text-7xl md:text-8xl font-bold mb-4">Welcome to FittinGap</h1>
        <p className="mb-8 text-base sm:text-lg">Find recommended outfits based on your uploaded inspiration photo.</p>
        <button
          onClick={() => setStarted(true)}
          className="px-6 py-3 text-lg sm:text-xl rounded-lg bg-gray-900 text-white hover:bg-gray-700 transition-colors duration-300"
        >
          Get Started
        </button>
      </div>
    );
  }

  return (
    <div className="p-4 sm:p-8 lg:p-16 box-border w-screen h-screen overflow-auto">
      <div className="flex flex-col lg:flex-row gap-6 mx-auto">
        <div className="flex-1">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-semibold mb-6">Upload Your Inspiration Photo</h1>

          <div className="flex items-center gap-4 flex-col sm:flex-row mb-4">
            <div
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById("fileInput").click()}
              className={`w-full sm:flex-1 relative cursor-pointer rounded-lg border-2 border-dashed transition-colors duration-300 p-4 ${isDragging ? "border-gray-800 bg-gray-100" : "border-gray-300 bg-transparent"} hover:bg-gray-300`}
            >
              <p className="text-center text-sm sm:text-base">
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

            {!cameraActive && (
              <button
                onClick={startCamera}
                className="p-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                aria-label="Open Camera"
                title="Open Camera"
              >
                <HiOutlineCamera className="h-6 w-6" />
              </button>
            )}
          </div>

          {cameraActive && (
            <CameraCapture
              stream={stream}
              stopCamera={stopCamera}
              onCapture={handleCameraCapture}
            />
          )}

          <form onSubmit={handleSubmit} className="mb-8">
            <div className="mb-4">
              <label htmlFor="description" className="block font-medium mb-1">
                Optional Description
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe your inspiration (e.g. 'flowy floral summer dress')"
                className="w-full p-2 border border-gray-300 rounded-md resize-none"
                rows={3}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-6 py-2 text-base bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-300 transition-colors duration-300"
            >
              {loading ? "Uploading..." : "Get Recommendations"}
            </button>
          </form>

          {loading && <LoadingBar />}

          {error && <p className="text-red-600 mb-4 text-sm">{error}</p>}

          {products.length > 0 && (
            <>
              <h2 className="text-xl sm:text-2xl font-semibold mb-4">Recommended Products</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 w-full">
                {products.map((product, index) => {
                  const isExpanded = expandedIndex === index;
                  const imageUrl = `${BACKEND_URL}/${product.image_path.replace(/\\/g, "/")}`;

                  const priceText = product.price || "";
                  const originalPriceMatch = priceText.match(/Original Price:\s*\$?([0-9.,]+)/i);
                  const currentPriceMatch = priceText.match(/Current Price:\s*\$?([0-9.,]+)/i);

                  const originalPrice = originalPriceMatch ? originalPriceMatch[1] : "";
                  const currentPrice = currentPriceMatch ? currentPriceMatch[1] : "";

                  return (
                    <div
                      key={index}
                      className="rounded-md text-left cursor-pointer select-none"
                      onClick={() => setExpandedIndex(isExpanded ? null : index)}
                    >
                      <img
                        src={imageUrl}
                        alt={product.name}
                        className="rounded-2xl mt-2 w-full object-contain"
                      />
                      <p className="block mt-2 font-bold text-sm sm:text-base">{product.name}</p>

                      <div className="flex items-center gap-2 text-sm text-gray-700 my-1">
                        {originalPrice && (
                          <span className="text-gray-500">
                            <span className="line-through">${originalPrice}</span>
                          </span>
                        )}
                        {currentPrice && (
                          <span className="font-semibold text-black">
                            ${currentPrice}
                          </span>
                        )}
                      </div>

                      {isExpanded && (
                        <p className="whitespace-pre-line mt-2 text-sm">{product.description}</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        <div className="w-full max-w-md mx-auto lg:w-[500px] flex-shrink-0 overflow-hidden text-center rounded-lg shadow-md h-fit">
          <h2 className="text-xl sm:text-2xl font-semibold mb-4">Photo</h2>
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


