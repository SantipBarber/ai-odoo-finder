#!/usr/bin/env python3
"""
Save enrichment data for modules.
Used by /enrich slash command.
"""

import argparse
import json
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.database import SessionLocal
from backend.app.models import OdooModule

ENRICHMENT_VERSION = "v1.0"


def save_single_enrichment(
    module_id: int,
    ai_description: str,
    functional_tags: list,
    keywords: list
):
    """
    Save enrichment data for a module AND propagate to all versions.

    Args:
        module_id: Database ID of the module
        ai_description: AI-generated description
        functional_tags: List of functional category tags
        keywords: List of search keywords
    """
    db = SessionLocal()

    try:
        module = db.query(OdooModule).filter(OdooModule.id == module_id).first()

        if not module:
            print(f"❌ Module with ID {module_id} not found")
            return False

        technical_name = module.technical_name

        # Find ALL versions of this module
        all_versions = db.query(OdooModule).filter(
            OdooModule.technical_name == technical_name
        ).all()

        # Update ALL versions with the same enrichment
        updated_count = 0
        for mod in all_versions:
            mod.ai_description = ai_description
            mod.functional_tags = functional_tags
            mod.keywords = keywords
            mod.enriched_at = datetime.now(datetime.UTC) if hasattr(datetime, 'UTC') else datetime.utcnow()
            mod.enrichment_version = ENRICHMENT_VERSION
            updated_count += 1

        db.commit()

        print(f"✅ Enriched: {technical_name} ({updated_count} versions)")
        return True

    except Exception as e:
        print(f"❌ Error saving enrichment for module {module_id}: {e}")
        db.rollback()
        return False

    finally:
        db.close()


def save_batch_enrichment(modules_data: list):
    """
    Save enrichment data for multiple modules.

    Args:
        modules_data: List of dicts with id, ai_description, functional_tags, keywords
    """
    db = SessionLocal()
    success_count = 0
    error_count = 0

    try:
        for module_data in modules_data:
            module_id = module_data.get("id")
            module = db.query(OdooModule).filter(OdooModule.id == module_id).first()

            if not module:
                print(f"❌ Module ID {module_id} not found")
                error_count += 1
                continue

            try:
                module.ai_description = module_data.get("ai_description")
                module.functional_tags = module_data.get("functional_tags", [])
                module.keywords = module_data.get("keywords", [])
                module.enriched_at = datetime.utcnow()
                module.enrichment_version = ENRICHMENT_VERSION

                success_count += 1
                print(f"✅ {module.technical_name} (v{module.version})")

            except Exception as e:
                print(f"❌ Error with {module_id}: {e}")
                error_count += 1

        db.commit()

        print(f"\n📊 SUMMARY: {success_count} success, {error_count} errors")
        return success_count, error_count

    except Exception as e:
        print(f"❌ Batch error: {e}")
        db.rollback()
        return 0, len(modules_data)

    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Save module enrichment data")

    # Single module mode
    parser.add_argument("--id", type=int, help="Module ID to enrich")
    parser.add_argument("--description", type=str, help="AI description")
    parser.add_argument("--tags", type=str, help="Comma-separated tags")
    parser.add_argument("--keywords", type=str, help="Comma-separated keywords")

    # Batch mode
    parser.add_argument("--json", type=str, help="JSON string or file path with batch data")

    args = parser.parse_args()

    if args.json:
        # Batch mode
        try:
            # Check if it's a file path
            if os.path.isfile(args.json):
                with open(args.json, 'r') as f:
                    modules_data = json.load(f)
            else:
                modules_data = json.loads(args.json)

            if isinstance(modules_data, dict):
                modules_data = [modules_data]

            print(f"\n📦 Processing {len(modules_data)} modules...\n")
            save_batch_enrichment(modules_data)

        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            sys.exit(1)

    elif args.id and args.description:
        # Single module mode
        tags = args.tags.split(",") if args.tags else []
        keywords = args.keywords.split(",") if args.keywords else []

        # Clean up whitespace
        tags = [t.strip() for t in tags if t.strip()]
        keywords = [k.strip() for k in keywords if k.strip()]

        save_single_enrichment(
            module_id=args.id,
            ai_description=args.description,
            functional_tags=tags,
            keywords=keywords
        )

    else:
        print("Usage:")
        print("  Single: --id 123 --description 'desc' --tags 'sales,accounting' --keywords 'invoice,billing'")
        print("  Batch:  --json '[{\"id\": 123, \"ai_description\": \"...\", ...}]'")
        print("  Batch from file: --json enrichment_batch.json")
        sys.exit(1)


if __name__ == "__main__":
    main()
