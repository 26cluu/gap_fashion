import os
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
import requests
from io import BytesIO
import json
from typing import List, Dict, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from transformers import (
    AutoImageProcessor,
    AutoModelForObjectDetection,
    CLIPProcessor,
    CLIPModel,
)
from collections import defaultdict


class FashionAnalyzer:
    """
    A comprehensive fashion analysis tool that segments outfits using Fashionpedia
    and analyzes individual pieces using FashionCLIP for style, fit, and shape analysis.
    """

    def __init__(self):
        """
        Initialize the FashionAnalyzer with Fashionpedia and FashionCLIP models.
        """
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")

        # Initialize Fashionpedia (YOLOS-Fashionpedia)
        print("Loading Fashionpedia model...")
        self.fashionpedia_processor = AutoImageProcessor.from_pretrained(
            "hustvl/yolos-fashionpedia"
        )
        self.fashionpedia_model = AutoModelForObjectDetection.from_pretrained(
            "hustvl/yolos-fashionpedia"
        )
        self.fashionpedia_model.to(self.device)

        # Initialize FashionCLIP by patrickjohncyh
        print("Loading FashionCLIP model...")
        self.clip_model = CLIPModel.from_pretrained("patrickjohncyh/fashion-clip")
        self.clip_processor = CLIPProcessor.from_pretrained(
            "patrickjohncyh/fashion-clip"
        )
        self.clip_model.to(self.device)

        # Fashion-specific text prompts for analysis (optimized for FashionCLIP)
        self.style_prompts = {
            "style": [
                "casual style",
                "formal style",
                "streetwear",
                "vintage",
                "minimalist",
                "bohemian",
                "preppy",
                "punk",
                "gothic",
                "sporty",
                "elegant",
                "romantic",
                "edgy",
                "classic",
                "trendy",
                "retro",
                "modern",
                "traditional",
                "luxury",
                "athleisure",
                "business casual",
                "evening wear",
                "day wear",
            ],
            "color": [
                "black",
                "white",
                "red",
                "blue",
                "green",
                "yellow",
                "purple",
                "pink",
                "orange",
                "brown",
                "gray",
                "navy",
                "beige",
                "cream",
                "olive",
                "burgundy",
                "maroon",
                "teal",
                "coral",
                "lavender",
                "gold",
                "silver",
                "bronze",
            ],
            "fit": [
                "loose fit",
                "tight fit",
                "regular fit",
                "oversized",
                "slim fit",
                "relaxed fit",
                "fitted",
                "baggy",
                "tailored",
                "comfortable",
                "skinny",
                "wide leg",
                "straight leg",
                "bootcut",
                "flare",
                "tapered",
            ],
            "shape": [
                "round neck",
                "v-neck",
                "square neck",
                "collar",
                "sleeveless",
                "long sleeve",
                "short sleeve",
                "wide leg",
                "skinny leg",
                "straight leg",
                "flared",
                "tapered",
                "boxy",
                "flowy",
                "structured",
                "asymmetric",
                "high waist",
                "low waist",
                "mid rise",
                "crop top",
                "tunic",
            ],
            "material": [
                "cotton",
                "denim",
                "silk",
                "wool",
                "leather",
                "synthetic",
                "linen",
                "polyester",
                "cashmere",
                "velvet",
                "suede",
                "mesh",
                "knit",
                "jersey",
                "chiffon",
                "satin",
                "tweed",
                "corduroy",
                "flannel",
                "lace",
            ],
        }

    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file path or URL.

        Args:
            image_path: Path to image file or URL

        Returns:
            Loaded image as numpy array
        """
        if image_path.startswith(("http://", "https://")):
            response = requests.get(image_path)
            image = Image.open(BytesIO(response.content))
        else:
            image = Image.open(image_path)

        return np.array(image)

    def segment_outfit(self, image: np.ndarray) -> List[Dict]:
        """
        Segment the outfit into individual clothing pieces using Fashionpedia.

        Args:
            image: Input image as numpy array

        Returns:
            List of dictionaries containing segment information
        """
        # Convert to PIL Image for Fashionpedia processing
        pil_image = Image.fromarray(image)

        # Prepare inputs for Fashionpedia
        inputs = self.fashionpedia_processor(images=pil_image, return_tensors="pt").to(
            self.device
        )

        # Get predictions
        with torch.no_grad():
            outputs = self.fashionpedia_model(**inputs)

        # Post-process outputs
        target_sizes = torch.tensor([pil_image.size[::-1]]).to(self.device)
        results = self.fashionpedia_processor.post_process_object_detection(
            outputs, target_sizes=target_sizes, threshold=0.5
        )[0]

        segments = []

        # Process detected objects
        for score, label, box in zip(
            results["scores"], results["labels"], results["boxes"]
        ):
            # Convert box coordinates to integers
            x1, y1, x2, y2 = box.cpu().numpy().astype(int)

            # Get label name
            label_name = self.fashionpedia_model.config.id2label[label.item()]

            # Create segment
            segment = {
                "id": len(segments),
                "bbox": [x1, y1, x2 - x1, y2 - y1],  # [x, y, w, h]
                "area": (x2 - x1) * (y2 - y1),
                "category": label_name,
                "confidence": score.item(),
                "image_region": image[y1:y2, x1:x2],
                "box_coords": [x1, y1, x2, y2],  # [x1, y1, x2, y2]
            }
            segments.append(segment)

        # If no segments found, create a default segment for the whole image
        if not segments:
            segments.append(
                {
                    "id": 0,
                    "bbox": [0, 0, image.shape[1], image.shape[0]],
                    "area": image.shape[0] * image.shape[1],
                    "category": "unknown",
                    "confidence": 1.0,
                    "image_region": image,
                    "box_coords": [0, 0, image.shape[1], image.shape[0]],
                }
            )

        return segments

    def get_clip_embeddings(
        self, image_region: np.ndarray, text_prompts: List[str]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get FashionCLIP embeddings for image and text prompts.

        Args:
            image_region: Image region as numpy array
            text_prompts: List of text prompts

        Returns:
            Tuple of (image_embeddings, text_embeddings)
        """
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(image_region)

        # Process image and text
        inputs = self.clip_processor(
            images=pil_image,
            text=text_prompts,
            return_tensors="pt",
            padding=True,
            truncation=True,
        ).to(self.device)

        # Get embeddings
        with torch.no_grad():
            outputs = self.clip_model(**inputs)
            image_embeddings = outputs.image_embeds
            text_embeddings = outputs.text_embeds

        return image_embeddings.cpu().numpy(), text_embeddings.cpu().numpy()

    def analyze_style(self, image_region: np.ndarray) -> Dict:
        """
        Analyze the style of a clothing piece using FashionCLIP.

        Args:
            image_region: Image region as numpy array

        Returns:
            Dictionary containing style analysis
        """
        style_analysis = {}

        for category, prompts in self.style_prompts.items():
            # Get embeddings
            image_emb, text_emb = self.get_clip_embeddings(image_region, prompts)

            # Calculate similarities
            similarities = F.cosine_similarity(
                torch.from_numpy(image_emb), torch.from_numpy(text_emb), dim=1
            ).numpy()

            # Get top matches
            top_indices = np.argsort(similarities)[::-1][:3]
            top_matches = [(prompts[i], similarities[i]) for i in top_indices]

            style_analysis[category] = {
                "top_matches": top_matches,
                "confidence_scores": similarities.tolist(),
                "best_match": top_matches[0] if top_matches else (None, 0.0),
            }

        return style_analysis

    def analyze_outfit(self, image_path: str, save_results: bool = True) -> Dict:
        """
        Complete outfit analysis pipeline.

        Args:
            image_path: Path to outfit image
            save_results: Whether to save results to file

        Returns:
            Complete analysis results
        """
        print(f"Analyzing outfit from: {image_path}")

        # Load image
        image = self.load_image(image_path)
        print(f"Image loaded: {image.shape}")

        # Segment outfit using Fashionpedia
        print("Segmenting outfit using Fashionpedia...")
        segments = self.segment_outfit(image)
        print(f"Found {len(segments)} clothing segments")

        # Analyze each segment
        analysis_results = {
            "image_path": image_path,
            "image_shape": image.shape,
            "segments": [],
            "overall_analysis": {},
        }

        for segment in segments:
            print(f"Analyzing segment {segment['id']} ({segment['category']})...")

            # Style analysis using FashionCLIP
            style_analysis = self.analyze_style(segment["image_region"])

            # Combine all analyses
            segment_analysis = {
                "segment_id": segment["id"],
                "bbox": segment["bbox"],
                "area": segment["area"],
                "category": segment["category"],
                "confidence": segment["confidence"],
                "style_analysis": style_analysis,
                "summary": self._create_segment_summary(
                    style_analysis, segment["category"]
                ),
            }

            analysis_results["segments"].append(segment_analysis)

        # Create overall outfit analysis
        analysis_results["overall_analysis"] = self._create_overall_analysis(
            analysis_results["segments"]
        )

        # Save results if requested
        if save_results:
            output_path = (
                f"outfit_analysis_{os.path.basename(image_path).split('.')[0]}.json"
            )
            with open(output_path, "w") as f:
                json.dump(analysis_results, f, indent=2, default=str)
            print(f"Analysis saved to: {output_path}")

        return analysis_results

    def _create_segment_summary(self, style_analysis: Dict, category: str) -> Dict:
        """
        Create a summary for a clothing segment.
        """
        # Get dominant style characteristics
        dominant_style = (
            style_analysis["style"]["best_match"][0]
            if style_analysis["style"]["best_match"][0]
            else "unknown"
        )
        dominant_color = (
            style_analysis["color"]["best_match"][0]
            if style_analysis["color"]["best_match"][0]
            else "unknown"
        )
        fit_type = (
            style_analysis["fit"]["best_match"][0]
            if style_analysis["fit"]["best_match"][0]
            else "unknown"
        )
        shape_type = (
            style_analysis["shape"]["best_match"][0]
            if style_analysis["shape"]["best_match"][0]
            else "unknown"
        )

        return {
            "description": f"A {dominant_color} {category} with {dominant_style} style and {fit_type} fit",
            "key_features": {
                "category": category,
                "style": dominant_style,
                "color": dominant_color,
                "fit": fit_type,
                "shape": shape_type,
                "material_hint": (
                    style_analysis["material"]["best_match"][0]
                    if style_analysis["material"]["best_match"][0]
                    else "unknown"
                ),
            },
        }

    def _create_overall_analysis(self, segments: List[Dict]) -> Dict:
        """
        Create overall outfit analysis from individual segments.
        """
        if not segments:
            return {}

        # Aggregate styles
        all_styles = [
            seg["style_analysis"]["style"]["best_match"][0] for seg in segments
        ]
        all_colors = [
            seg["style_analysis"]["color"]["best_match"][0] for seg in segments
        ]
        all_fits = [seg["style_analysis"]["fit"]["best_match"][0] for seg in segments]
        all_categories = [seg["category"] for seg in segments]

        # Calculate outfit coherence
        unique_styles = len(set(all_styles))
        unique_colors = len(set(all_colors))
        style_coherence = 1.0 - (unique_styles / len(segments))

        # Determine overall style
        style_counts = defaultdict(int)
        for style in all_styles:
            style_counts[style] += 1
        dominant_outfit_style = (
            max(style_counts.items(), key=lambda x: x[1])[0]
            if style_counts
            else "mixed"
        )

        return {
            "total_pieces": len(segments),
            "style_coherence": style_coherence,
            "dominant_style": dominant_outfit_style,
            "color_palette": list(set(all_colors)),
            "fit_variety": list(set(all_fits)),
            "categories": list(set(all_categories)),
            "outfit_complexity": len(segments),
            "style_assessment": self._assess_outfit_style(
                style_coherence, unique_colors, len(segments)
            ),
        }

    def _assess_outfit_style(
        self, coherence: float, color_variety: int, piece_count: int
    ) -> str:
        """
        Assess the overall style of the outfit.
        """
        if coherence > 0.8 and color_variety <= 3:
            return "Cohesive and well-coordinated"
        elif coherence > 0.6:
            return "Balanced with some variety"
        elif piece_count > 5:
            return "Complex layered look"
        else:
            return "Eclectic mix"

    def visualize_analysis(
        self, analysis_results: Dict, save_path: Optional[str] = None
    ):
        """
        Visualize the analysis results with bounding boxes and labels.
        """
        # Load original image
        image = self.load_image(analysis_results["image_path"])

        # Create figure
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        ax.imshow(image)

        # Draw bounding boxes and labels
        for segment in analysis_results["segments"]:
            bbox = segment["bbox"]
            x, y, w, h = bbox

            # Create rectangle
            rect = patches.Rectangle(
                (x, y), w, h, linewidth=2, edgecolor="red", facecolor="none"
            )
            ax.add_patch(rect)

            # Add label
            summary = segment["summary"]["description"]
            ax.text(
                x,
                y - 10,
                f"{segment['category']}: {summary[:50]}...",
                fontsize=8,
                color="red",
                weight="bold",
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8),
            )

        ax.set_title(
            f"Outfit Analysis - {analysis_results['overall_analysis']['dominant_style']} Style"
        )
        ax.axis("off")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Visualization saved to: {save_path}")

        plt.show()


def main():
    """
    Main function to demonstrate the FashionAnalyzer.
    """
    # Initialize analyzer
    analyzer = FashionAnalyzer()

    # Example usage
    image_path = input("Enter the path to your outfit image: ").strip()

    if not os.path.exists(image_path):
        print(f"Error: Image file not found at {image_path}")
        return

    try:
        # Analyze outfit
        results = analyzer.analyze_outfit(image_path, save_results=True)

        # Print summary
        print("\n" + "=" * 50)
        print("OUTFIT ANALYSIS SUMMARY")
        print("=" * 50)

        overall = results["overall_analysis"]
        print(f"Total pieces detected: {overall['total_pieces']}")
        print(f"Overall style: {overall['dominant_style']}")
        print(f"Style coherence: {overall['style_coherence']:.2f}")
        print(f"Color palette: {', '.join(overall['color_palette'])}")
        print(f"Categories: {', '.join(overall['categories'])}")
        print(f"Style assessment: {overall['style_assessment']}")

        print(f"\nIndividual pieces:")
        for i, segment in enumerate(results["segments"]):
            print(f"  Piece {i+1}: {segment['summary']['description']}")

        # Visualize results
        analyzer.visualize_analysis(
            results, save_path="outfit_analysis_visualization.png"
        )

    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
