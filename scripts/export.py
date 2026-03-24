"""
Step 7: Generate src/data/items.js from pipeline data.
Exports approved + uploaded images in the exact format the Next.js app expects.
"""

import json
import random
import shutil
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_JSON = DATA_DIR / "pipeline.json"
PROJECT_ROOT = Path(__file__).parent.parent
ITEMS_JS = PROJECT_ROOT / "src" / "data" / "items.js"
ITEMS_BACKUP = PROJECT_ROOT / "src" / "data" / "items.backup.js"

CATEGORIES = ["animal", "food", "vintage", "technology", "transport", "sport"]


def load_pipeline():
    with open(PIPELINE_JSON) as f:
        return json.load(f)


def format_js_string(s):
    """Escape string for JavaScript."""
    return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def main():
    pipeline = load_pipeline()

    # Filter to items with Supabase URLs
    items = [
        item for item in pipeline
        if "supabase_url" in item and not item.get("is_duplicate")
    ]

    if not items:
        print("No uploaded images found. Run upload.py first.")
        return

    # Sort by category then by confidence
    items.sort(key=lambda x: (
        CATEGORIES.index(x.get("category", "")) if x.get("category", "") in CATEGORIES else 99,
        -max(x.get("category_scores", {}).values()) if x.get("category_scores") else 0
    ))

    # Backup existing file
    if ITEMS_JS.exists():
        shutil.copy2(ITEMS_JS, ITEMS_BACKUP)
        print(f"Backup created: {ITEMS_BACKUP}")

    # Generate JavaScript
    js_items = []
    for idx, item in enumerate(items, start=1):
        parallax_speed = round(random.uniform(0.01, 0.085), 3)
        category = item.get("category", "")
        alt = format_js_string(item.get("alt", ""))
        legende = format_js_string(item.get("legende", ""))
        place = format_js_string(item.get("place", ""))
        keywords = item.get("keywords", [])
        img_url = item.get("supabase_url", "")

        kw_str = json.dumps(keywords)

        entry = f"""  {{
    img: "{img_url}",
    alt: "{alt}",
    legende: "{legende}",
    id: {idx},
    parllaxSpeed: {parallax_speed},
    place: "{place}",
    category: "{category}",
    keyWord: {kw_str}
  }}"""
        js_items.append(entry)

    js_content = "const items = [\n" + ",\n".join(js_items) + "\n];\n\nexport { items };\n"

    ITEMS_JS.parent.mkdir(parents=True, exist_ok=True)
    with open(ITEMS_JS, "w") as f:
        f.write(js_content)

    # Summary
    cat_counts = {}
    for item in items:
        cat = item.get("category", "unknown")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1

    print(f"\nExported {len(items)} items to {ITEMS_JS}")
    print("\nPer category:")
    for cat in CATEGORIES:
        count = cat_counts.get(cat, 0)
        print(f"  {cat:12s}: {count}")


if __name__ == "__main__":
    main()
