# Fashion Analysis Tool

A comprehensive Python tool that analyzes outfit images using Fashionpedia (YOLOS-Fashionpedia) for segmentation and FashionCLIP by patrickjohncyh for style analysis. The tool can segment full outfits into individual clothing pieces and analyze factors such as style, fit, and shape.

## Features

-   **Outfit Segmentation**: Automatically segments full outfit images into individual clothing pieces using Fashionpedia
-   **Style Analysis**: Uses FashionCLIP to analyze style, material, fit, shape, and fashion characteristics
-   **Visualization**: Creates annotated images showing detected pieces and analysis results
-   **Batch Processing**: Analyze multiple outfit images at once
-   **Comprehensive Reporting**: Generates detailed JSON reports with all analysis data

## Installation

### Prerequisites

-   Python 3.8 or higher
-   CUDA-compatible GPU (optional, for faster processing)

### Setup

#### Option 1: Automatic Installation (Recommended)

1. **Run the installation script**:
    ```bash
    python install_dependencies.py
    ```

#### Option 2: Manual Installation

1. **Install PyTorch first** (CPU version for Windows):

    ```bash
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
    ```

2. **Install other dependencies**:
    ```bash
    pip install transformers>=4.30.0 matplotlib>=3.7.0 Pillow>=10.0.0 numpy>=1.24.0 requests>=2.31.0
    ```

#### Option 3: Using Conda (Alternative)

If you encounter compilation issues with pip, try using conda:

```bash
conda install pytorch torchvision transformers matplotlib pillow numpy requests -c pytorch
```

#### Troubleshooting Installation Issues

If you encounter the "Microsoft Visual C++ 14.0 or greater is required" error:

1. **Install Microsoft Visual C++ Build Tools**:

    - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
    - Install the "C++ build tools" workload

2. **Or use pre-built wheels**:

    - The installation script automatically tries to use pre-built wheels
    - PyTorch provides pre-built wheels for most platforms

3. **Verify installation**:
    ```bash
    python -c "import torch, transformers, matplotlib, PIL, numpy, requests; print('All dependencies installed successfully!')"
    ```

## Usage

### Quick Start

1. **Run the main analysis script**:

    ```bash
    python analysis.py
    ```

2. **Or use the example script with menu options**:

    ```bash
    python example_usage.py
    ```

3. **Enter the path to your outfit image** when prompted.

### Programmatic Usage

```python
from analysis import FashionAnalyzer

# Initialize the analyzer
analyzer = FashionAnalyzer()

# Analyze an outfit
results = analyzer.analyze_outfit("path/to/outfit.jpg", save_results=True)

# Access results
print(f"Found {results['overall_analysis']['total_pieces']} clothing pieces")
print(f"Overall style: {results['overall_analysis']['dominant_style']}")

# Visualize results
analyzer.visualize_analysis(results, save_path="analysis_visualization.png")
```

### Batch Analysis

```python
# Analyze multiple images in a folder
analyzer = FashionAnalyzer()
folder_path = "path/to/outfit/images/"
# The script will automatically process all image files in the folder
```

## Output

The tool generates several types of output:

### 1. JSON Analysis Report

-   Detailed analysis of each detected clothing piece
-   Style analysis using FashionCLIP embeddings
-   Overall outfit assessment

### 2. Visualization Image

-   Original image with bounding boxes around detected pieces
-   Labels showing piece descriptions
-   Saved as PNG file

### 3. Console Output

-   Real-time progress updates
-   Summary of findings
-   Error messages if any issues occur

## Analysis Components

### Style Analysis (FashionCLIP)

-   **Style Categories**: casual, formal, streetwear, vintage, etc.
-   **Color Matching**: black, white, red, blue, etc.
-   **Fit Descriptions**: loose fit, tight fit, regular fit, etc.
-   **Shape Features**: round neck, v-neck, long sleeve, etc.
-   **Material Hints**: cotton, denim, silk, wool, etc.

### Fashionpedia Segmentation

-   **Object Detection**: Identifies clothing items using YOLOS-Fashionpedia
-   **Category Classification**: Labels each piece with its clothing category
-   **Confidence Scoring**: Provides confidence levels for each detection
-   **Bounding Boxes**: Precise location of each clothing piece

## Supported Image Formats

-   JPEG (.jpg, .jpeg)
-   PNG (.png)
-   BMP (.bmp)
-   TIFF (.tiff)
-   WebP (.webp)

## Configuration

### Customizing Style Prompts

You can modify the style analysis by editing the `style_prompts` dictionary in the `FashionAnalyzer` class:

```python
self.style_prompts = {
    'style': [
        "casual style", "formal style", "streetwear", "vintage",
        # Add your custom style prompts here
    ],
    'color': [
        "black", "white", "red", "blue",
        # Add your custom color prompts here
    ],
    # ... other categories
}
```

## Performance Tips

1. **GPU Acceleration**: The tool automatically uses CUDA if available for faster processing
2. **Image Size**: Larger images provide better analysis but take longer to process
3. **Batch Processing**: Use batch analysis for multiple images to save time

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**:

    - Reduce image size before analysis
    - Use CPU processing instead of GPU

2. **No Segments Detected**:

    - Ensure the image contains clear clothing items
    - Try adjusting the detection threshold

3. **Poor Style Analysis**:

    - Ensure good lighting in the image
    - Make sure clothing items are clearly visible

4. **Installation Errors**:
    - Try the automatic installation script first
    - Install Microsoft Visual C++ Build Tools if needed
    - Use conda as an alternative to pip

### Error Messages

-   **"Image file not found"**: Check the file path and ensure the image exists
-   **"No image files found"**: Verify the folder contains supported image formats
-   **"Error loading Fashionpedia model"**: Check internet connection for model download
-   **"Microsoft Visual C++ 14.0 or greater is required"**: Install Visual C++ Build Tools or use conda

## Example Output

```
FASHION ANALYSIS RESULTS
============================================================

📊 OVERALL OUTFIT ANALYSIS:
   • Total pieces detected: 3
   • Dominant style: casual style
   • Style coherence: 0.67
   • Color palette: blue, white, black
   • Fit variety: regular, loose
   • Categories: shirt, pants, jacket
   • Style assessment: Balanced with some variety

👕 INDIVIDUAL PIECES ANALYSIS:

   Piece 1:
   • Description: A blue shirt with casual style style and regular fit
   • Category: shirt
   • Confidence: 0.95
   • Location: [120, 80, 200, 300]
   • Area: 60000 pixels
   • Style: casual style (0.85)
   • Color: blue (0.78)
   • Fit: regular fit (0.78)
   • Shape: round neck (0.72)
   • Material hint: cotton (0.82)
```

## Contributing

To improve the tool:

1. Add new style prompts for better fashion analysis
2. Implement more sophisticated analysis techniques
3. Add support for additional fashion categories
4. Improve visualization with more detailed annotations

## License

This tool is provided as-is for educational and research purposes.

## Dependencies

-   **torch**: Deep learning framework
-   **transformers**: Hugging Face transformers for Fashionpedia and FashionCLIP models
-   **matplotlib**: Visualization
-   **Pillow**: Image processing
-   **numpy**: Numerical computing
-   **requests**: HTTP requests for URL images
