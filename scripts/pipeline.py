"""
Orchestrator: run pipeline steps sequentially.

Usage:
  python pipeline.py                  # Run collect → review (stops for manual curation)
  python pipeline.py --post-review    # Run upload → export (after manual curation)
  python pipeline.py --step classify  # Run a single step
  python pipeline.py --from classify  # Run from a specific step onwards
  python pipeline.py --all            # Run everything (assumes review_decisions.json exists)
"""

import subprocess
import sys
import argparse
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent

STEPS_PRE_REVIEW = [
    ("collect", "Collecting images from web sources"),
    ("deduplicate", "Removing near-duplicate images"),
    ("classify", "Classifying images with CLIP"),
    ("review", "Generating review gallery"),
]

STEPS_POST_REVIEW = [
    ("upload", "Uploading to Supabase Storage"),
    ("export", "Exporting items.js"),
]

ALL_STEPS = STEPS_PRE_REVIEW + STEPS_POST_REVIEW


def run_step(name, description):
    """Run a single pipeline step."""
    script = SCRIPTS_DIR / f"{name}.py"
    if not script.exists():
        print(f"  Error: {script} not found!")
        return False

    print(f"\n{'='*60}")
    print(f"  Step: {name} - {description}")
    print(f"{'='*60}\n")

    result = subprocess.run(
        [sys.executable, str(script)],
        cwd=str(SCRIPTS_DIR),
    )

    if result.returncode != 0:
        print(f"\n  Step '{name}' failed with exit code {result.returncode}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Mutti photo pipeline orchestrator")
    parser.add_argument("--step", type=str, help="Run a single step")
    parser.add_argument("--from-step", type=str, help="Run from a specific step onwards")
    parser.add_argument("--post-review", action="store_true", help="Run post-review steps (upload + export)")
    parser.add_argument("--all", action="store_true", help="Run all steps")
    args = parser.parse_args()

    if args.step:
        step_names = {name: desc for name, desc in ALL_STEPS}
        if args.step not in step_names:
            print(f"Unknown step: {args.step}")
            print(f"Available: {', '.join(step_names.keys())}")
            sys.exit(1)
        success = run_step(args.step, step_names[args.step])
        sys.exit(0 if success else 1)

    if args.from_step:
        step_names = [name for name, _ in ALL_STEPS]
        if args.from_step not in step_names:
            print(f"Unknown step: {args.from_step}")
            sys.exit(1)
        start_idx = step_names.index(args.from_step)
        steps = ALL_STEPS[start_idx:]
    elif args.post_review:
        steps = STEPS_POST_REVIEW
    elif args.all:
        steps = ALL_STEPS
    else:
        steps = STEPS_PRE_REVIEW

    print("Mutti Photo Pipeline")
    print(f"Running {len(steps)} steps: {', '.join(name for name, _ in steps)}")

    for name, description in steps:
        success = run_step(name, description)
        if not success:
            print(f"\nPipeline stopped at step '{name}'.")
            sys.exit(1)

        # After review step, pause for manual curation
        if name == "review" and not args.all:
            print("\n" + "="*60)
            print("  MANUAL CURATION REQUIRED")
            print("="*60)
            print()
            print("  1. Open scripts/data/review.html in your browser")
            print("  2. Approve/reject images, override categories as needed")
            print("  3. Click 'Export Decisions' and save to scripts/data/review_decisions.json")
            print("  4. Then run: python scripts/pipeline.py --post-review")
            print()
            break

    if steps == STEPS_POST_REVIEW or args.all:
        print("\n" + "="*60)
        print("  PIPELINE COMPLETE")
        print("="*60)
        print()
        print("  Run 'pnpm dev' to see the updated site!")


if __name__ == "__main__":
    main()
