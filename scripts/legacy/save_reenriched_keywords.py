#!/usr/bin/env python3
"""
Save re-enriched keywords for modules.
Used by /reenrich-keywords slash command.

Updates keywords and marks modules with enrichment_version v2.0.
Also updates checkpoint to track progress.
"""

import argparse
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule

ENRICHMENT_VERSION = "v2.0"
CHECKPOINT_FILE = os.path.join(os.path.dirname(__file__), ".reenrich_checkpoint.json")


def load_checkpoint() -> dict:
    """Load checkpoint from file."""
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"processed_ids": [], "started_at": None}


def save_checkpoint(checkpoint: dict):
    """Save checkpoint to file."""
    checkpoint["updated_at"] = datetime.now().isoformat()
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(checkpoint, f, indent=2)


def save_keywords_batch(keywords_data: list):
    """
    Save re-enriched keywords for multiple modules.
    Updates ALL versions of each module with new keywords.

    Args:
        keywords_data: List of dicts with id and keywords
    """
    db = SessionLocal()
    checkpoint = load_checkpoint()
    if not checkpoint.get("started_at"):
        checkpoint["started_at"] = datetime.now().isoformat()

    processed_ids = set(checkpoint.get("processed_ids", []))
    success_count = 0
    error_count = 0
    versions_updated = 0

    try:
        for item in keywords_data:
            module_id = item.get("id")
            new_keywords = item.get("keywords", [])

            if not module_id:
                print(f"❌ Missing module ID in item")
                error_count += 1
                continue

            if not new_keywords or len(new_keywords) < 3:
                print(f"❌ Module {module_id}: Not enough keywords ({len(new_keywords)})")
                error_count += 1
                continue

            # Get the module to find its technical_name
            module = db.query(OdooModule).filter(OdooModule.id == module_id).first()

            if not module:
                print(f"❌ Module ID {module_id} not found")
                error_count += 1
                continue

            technical_name = module.technical_name

            # Update ALL versions of this module
            all_versions = db.query(OdooModule).filter(
                OdooModule.technical_name == technical_name
            ).all()

            for mod in all_versions:
                mod.keywords = new_keywords
                mod.enrichment_version = ENRICHMENT_VERSION
                versions_updated += 1

            # Track processed
            processed_ids.add(module_id)
            success_count += 1
            print(f"✅ {technical_name}: {len(new_keywords)} keywords ({len(all_versions)} versions)")

        db.commit()

        # Update checkpoint
        checkpoint["processed_ids"] = list(processed_ids)
        checkpoint["last_success_count"] = success_count
        save_checkpoint(checkpoint)

        print(f"\n📊 SUMMARY")
        print(f"   Modules processed: {success_count}")
        print(f"   Versions updated:  {versions_updated}")
        print(f"   Errors:            {error_count}")
        print(f"   Total processed:   {len(processed_ids)}")

        return success_count, error_count

    except Exception as e:
        print(f"❌ Batch error: {e}")
        db.rollback()
        return 0, len(keywords_data)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Save re-enriched keywords")
    parser.add_argument("--json", type=str, required=True,
                       help="JSON string or file path with keywords data")

    args = parser.parse_args()

    try:
        # Check if it's a file path
        if os.path.isfile(args.json):
            with open(args.json, 'r') as f:
                keywords_data = json.load(f)
        else:
            keywords_data = json.loads(args.json)

        if isinstance(keywords_data, dict):
            keywords_data = [keywords_data]

        print(f"\n📦 Processing {len(keywords_data)} modules...\n")
        save_keywords_batch(keywords_data)

    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()