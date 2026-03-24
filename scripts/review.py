"""
Step 5: Generate an HTML review gallery for manual curation.
Opens in any browser. User approves/rejects images and exports decisions.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
PIPELINE_JSON = DATA_DIR / "pipeline.json"
REVIEW_HTML = DATA_DIR / "review.html"

CATEGORIES = ["animal", "food", "vintage", "technology", "transport", "sport"]
TARGET_PER_CATEGORY = 17  # ~100 total across 6 categories


def load_pipeline():
    with open(PIPELINE_JSON) as f:
        return json.load(f)


def generate_html(pipeline):
    """Generate standalone HTML review gallery."""

    # Group items by category
    by_category = {cat: [] for cat in CATEGORIES}
    uncategorized = []

    for item in pipeline:
        if item.get("is_duplicate"):
            continue
        cat = item.get("category", "")
        if cat in by_category:
            # Sort by confidence (highest first)
            by_category[cat].append(item)
        else:
            uncategorized.append(item)

    for cat in by_category:
        by_category[cat].sort(
            key=lambda x: x.get("category_scores", {}).get(cat, 0),
            reverse=True
        )

    items_json = json.dumps(
        [item for item in pipeline if not item.get("is_duplicate") and "category" in item],
        ensure_ascii=False
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Mutti - Photo Review Gallery</title>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: #0f0f0f; color: #fff; font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; }}
h1 {{ text-align: center; margin-bottom: 10px; font-size: 2rem; }}
.stats {{ text-align: center; margin-bottom: 30px; color: #aaa; }}
.stats span {{ color: #4ade80; font-weight: bold; }}
.category-section {{ margin-bottom: 40px; }}
.category-header {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 20px; background: #1a1a1a; border-radius: 8px; margin-bottom: 16px;
    position: sticky; top: 0; z-index: 10;
}}
.category-header h2 {{ font-size: 1.3rem; }}
.category-count {{ font-size: 0.9rem; color: #aaa; }}
.category-count .approved {{ color: #4ade80; }}
.category-actions button {{
    padding: 6px 14px; border: 1px solid #333; background: transparent;
    color: #aaa; border-radius: 4px; cursor: pointer; margin-left: 8px; font-size: 0.85rem;
}}
.category-actions button:hover {{ background: #222; color: #fff; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }}
.card {{
    background: #1a1a1a; border-radius: 8px; overflow: hidden; border: 2px solid transparent;
    transition: border-color 0.2s;
}}
.card.approved {{ border-color: #4ade80; }}
.card.rejected {{ opacity: 0.3; }}
.card.low-confidence {{ border-color: #fbbf24; }}
.card img {{ width: 100%; height: 200px; object-fit: cover; cursor: pointer; }}
.card-body {{ padding: 12px; }}
.card-body .edit-field {{
    width: 100%; padding: 6px 8px; background: #2a2a2a; color: #fff; border: 1px solid #333;
    border-radius: 4px; font-size: 0.8rem; margin-bottom: 6px; outline: none;
}}
.card-body .edit-field:focus {{ border-color: #4ade80; }}
.card-body .edit-field::placeholder {{ color: #666; }}
.card-body .scores {{ font-size: 0.75rem; color: #666; margin-bottom: 8px; }}
.card-actions {{ display: flex; gap: 8px; align-items: center; }}
.card-actions button {{
    padding: 4px 12px; border: 1px solid #333; background: transparent;
    color: #aaa; border-radius: 4px; cursor: pointer; font-size: 0.8rem;
}}
.card-actions button.active {{ background: #4ade80; color: #000; border-color: #4ade80; }}
.card-actions button.reject-active {{ background: #ef4444; color: #fff; border-color: #ef4444; }}
.card-actions select {{
    padding: 4px 8px; background: #2a2a2a; color: #fff; border: 1px solid #333;
    border-radius: 4px; font-size: 0.8rem;
}}
.export-bar {{
    position: fixed; bottom: 0; left: 0; right: 0; padding: 16px 20px;
    background: #1a1a1a; border-top: 1px solid #333; display: flex;
    justify-content: space-between; align-items: center; z-index: 100;
}}
.export-bar .total {{ font-size: 0.9rem; color: #aaa; }}
.export-bar .total span {{ color: #4ade80; font-weight: bold; }}
.export-bar button {{
    padding: 10px 24px; background: #4ade80; color: #000; border: none;
    border-radius: 6px; cursor: pointer; font-weight: bold; font-size: 1rem;
}}
.export-bar button:hover {{ background: #22c55e; }}
body {{ padding-bottom: 80px; }}
.confidence-badge {{
    display: inline-block; padding: 2px 6px; border-radius: 3px;
    font-size: 0.7rem; font-weight: bold; margin-left: 8px;
}}
.confidence-badge.low {{ background: #fbbf24; color: #000; }}
.confidence-badge.high {{ background: #4ade80; color: #000; }}
</style>
</head>
<body>

<h1>Mutti - Photo Review</h1>
<div class="stats">
    Target: ~{TARGET_PER_CATEGORY} per category | <span id="total-approved">0</span> / ~100 approved
</div>

<div id="categories"></div>

<div class="export-bar">
    <div class="total">Approved: <span id="bar-approved">0</span> / ~100</div>
    <button onclick="exportDecisions()">Export Decisions</button>
</div>

<script>
const CATEGORIES = {json.dumps(CATEGORIES)};
const TARGET = {TARGET_PER_CATEGORY};
const allItems = {items_json};

// State: track approval status and overrides
const state = {{}};
allItems.forEach(item => {{
    state[item.id] = {{
        approved: false,
        category_override: null,
        alt_edit: null,
        legende_edit: null,
    }};
}});

function getCategory(item) {{
    return state[item.id]?.category_override || item.category;
}}

function renderAll() {{
    const container = document.getElementById('categories');
    container.innerHTML = '';

    CATEGORIES.forEach(cat => {{
        const items = allItems.filter(item => getCategory(item) === cat);
        const approved = items.filter(item => state[item.id]?.approved).length;

        const section = document.createElement('div');
        section.className = 'category-section';
        section.innerHTML = `
            <div class="category-header">
                <div>
                    <h2>${{cat.charAt(0).toUpperCase() + cat.slice(1)}}</h2>
                    <span class="category-count"><span class="approved">${{approved}}</span> / ${{items.length}} (target: ${{TARGET}})</span>
                </div>
                <div class="category-actions">
                    <button onclick="selectAll('${{cat}}', true)">Select All</button>
                    <button onclick="selectAll('${{cat}}', false)">Deselect All</button>
                </div>
            </div>
            <div class="grid" id="grid-${{cat}}"></div>
        `;
        container.appendChild(section);

        const grid = section.querySelector('.grid');
        items.forEach(item => {{
            const s = state[item.id];
            const topScore = Math.max(...Object.values(item.category_scores || {{}}));
            const isLow = item.low_confidence;

            const card = document.createElement('div');
            card.className = 'card' + (s.approved ? ' approved' : ' rejected') + (isLow ? ' low-confidence' : '');
            card.id = 'card-' + item.id;

            const scoresHtml = Object.entries(item.category_scores || {{}})
                .sort((a, b) => b[1] - a[1])
                .map(([c, v]) => `${{c}}: ${{v.toFixed(3)}}`)
                .join(' | ');

            const keywordsHtml = (item.keywords || []).map(k => `<span>${{k}}</span>`).join('');

            const categoryOptions = CATEGORIES.map(c =>
                `<option value="${{c}}" ${{getCategory(item) === c ? 'selected' : ''}}>${{c}}</option>`
            ).join('');

            // Use relative path from the data directory
            const imgSrc = item.local_path ? item.local_path.replace('data/', '') : '';

            card.innerHTML = `
                <img src="${{imgSrc}}" alt="${{item.alt || ''}}" loading="lazy"
                     onerror="this.src='data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 width=%22200%22 height=%22200%22><rect fill=%22%23333%22 width=%22200%22 height=%22200%22/><text fill=%22%23999%22 x=%2250%25%22 y=%2250%25%22 text-anchor=%22middle%22>No image</text></svg>'">
                <div class="card-body">
                    <input type="text" class="edit-field" placeholder="Alt text..."
                           value="${{s.alt_edit || item.alt || ''}}"
                           onchange="editField('${{item.id}}', 'alt_edit', this.value)">
                    <input type="text" class="edit-field" placeholder="Legende..."
                           value="${{s.legende_edit || item.legende || ''}}"
                           onchange="editField('${{item.id}}', 'legende_edit', this.value)">
                    <div class="scores">${{scoresHtml}}
                        ${{isLow ? '<span class="confidence-badge low">LOW</span>' : '<span class="confidence-badge high">OK</span>'}}
                    </div>
                    <div class="card-actions">
                        <button class="${{s.approved ? 'active' : ''}}" onclick="toggleApprove('${{item.id}}')">
                            ${{s.approved ? 'Approved' : 'Approve'}}
                        </button>
                        <select onchange="overrideCategory('${{item.id}}', this.value)">
                            ${{categoryOptions}}
                        </select>
                    </div>
                </div>
            `;
            grid.appendChild(card);
        }});
    }});

    updateCounts();
}}

function toggleApprove(id) {{
    state[id].approved = !state[id].approved;
    renderAll();
}}

function selectAll(category, approve) {{
    allItems.forEach(item => {{
        if (getCategory(item) === category) {{
            state[item.id].approved = approve;
        }}
    }});
    renderAll();
}}

function overrideCategory(id, newCat) {{
    state[id].category_override = newCat;
    renderAll();
}}

function editField(id, field, value) {{
    state[id][field] = value;
}}

function updateCounts() {{
    const total = Object.values(state).filter(s => s.approved).length;
    document.getElementById('total-approved').textContent = total;
    document.getElementById('bar-approved').textContent = total;
}}

function exportDecisions() {{
    const approved = [];
    const category_overrides = {{}};
    const captions = {{}};

    Object.entries(state).forEach(([id, s]) => {{
        if (s.approved) approved.push(id);
        if (s.category_override) category_overrides[id] = s.category_override;
        if (s.alt_edit || s.legende_edit) {{
            captions[id] = {{}};
            if (s.alt_edit) captions[id].alt = s.alt_edit;
            if (s.legende_edit) captions[id].legende = s.legende_edit;
        }}
    }});

    const decisions = {{ approved, category_overrides, captions }};
    const blob = new Blob([JSON.stringify(decisions, null, 2)], {{ type: 'application/json' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'review_decisions.json';
    a.click();
    URL.revokeObjectURL(url);
    alert(`Exported ${{approved.length}} approved images. Save the file to scripts/data/review_decisions.json`);
}}

renderAll();
</script>
</body>
</html>"""

    return html


def main():
    pipeline = load_pipeline()

    valid = [item for item in pipeline if not item.get("is_duplicate") and "category" in item]
    if not valid:
        print("No classified images found. Run classify.py first.")
        return

    print(f"Generating review gallery for {len(valid)} images...")

    html = generate_html(pipeline)
    with open(REVIEW_HTML, "w") as f:
        f.write(html)

    # Summary
    by_cat = {}
    for item in valid:
        cat = item.get("category", "unknown")
        by_cat[cat] = by_cat.get(cat, 0) + 1

    print("\nImages per category:")
    for cat in CATEGORIES:
        count = by_cat.get(cat, 0)
        print(f"  {cat:12s}: {count}")
    print(f"\nReview gallery: {REVIEW_HTML}")
    print("Open this file in your browser, curate, then export decisions.")


if __name__ == "__main__":
    main()
