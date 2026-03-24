"""
Step 6: Upload approved images to Supabase Storage.
Reads review_decisions.json, resizes images, uploads to bucket.
"""

import json
import os
from pathlib import Path
from io import BytesIO

from PIL import Image
from dotenv import load_dotenv
from supabase import create_client
from tqdm import tqdm

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_JSON = DATA_DIR / "pipeline.json"
DECISIONS_JSON = DATA_DIR / "review_decisions.json"

BUCKET_NAME = "mutti-photos"
MAX_DIMENSION = 1200
JPEG_QUALITY = 85


def load_pipeline():
    with open(PIPELINE_JSON) as f:
        return json.load(f)


def save_pipeline(data):
    with open(PIPELINE_JSON, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_decisions():
    if not DECISIONS_JSON.exists():
        print(f"Error: {DECISIONS_JSON} not found.")
        print("Run review.py, open the HTML gallery, curate images, and export decisions first.")
        return None
    with open(DECISIONS_JSON) as f:
        return json.load(f)


def optimize_image(image_path):
    """Resize and compress image for web. Returns JPEG bytes."""
    with Image.open(image_path) as img:
        img = img.convert("RGB")

        # Strip EXIF
        data = list(img.getdata())
        clean = Image.new(img.mode, img.size)
        clean.putdata(data)

        # Resize if needed
        w, h = clean.size
        if max(w, h) > MAX_DIMENSION:
            ratio = MAX_DIMENSION / max(w, h)
            new_size = (int(w * ratio), int(h * ratio))
            clean = clean.resize(new_size, Image.LANCZOS)

        buf = BytesIO()
        clean.save(buf, "JPEG", quality=JPEG_QUALITY, optimize=True)
        return buf.getvalue()


def main():
    # Load env
    load_dotenv(Path(__file__).parent / ".env")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY")

    if not supabase_url or not supabase_key:
        print("Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in scripts/.env")
        print("See .env.example for reference.")
        return

    # Load data
    pipeline = load_pipeline()
    decisions = load_decisions()
    if decisions is None:
        return

    approved_ids = set(decisions.get("approved", []))
    category_overrides = decisions.get("category_overrides", {})
    captions = decisions.get("captions", {})

    # Apply overrides and captions
    items_by_id = {item["id"]: item for item in pipeline}
    for item_id, new_cat in category_overrides.items():
        if item_id in items_by_id:
            items_by_id[item_id]["category"] = new_cat
    for item_id, cap in captions.items():
        if item_id in items_by_id:
            if "alt" in cap:
                items_by_id[item_id]["alt"] = cap["alt"]
            if "legende" in cap:
                items_by_id[item_id]["legende"] = cap["legende"]

    # Filter to approved items
    to_upload = [
        item for item in pipeline
        if item["id"] in approved_ids and "supabase_url" not in item
    ]

    already_uploaded = sum(1 for item in pipeline if item["id"] in approved_ids and "supabase_url" in item)

    if not to_upload and already_uploaded == 0:
        print("No approved images to upload.")
        return

    if already_uploaded:
        print(f"Already uploaded: {already_uploaded}")

    print(f"Uploading {len(to_upload)} images to Supabase Storage...")

    # Connect to Supabase
    supabase = create_client(supabase_url, supabase_key)

    uploaded = 0
    errors = 0

    for item in tqdm(to_upload, desc="Uploading"):
        local_path = Path(__file__).parent / item.get("local_path", "")
        if not local_path.exists():
            print(f"\n  Missing: {local_path}")
            errors += 1
            continue

        category = item.get("category", "uncategorized")
        storage_path = f"{category}/{item['id']}.jpg"

        try:
            # Optimize image
            img_bytes = optimize_image(local_path)

            # Upload
            supabase.storage.from_(BUCKET_NAME).upload(
                storage_path,
                img_bytes,
                {"content-type": "image/jpeg"}
            )

            # Get public URL
            public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
            item["supabase_url"] = public_url
            uploaded += 1

        except Exception as e:
            error_msg = str(e)
            if "Duplicate" in error_msg or "already exists" in error_msg:
                # File already exists, just get the URL
                public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(storage_path)
                item["supabase_url"] = public_url
                uploaded += 1
            else:
                print(f"\n  Upload error for {item['id']}: {e}")
                errors += 1

    save_pipeline(pipeline)
    print(f"\nDone! Uploaded: {uploaded} | Errors: {errors}")
    print(f"Total with Supabase URLs: {sum(1 for item in pipeline if 'supabase_url' in item)}")

    # Cleanup local images
    images_dir = DATA_DIR / "images"
    if images_dir.exists():
        import shutil
        size_mb = sum(f.stat().st_size for f in images_dir.rglob("*") if f.is_file()) / (1024 * 1024)
        print(f"\nLocal images folder: {size_mb:.0f}MB")
        answer = input("Delete local images? (y/n): ").strip().lower()
        if answer == "y":
            shutil.rmtree(images_dir)
            print("Local images deleted.")


if __name__ == "__main__":
    main()
