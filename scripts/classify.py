"""
Step 3: Classify images into 6 categories using CLIP zero-shot classification.
Uses openai/clip-vit-base-patch32 via transformers (same model as album_cover_search project).
"""

import json
from pathlib import Path

import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from tqdm import tqdm

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_JSON = DATA_DIR / "pipeline.json"

MODEL_NAME = "openai/clip-vit-base-patch32"

# Multi-prompt descriptions per category for better accuracy
CATEGORY_PROMPTS = {
    "animal": [
        "a photo of Angela Merkel with an animal",
        "a photo of a politician with a dog or pet",
        "a photo of a politician with a bird or parrot",
        "a photo of a person at a zoo feeding animals",
        "a photo of a politician holding or petting an animal",
    ],
    "food": [
        "a photo of Angela Merkel eating food",
        "a photo of a politician drinking beer at a festival",
        "a photo of a politician holding a sausage or bratwurst",
        "a photo of a politician cutting or eating a cake",
        "a photo of a person eating or drinking beverages",
    ],
    "vintage": [
        "a black and white photo of a young Angela Merkel",
        "an old photograph from the 1980s or 1990s",
        "a vintage photo of a young woman in East Germany",
        "a grainy old photograph of a young politician",
        "a retro photograph with faded colors from decades ago",
    ],
    "technology": [
        "a photo of Angela Merkel with a robot or computer",
        "a photo of a politician visiting a science laboratory",
        "a photo of a politician with astronauts or space equipment",
        "a photo of a politician at a technology exhibition or CeBIT",
        "a photo of a person using a microscope or scientific instrument",
    ],
    "transport": [
        "a photo of Angela Merkel inside a car or vehicle",
        "a photo of a politician on a ship or submarine",
        "a photo of a politician next to an airplane or helicopter",
        "a photo of a politician visiting a train or railway station",
        "a photo of a person inside a military vehicle or tank",
    ],
    "sport": [
        "a photo of Angela Merkel playing sports",
        "a photo of a politician with a football or soccer ball",
        "a photo of a politician at the Olympics or a stadium",
        "a photo of a politician holding a handball or tennis ball",
        "a photo of a person doing physical activity or exercise",
    ],
}

CONFIDENCE_THRESHOLD = 0.20
MARGIN_THRESHOLD = 0.03


def load_pipeline():
    with open(PIPELINE_JSON) as f:
        return json.load(f)


def save_pipeline(data):
    with open(PIPELINE_JSON, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_device():
    """Get best available device: MPS (Apple Silicon) > CUDA > CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def main():
    pipeline = load_pipeline()

    # Filter to non-duplicate items without classification
    to_classify = [
        item for item in pipeline
        if not item.get("is_duplicate") and "category" not in item
    ]

    if not to_classify:
        print("No images to classify. Run collect.py and deduplicate.py first.")
        return

    print(f"Classifying {len(to_classify)} images...")

    # Load model
    device = get_device()
    print(f"Device: {device}")
    print(f"Loading CLIP model: {MODEL_NAME}...")

    model = CLIPModel.from_pretrained(MODEL_NAME).to(device)
    processor = CLIPProcessor.from_pretrained(MODEL_NAME)
    model.eval()

    # Pre-compute text embeddings for each category (averaged over prompts)
    print("Computing category text embeddings...")
    category_embeddings = {}
    categories = list(CATEGORY_PROMPTS.keys())

    with torch.no_grad():
        for cat, prompts in CATEGORY_PROMPTS.items():
            inputs = processor(text=prompts, return_tensors="pt", padding=True, truncation=True).to(device)
            text_embeds = model.get_text_features(**inputs)
            text_embeds = text_embeds / text_embeds.norm(dim=-1, keepdim=True)
            # Average the prompt embeddings
            avg_embed = text_embeds.mean(dim=0)
            avg_embed = avg_embed / avg_embed.norm()
            category_embeddings[cat] = avg_embed

    # Stack all category embeddings
    cat_names = list(category_embeddings.keys())
    cat_tensor = torch.stack([category_embeddings[c] for c in cat_names])

    # Classify each image
    print("Classifying images...")
    for item in tqdm(to_classify, desc="CLIP classification"):
        local_path = Path(__file__).parent / item.get("local_path", "")
        if not local_path.exists():
            continue

        try:
            image = Image.open(local_path).convert("RGB")
        except Exception:
            continue

        with torch.no_grad():
            inputs = processor(images=image, return_tensors="pt").to(device)
            image_embeds = model.get_image_features(**inputs)
            image_embeds = image_embeds / image_embeds.norm(dim=-1, keepdim=True)

            # Cosine similarity with each category
            similarities = (image_embeds @ cat_tensor.T).squeeze(0)
            scores = similarities.cpu().numpy()

        # Build scores dict
        score_dict = {cat: float(scores[i]) for i, cat in enumerate(cat_names)}
        sorted_scores = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)

        best_cat, best_score = sorted_scores[0]
        second_score = sorted_scores[1][1]

        item["category"] = best_cat
        item["category_scores"] = score_dict
        item["low_confidence"] = best_score < CONFIDENCE_THRESHOLD or (best_score - second_score) < MARGIN_THRESHOLD

    save_pipeline(pipeline)

    # Summary
    cat_counts = {}
    low_conf = 0
    for item in pipeline:
        if item.get("is_duplicate") or "category" not in item:
            continue
        cat = item["category"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
        if item.get("low_confidence"):
            low_conf += 1

    print("\nClassification results:")
    for cat in categories:
        count = cat_counts.get(cat, 0)
        print(f"  {cat:12s}: {count}")
    print(f"\n  Low confidence: {low_conf}")
    print("Done!")


if __name__ == "__main__":
    main()
