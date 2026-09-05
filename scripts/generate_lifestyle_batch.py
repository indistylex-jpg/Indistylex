#!/usr/bin/env python3
"""Build lifestyle (humanpic) generation manifest for Party bear product photos.

Reads processed background images and writes manifest.json with prompts for
Indian boy/girl model shots matching Indistylex lifestyle style.

Usage:
  .imgvenv/bin/python scripts/generate_lifestyle_batch.py
  .imgvenv/bin/python scripts/generate_lifestyle_batch.py --list-pending
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "Party bear and festival-20260822T073058Z-1-001"
SOURCE = BASE / "Party bear and festival"
OUT_BG = BASE / "background"
OUT_HUMAN = BASE / "humanpic"
MANIFEST = OUT_HUMAN / "manifest.json"

# Keywords suggesting girls' wear (flat-lay classification heuristic)
GIRL_KEYWORDS = re.compile(
    r"\b(dress|frock|skirt|gown|lehenga|ghagra|anarkali|marie|"
    r"party\s*wear\s*girl|girls?|princess|tiara|bow|ribbon)\b",
    re.I,
)
BOY_KEYWORDS = re.compile(
    r"\b(shirt|kurta|pant|trouser|cargo|jacket|blazer|suit|"
    r"boys?|camp|style|polo|t[\s-]?shirt)\b",
    re.I,
)

LIFESTYLE_STYLE = (
    "Professional e-commerce lifestyle photo for Indistylex kids fashion website. "
    "Full body shot, natural confident smile, soft natural daylight, shallow depth of field, "
    "clean blurred outdoor park or soft studio backdrop in light blue and white tones matching "
    "Indistylex brand (#EFF6FF palette). High quality commercial photography, no text overlays."
)


def guess_gender(stem: str) -> str:
    """Return 'girl' or 'boy' using filename hints; default boy for ambiguous."""
    name = stem.replace("_", " ").replace("-", " ")
    if GIRL_KEYWORDS.search(name):
        return "girl"
    if BOY_KEYWORDS.search(name):
        return "boy"
    return "boy"


def build_prompt(gender: str) -> str:
    age = "6-8 years old" if gender == "girl" else "8-10 years old"
    model = f"Indian {gender}, {age}"
    outfit = (
        "wearing the exact outfit shown in the reference product photo — same colors, "
        "print, pattern, and design details"
    )
    if gender == "girl":
        pose = "standing gracefully, slight smile, optional floral headband, neat Mary Jane shoes"
    else:
        pose = "standing casually with hands in pockets or at sides, white sneakers, confident smile"
    return f"{LIFESTYLE_STYLE} {model} {outfit}, {pose}."


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-pending", action="store_true", help="Print pending filenames")
    args = parser.parse_args()

    OUT_HUMAN.mkdir(parents=True, exist_ok=True)

    bg_files = sorted(
        p for p in OUT_BG.iterdir()
        if p.suffix.lower() in {".jpg", ".jpeg", ".png"}
    ) if OUT_BG.exists() else []

    if not bg_files and SOURCE.exists():
        bg_files = sorted(
            p for p in SOURCE.iterdir()
            if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}
        )

    entries = []
    pending = []
    for path in bg_files:
        out_name = path.stem + ".jpg"
        human_path = OUT_HUMAN / out_name
        gender = guess_gender(path.stem)
        entry = {
            "source": str(path.relative_to(ROOT)),
            "output": str((OUT_HUMAN / out_name).relative_to(ROOT)),
            "gender": gender,
            "prompt": build_prompt(gender),
            "done": human_path.exists() and human_path.stat().st_size > 50_000,
        }
        entries.append(entry)
        if not entry["done"]:
            pending.append(out_name)

    manifest = {
        "total": len(entries),
        "done": sum(1 for e in entries if e["done"]),
        "pending": len(pending),
        "entries": entries,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest: {MANIFEST} ({manifest['done']}/{manifest['total']} done)")

    if args.list_pending:
        for name in pending:
            print(name)


if __name__ == "__main__":
    main()
