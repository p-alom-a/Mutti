"""
Step 1: Collect candidate images of Angela Merkel from Wikimedia Commons and DuckDuckGo.
Downloads images to scripts/data/images/ and updates pipeline.json.
"""

import json
import hashlib
import time
import os
import sys
from pathlib import Path
from io import BytesIO

import requests
from PIL import Image
from tqdm import tqdm

DATA_DIR = Path(__file__).parent / "data"
IMAGES_DIR = DATA_DIR / "images"
PIPELINE_JSON = DATA_DIR / "pipeline.json"

MIN_SIZE = 400  # minimum pixels on shortest side
WIKIMEDIA_DELAY = 1.0  # seconds between API calls
DDG_DELAY = 2.0  # seconds between DDG batches

HEADERS = {
    "User-Agent": "MuttiPhotoCollector/1.0 (photography art project; contact: github.com/mutti)"
}

# Category-biased search queries
CATEGORY_QUERIES = {
    "animal": [
        '"Angela Merkel" animal',
        '"Angela Merkel" dog',
        '"Angela Merkel" bird parrot',
        '"Angela Merkel" zoo',
    ],
    "food": [
        '"Angela Merkel" food eating',
        '"Angela Merkel" beer drinking',
        '"Angela Merkel" sausage bratwurst',
        '"Angela Merkel" cake',
    ],
    "vintage": [
        '"Angela Merkel" young 1990',
        '"Angela Merkel" DDR GDR',
        '"Angela Merkel" old photo vintage',
        'Angela Merkel 1980s',
    ],
    "technology": [
        '"Angela Merkel" robot technology',
        '"Angela Merkel" computer science laboratory',
        '"Angela Merkel" astronaut space',
        '"Angela Merkel" CeBIT technology fair',
    ],
    "transport": [
        '"Angela Merkel" car vehicle',
        '"Angela Merkel" submarine ship',
        '"Angela Merkel" airplane helicopter',
        '"Angela Merkel" train railway',
    ],
    "sport": [
        '"Angela Merkel" sport football soccer',
        '"Angela Merkel" handball ball',
        '"Angela Merkel" olympic athlete',
        '"Angela Merkel" sport playing',
    ],
}


def load_pipeline():
    """Load existing pipeline data or initialize empty list."""
    if PIPELINE_JSON.exists():
        with open(PIPELINE_JSON) as f:
            return json.load(f)
    return []


def save_pipeline(data):
    """Save pipeline data to JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PIPELINE_JSON, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_existing_urls(data):
    """Get set of already-collected source URLs."""
    return {item["source_url"] for item in data}


def validate_image(path):
    """Check if file is a valid image with minimum size."""
    try:
        with Image.open(path) as img:
            img.verify()
        with Image.open(path) as img:
            w, h = img.size
            if min(w, h) < MIN_SIZE:
                return None
            return w, h
    except Exception:
        return None


def download_image(url, dest_path, timeout=15, retries=3):
    """Download image from URL with retry on rate-limit. Return True on success."""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=timeout)
            if resp.status_code == 429:
                wait = 2 ** (attempt + 1)  # 2s, 4s, 8s
                print(f"\n    Rate limited, waiting {wait}s...")
                time.sleep(wait)
                continue
            resp.raise_for_status()

            raw_bytes = resp.content
            if len(raw_bytes) < 5000:
                return False

            with open(dest_path, "wb") as f:
                f.write(raw_bytes)

            # Validate and convert to JPEG
            try:
                with Image.open(dest_path) as img:
                    img = img.convert("RGB")
                    jpeg_path = dest_path.with_suffix(".jpg")
                    img.save(jpeg_path, "JPEG", quality=90)
                    if str(jpeg_path) != str(dest_path) and dest_path.exists():
                        os.remove(dest_path)
                return True
            except Exception:
                if dest_path.exists():
                    os.remove(dest_path)
                return False
        except Exception:
            if dest_path.exists():
                os.remove(dest_path)
            if attempt < retries - 1:
                time.sleep(1)
    return False


# --- Wikimedia Commons ---

def search_wikimedia(query, limit=50):
    """Search Wikimedia Commons for images matching query."""
    results = []
    params = {
        "action": "query",
        "format": "json",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,  # File namespace
        "gsrlimit": min(limit, 50),
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 1200,
    }
    url = "https://commons.wikimedia.org/w/api.php"
    continuation = {}

    while len(results) < limit:
        resp = requests.get(url, params={**params, **continuation}, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page in pages.items():
            imageinfo = page.get("imageinfo", [{}])[0]
            mime = imageinfo.get("mime", "")
            if mime not in ("image/jpeg", "image/png"):
                continue
            width = imageinfo.get("width", 0)
            height = imageinfo.get("height", 0)
            if min(width, height) < MIN_SIZE:
                continue

            # Prefer thumburl (resized to 1200px) but fall back to full URL
            img_url = imageinfo.get("thumburl") or imageinfo.get("url")
            # If thumburl looks broken or too small, use the original
            if not img_url or "/thumb/" not in str(img_url):
                img_url = imageinfo.get("url", "")
            if not img_url:
                continue

            results.append({
                "id": f"wikimedia_{page_id}",
                "source": "wikimedia",
                "source_url": img_url,
                "page_url": page.get("title", ""),
                "width": width,
                "height": height,
            })

        if "continue" not in data:
            break
        continuation = data["continue"]
        time.sleep(WIKIMEDIA_DELAY)

    return results[:limit]


def collect_wikimedia(existing_urls):
    """Collect images from Wikimedia Commons."""
    all_results = []

    # General search
    print("  Wikimedia: general search...")
    general = search_wikimedia('"Angela Merkel"', limit=60)
    all_results.extend(general)
    time.sleep(WIKIMEDIA_DELAY)

    # Category-biased searches
    for category, queries in CATEGORY_QUERIES.items():
        for query in queries:
            print(f"  Wikimedia: {category} - {query[:40]}...")
            results = search_wikimedia(query, limit=15)
            all_results.extend(results)
            time.sleep(WIKIMEDIA_DELAY)

    # Deduplicate by source_url
    seen = set()
    unique = []
    for r in all_results:
        if r["source_url"] not in seen and r["source_url"] not in existing_urls:
            seen.add(r["source_url"])
            unique.append(r)

    return unique


# --- DuckDuckGo ---

def collect_duckduckgo(existing_urls):
    """Collect images from DuckDuckGo image search."""
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        print("  duckduckgo-search not installed, skipping DDG collection")
        return []

    all_results = []

    queries = [
        "Angela Merkel funny",
        "Angela Merkel animal dog bird",
        "Angela Merkel eating food beer sausage",
        "Angela Merkel young vintage DDR",
        "Angela Merkel technology robot science",
        "Angela Merkel car submarine airplane",
        "Angela Merkel sport football handball",
        "Angela Merkel cooking kitchen",
        "Angela Merkel nature outdoor",
    ]

    ddgs = DDGS()
    for query in queries:
        print(f"  DDG: {query[:40]}...")
        try:
            results = ddgs.images(query, max_results=15)
            for r in results:
                img_url = r.get("image", "")
                if not img_url or img_url in existing_urls:
                    continue
                url_hash = hashlib.md5(img_url.encode()).hexdigest()[:12]
                all_results.append({
                    "id": f"ddg_{url_hash}",
                    "source": "duckduckgo",
                    "source_url": img_url,
                    "title": r.get("title", ""),
                })
        except Exception as e:
            print(f"    DDG error: {e}")
        time.sleep(DDG_DELAY)

    # Deduplicate
    seen = set()
    unique = []
    for r in all_results:
        if r["source_url"] not in seen:
            seen.add(r["source_url"])
            unique.append(r)

    return unique


# --- Main ---

def main():
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    pipeline = load_pipeline()
    existing_urls = get_existing_urls(pipeline)

    print(f"Existing items: {len(pipeline)}")
    print()

    # Collect from sources
    print("=== Collecting from Wikimedia Commons ===")
    wiki_results = collect_wikimedia(existing_urls)
    print(f"  Found {len(wiki_results)} new candidates")
    print()

    print("=== Collecting from DuckDuckGo ===")
    ddg_results = collect_duckduckgo(existing_urls)
    print(f"  Found {len(ddg_results)} new candidates")
    print()

    all_new = wiki_results + ddg_results
    print(f"=== Downloading {len(all_new)} images ===")

    downloaded = 0
    for item in tqdm(all_new, desc="Downloading"):
        filename = f"{item['id']}.jpg"
        dest = IMAGES_DIR / filename

        if dest.exists():
            item["local_path"] = str(dest.relative_to(DATA_DIR.parent))
            dims = validate_image(dest)
            if dims:
                item["width"], item["height"] = dims
                pipeline.append(item)
                downloaded += 1
            continue

        success = download_image(item["source_url"], dest)
        time.sleep(0.5)  # Rate limit: 2 downloads/sec max
        if success:
            dims = validate_image(dest)
            if dims:
                item["local_path"] = str(dest.relative_to(DATA_DIR.parent))
                item["width"], item["height"] = dims
                pipeline.append(item)
                downloaded += 1
            else:
                # Remove invalid image
                if dest.exists():
                    os.remove(dest)

    save_pipeline(pipeline)
    print(f"\nDone! Downloaded {downloaded} new images. Total: {len(pipeline)}")


if __name__ == "__main__":
    main()
