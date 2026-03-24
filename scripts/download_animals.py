"""Download the 10 curated animal category images from pipeline.json."""
import json
import os
import time
from pathlib import Path

import requests
from PIL import Image

DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = DATA_DIR / "images"
PIPELINE_JSON = DATA_DIR / "pipeline.json"

HEADERS = {
    "User-Agent": "MuttiPhotoCollector/1.0 (photography art project)"
}

# Fallback URLs if _6000 doesn't work for DW images
DW_FALLBACK_SIZES = ["_6000", "_1006", "_804", "_702"]


def download(url, dest, timeout=15):
    """Download image, return True on success."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        if resp.status_code == 404 and "static.dw.com" in url:
            # Try fallback sizes for DW images
            for size in DW_FALLBACK_SIZES:
                fallback = url.rsplit("_", 1)[0] + size + ".jpg"
                if fallback == url:
                    continue
                print(f"    Trying fallback: {size}")
                resp = requests.get(fallback, headers=HEADERS, timeout=timeout)
                if resp.status_code == 200 and len(resp.content) > 5000:
                    break
        resp.raise_for_status()
        if len(resp.content) < 5000:
            print(f"    Too small ({len(resp.content)} bytes), skipping")
            return False
        with open(dest, "wb") as f:
            f.write(resp.content)
        # Validate and convert to JPEG
        with Image.open(dest) as img:
            img = img.convert("RGB")
            jpg = dest.with_suffix(".jpg")
            img.save(jpg, "JPEG", quality=92)
            if str(jpg) != str(dest) and dest.exists():
                os.remove(dest)
        return True
    except Exception as e:
        print(f"    Error: {e}")
        if dest.exists():
            os.remove(dest)
        return False


def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)

    with open(PIPELINE_JSON) as f:
        items = json.load(f)

    print(f"Downloading {len(items)} animal images...\n")
    success = 0

    for item in items:
        img_id = item["id"]
        url = item["source_url"]
        dest = IMAGES_DIR / f"{img_id}.jpg"

        if dest.exists():
            print(f"  [SKIP] {img_id} (already exists)")
            item["local_path"] = str(dest.relative_to(Path(__file__).parent))
            success += 1
            continue

        print(f"  [{items.index(item)+1}/{len(items)}] {img_id}")
        print(f"    URL: {url[:80]}...")

        if download(url, dest):
            with Image.open(dest) as img:
                w, h = img.size
                item["width"] = w
                item["height"] = h
            item["local_path"] = str(dest.relative_to(Path(__file__).parent))
            print(f"    OK ({w}x{h})")
            success += 1
        else:
            print(f"    FAILED")

        time.sleep(0.5)

    # Save updated pipeline
    with open(PIPELINE_JSON, "w") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"\nDone! {success}/{len(items)} images downloaded to {IMAGES_DIR}")


if __name__ == "__main__":
    main()
