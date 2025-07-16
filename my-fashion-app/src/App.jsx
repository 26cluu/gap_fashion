import { useState } from "react";
import defaultImage from "./assets/preview.png";

function App() {
  const BACKEND_URL = "http://localhost:8000";

  const [started, setStarted] = useState(false);
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(defaultImage);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);

    if (selectedFile) {
      setPreviewUrl(URL.createObjectURL(selectedFile));
    } else {
      setPreviewUrl(defaultImage);
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
    // Get Started page
    return (
      <div
        style={{
          height: "100vh",
          width: "100vw",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          padding: "2rem",
          textAlign: "center",
          boxSizing: "border-box",
        }}
      >
        <h1>Welcome to Fitting Gap</h1>
        <p>Find recommended outfits based on your uploaded inspiration photo.</p>
        <button
          onClick={() => setStarted(true)}
          style={{
            padding: "0.75rem 2rem",
            fontSize: "1.2rem",
            borderRadius: "8px",
            background: "#333",
            color: "white",
            border: "none",
            marginTop: "2rem",
            cursor: "pointer",
          }}
        >
          Get Started
        </button>
      </div>
    );
  }

  // Main app page
  return (
    <div style={{ padding: "2rem", boxSizing: "border-box" }}>
      <div
        style={{
          width: "100%",
          margin: "auto",
          padding: "2rem",
          display: "flex",
          gap: "3rem",
          boxSizing: "border-box",
        }}
      >
        {/* Left side: form + product recommendations */}
        <div style={{ flex: 1 }}>
          <h1>Upload Your Inspiration Photo</h1>
          <form onSubmit={handleSubmit} style={{ marginBottom: "2rem" }}>
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button type="submit" style={{ marginLeft: "1rem" }} disabled={loading}>
              {loading ? "Uploading..." : "Get Recommendations"}
            </button>
          </form>

          {error && <p style={{ color: "red" }}>{error}</p>}

          {products.length > 0 && (
            <>
              <h2>Recommended Products</h2>
              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(3, 1fr)",
                  gap: "1rem",
                  width: "100%"
                }}
              >
                {products.map((product, index) => {
                  const imageUrl = `${BACKEND_URL}/${product.image_path.replace(/\\/g, "/")}`;
                  return (
                    <div
                      key={index}
                      style={{
                        border: "1px solid #ddd",
                        padding: "1rem",
                        borderRadius: "8px",
                        textAlign: "center",
                      }}
                    >
                      <strong>{product.name}</strong>
                      <p style={{ whiteSpace: "pre-line" }}>{product.price}</p>
                      <p style={{ whiteSpace: "pre-line" }}>{product.description}</p>
                      <img
                        src={imageUrl}
                        alt={product.name}
                        width={150}
                        style={{ borderRadius: "4px", marginTop: "0.5rem" }}
                      />
                    </div>
                  );
                })}
              </div>
            </>
          )}
        </div>

        {/* Right side: preview box */}
        <div
          style={{
            width: "500px",
            flexShrink: 0, // Prevent shrinking
            overflow: "hidden",
            textAlign: "center",
            borderRadius: 8,
            boxShadow: "0 0 10px rgba(0,0,0,0.1)",
            height: "fit-content",
            marginLeft: "auto", // Push to the far right
          }}
        >
          <h2>Photo</h2>
          <img
            src={previewUrl}
            alt="Preview"
            style={{
              width: "100%",
              height: "auto",
              objectFit: "contain",
              borderRadius: 8,
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default App;