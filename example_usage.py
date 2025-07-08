#!/usr/bin/env python3
"""
Example usage of the FashionAnalyzer for outfit analysis.
This script demonstrates how to analyze different types of outfit images using
Fashionpedia for segmentation and FashionCLIP for style analysis.
"""

import os
from analysis import FashionAnalyzer


def analyze_sample_outfit():
    """
    Analyze a sample outfit image.
    """
    # Initialize the analyzer
    analyzer = FashionAnalyzer()

    # Example image path (you can replace this with your own image)
    # You can use a local file path or a URL
    image_path = input("Enter the path to your outfit image (or URL): ").strip()

    if not image_path:
        print("No image path provided. Using example URL...")
        # Example URL (replace with actual outfit image URL)
        image_path = "https://example.com/outfit.jpg"

    try:
        # Analyze the outfit
        print(f"\nAnalyzing outfit from: {image_path}")
        results = analyzer.analyze_outfit(image_path, save_results=True)

        # Print detailed results
        print_analysis_results(results)

        # Create visualization
        analyzer.visualize_analysis(results, save_path="outfit_analysis.png")

    except Exception as e:
        print(f"Error analyzing outfit: {e}")
        import traceback

        traceback.print_exc()


def print_analysis_results(results):
    """
    Print formatted analysis results.
    """
    print("\n" + "=" * 60)
    print("FASHION ANALYSIS RESULTS")
    print("=" * 60)

    # Overall analysis
    overall = results["overall_analysis"]
    print(f"\n📊 OVERALL OUTFIT ANALYSIS:")
    print(f"   • Total pieces detected: {overall['total_pieces']}")
    print(f"   • Dominant style: {overall['dominant_style']}")
    print(f"   • Style coherence: {overall['style_coherence']:.2f}")
    print(f"   • Color palette: {', '.join(overall['color_palette'])}")
    print(f"   • Fit variety: {', '.join(overall['fit_variety'])}")
    print(f"   • Categories: {', '.join(overall['categories'])}")
    print(f"   • Style assessment: {overall['style_assessment']}")

    # Individual pieces
    print(f"\n👕 INDIVIDUAL PIECES ANALYSIS:")
    for i, segment in enumerate(results["segments"], 1):
        print(f"\n   Piece {i}:")
        print(f"   • Description: {segment['summary']['description']}")
        print(f"   • Category: {segment['category']}")
        print(f"   • Confidence: {segment['confidence']:.2f}")
        print(f"   • Location: {segment['bbox']}")
        print(f"   • Area: {segment['area']:.0f} pixels")

        # Style details
        style_info = segment["style_analysis"]
        print(
            f"   • Style: {style_info['style']['best_match'][0]} ({style_info['style']['best_match'][1]:.2f})"
        )
        print(
            f"   • Color: {style_info['color']['best_match'][0]} ({style_info['color']['best_match'][1]:.2f})"
        )
        print(
            f"   • Fit: {style_info['fit']['best_match'][0]} ({style_info['fit']['best_match'][1]:.2f})"
        )
        print(
            f"   • Shape: {style_info['shape']['best_match'][0]} ({style_info['shape']['best_match'][1]:.2f})"
        )
        print(
            f"   • Material hint: {style_info['material']['best_match'][0]} ({style_info['material']['best_match'][1]:.2f})"
        )


def batch_analyze_outfits(image_folder):
    """
    Analyze multiple outfit images in a folder.
    """
    analyzer = FashionAnalyzer()

    # Supported image extensions
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"}

    # Get all image files in the folder
    image_files = []
    for file in os.listdir(image_folder):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            image_files.append(os.path.join(image_folder, file))

    if not image_files:
        print(f"No image files found in {image_folder}")
        return

    print(f"Found {len(image_files)} images to analyze")

    # Analyze each image
    for i, image_path in enumerate(image_files, 1):
        print(f"\n{'='*50}")
        print(f"Analyzing image {i}/{len(image_files)}: {os.path.basename(image_path)}")
        print(f"{'='*50}")

        try:
            results = analyzer.analyze_outfit(image_path, save_results=True)

            # Print summary
            overall = results["overall_analysis"]
            print(f"✓ {overall['total_pieces']} pieces detected")
            print(f"✓ Style: {overall['dominant_style']}")
            print(f"✓ Coherence: {overall['style_coherence']:.2f}")
            print(f"✓ Categories: {', '.join(overall['categories'])}")

        except Exception as e:
            print(f"✗ Error analyzing {image_path}: {e}")


def main():
    """
    Main function with menu options.
    """
    print("Fashion Analysis Tool")
    print("=" * 30)
    print("1. Analyze single outfit image")
    print("2. Batch analyze outfits from folder")
    print("3. Exit")

    choice = input("\nSelect an option (1-3): ").strip()

    if choice == "1":
        analyze_sample_outfit()
    elif choice == "2":
        folder_path = input("Enter folder path containing outfit images: ").strip()
        if os.path.exists(folder_path):
            batch_analyze_outfits(folder_path)
        else:
            print(f"Folder not found: {folder_path}")
    elif choice == "3":
        print("Goodbye!")
    else:
        print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
