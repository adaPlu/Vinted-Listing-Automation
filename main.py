"""Main orchestrator for AI Reseller Suite v2."""

from __future__ import annotations

import logging
from pathlib import Path

import config
from agents.inventory_agent import InventoryAgent
from agents.listing_agent import ListingAgent
from agents.pricing_agent import PricingAgent
from agents.review_lead_agent import ReviewLeadAgent
from agents.vision_agent import VisionAgent
from agents.vinted_agent import VintedAgent


def configure_logging() -> None:
    config.LOG_FOLDER.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=config.LOG_FOLDER / "ai_reseller_suite.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )


def get_listing_folders() -> list[Path]:
    if not config.IMAGE_FOLDER.exists():
        raise FileNotFoundError(
            f"Missing listing_images folder at {config.IMAGE_FOLDER}. "
            "Create one folder per item and place that item's photos inside."
        )
    return sorted(path for path in config.IMAGE_FOLDER.iterdir() if path.is_dir())


def get_images(folder: Path) -> list[str]:
    return [
        str(path.resolve())
        for path in sorted(folder.iterdir())
        if path.is_file()
        and path.suffix.lower() in config.SUPPORTED_IMAGE_EXTENSIONS
    ]


def main() -> None:
    configure_logging()

    inventory = InventoryAgent()
    listing_agent = ListingAgent()
    pricing_agent = PricingAgent()
    review_lead = ReviewLeadAgent()
    vision_agent = VisionAgent()

    folders = get_listing_folders()

    print(f"Found {len(folders)} item folders")
    logging.info("Found %s item folders", len(folders))

    with VintedAgent() as vinted:
        for folder in folders:
            print(f"\nPROCESSING: {folder.name}")
            images = get_images(folder)

            if inventory.is_duplicate_folder(folder, images):
                print(f"Skipping duplicate or already-listed folder: {folder.name}")
                inventory.record_event(folder.name, "skipped_duplicate")
                continue

            inventory.upsert_item(folder, images, status="processing")

            image_review = review_lead.review_images(images)
            image_review.print_summary()
            if not image_review.passed:
                inventory.update_status(folder.name, "image_review_failed")
                continue

            vision_metadata = vision_agent.analyze_item(folder, images)
            inventory.save_vision_metadata(folder.name, vision_metadata)

            listing = listing_agent.generate_listing(folder, vision_metadata)

            pricing_result = pricing_agent.estimate_price(listing, vision_metadata)
            listing["price"] = pricing_result["final_price"]
            listing["pricing_details"] = pricing_result

            listing_review = review_lead.review_listing(
                title=str(listing["title"]),
                description=str(listing["description"]),
                price=listing["price"],
            )
            listing_review.print_summary()
            if not listing_review.passed:
                inventory.update_status(folder.name, "listing_review_failed")
                continue

            print("\nGenerated draft data:")
            print(f"  Title: {listing['title']}")
            print(f"  Category guess: {listing['category']}")
            print(f"  Price: ${listing['price']}")
            print(f"  Tags: {', '.join(listing['tags'])}")
            print(f"  Vision source: {vision_metadata.get('source')}")
            print(f"  Pricing source: {pricing_result['source']}")

            try:
                uploaded, fields_filled = vinted.create_draft(images, listing)
                marketplace_review = review_lead.review_marketplace_submission(
                    uploaded,
                    fields_filled,
                )
                marketplace_review.print_summary()

                if not marketplace_review.passed:
                    screenshot = vinted.screenshot_failure(folder.name)
                    if screenshot:
                        print(f"Failure screenshot saved: {screenshot}")
                    inventory.update_status(folder.name, "marketplace_review_failed")
                    continue

                inventory.mark_uploaded(folder, listing, pricing_result)
                review_lead.final_human_gate()

            except SystemExit:
                raise

            except Exception as exc:
                logging.exception("Failed while processing %s", folder.name)
                print(f"ERROR processing {folder.name}: {exc}")
                screenshot = vinted.screenshot_failure(folder.name)
                if screenshot:
                    print(f"Failure screenshot saved: {screenshot}")
                inventory.update_status(folder.name, "failed", error=str(exc))
                input("Fix the browser/session if needed, then press ENTER to continue...")


if __name__ == "__main__":
    main()
