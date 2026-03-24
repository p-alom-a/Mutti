"""
Step 2: Remove near-duplicate images using perceptual hashing.
Marks duplicates in pipeline.json, keeping the highest-resolution version.
"""

import json
from pathlib import Path

import imagehash
from PIL import Image
from tqdm import tqdm

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_JSON = DATA_DIR / "pipeline.json"

HASH_THRESHOLD = 8  # Hamming distance threshold for duplicates
MIN_SIZE = 400  # Minimum pixels on shortest side


def load_pipeline():
    with open(PIPELINE_JSON) as f:
        return json.load(f)


def save_pipeline(data):
    with open(PIPELINE_JSON, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def compute_phash(image_path):
    """Compute perceptual hash of an image."""
    try:
        with Image.open(image_path) as img:
            return imagehash.phash(img)
    except Exception:
        return None


def main():
    pipeline = load_pipeline()
    print(f"Processing {len(pipeline)} images...")

    # Compute hashes
    hashes = []
    for item in tqdm(pipeline, desc="Computing hashes"):
        if "phash" in item and item.get("is_duplicate") is not None:
            # Already processed
            hashes.append((item.get("phash"), item))
            continue

        local_path = Path(__file__).parent / item.get("local_path", "")
        if not local_path.exists():
            item["is_duplicate"] = True
            item["duplicate_reason"] = "file_missing"
            hashes.append((None, item))
            continue

        # Validate size
        try:
            with Image.open(local_path) as img:
                w, h = img.size
                item["width"] = w
                item["height"] = h
        except Exception:
            item["is_duplicate"] = True
            item["duplicate_reason"] = "corrupt"
            hashes.append((None, item))
            continue

        if min(w, h) < MIN_SIZE:
            item["is_duplicate"] = True
            item["duplicate_reason"] = "too_small"
            hashes.append((None, item))
            continue

        h = compute_phash(local_path)
        if h is None:
            item["is_duplicate"] = True
            item["duplicate_reason"] = "hash_failed"
            hashes.append((None, item))
            continue

        item["phash"] = str(h)
        hashes.append((h, item))

    # Find duplicates - compare all pairs
    print("\nFinding duplicates...")
    valid_items = [(h, item) for h, item in hashes if h is not None and not item.get("is_duplicate")]

    duplicate_groups = []
    visited = set()

    for i, (hash_i, item_i) in enumerate(valid_items):
        if item_i["id"] in visited:
            continue

        group = [item_i]
        visited.add(item_i["id"])

        hash_obj_i = imagehash.hex_to_hash(str(hash_i)) if isinstance(hash_i, str) else hash_i

        for j in range(i + 1, len(valid_items)):
            hash_j, item_j = valid_items[j]
            if item_j["id"] in visited:
                continue

            hash_obj_j = imagehash.hex_to_hash(str(hash_j)) if isinstance(hash_j, str) else hash_j

            distance = hash_obj_i - hash_obj_j
            if distance <= HASH_THRESHOLD:
                group.append(item_j)
                visited.add(item_j["id"])

        if len(group) > 1:
            duplicate_groups.append(group)

    # Mark duplicates, keeping highest resolution
    duplicates_found = 0
    for group in duplicate_groups:
        # Sort by resolution (width * height), keep the largest
        group.sort(key=lambda x: x.get("width", 0) * x.get("height", 0), reverse=True)
        keeper = group[0]
        for dupe in group[1:]:
            dupe["is_duplicate"] = True
            dupe["duplicate_of"] = keeper["id"]
            dupe["duplicate_reason"] = "near_duplicate"
            duplicates_found += 1

    # Mark non-duplicates explicitly
    for h, item in hashes:
        if "is_duplicate" not in item:
            item["is_duplicate"] = False

    save_pipeline(pipeline)

    total = len(pipeline)
    dupes = sum(1 for item in pipeline if item.get("is_duplicate"))
    valid = total - dupes
    print(f"\nDone! {duplicates_found} near-duplicates found in {len(duplicate_groups)} groups.")
    print(f"Total: {total} | Valid: {valid} | Duplicates/Invalid: {dupes}")


if __name__ == "__main__":
    main()
