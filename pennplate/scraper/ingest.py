from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scraper.database import (
    SupabaseClient,
    SupabaseConfigError,
    count_metadata_conflicts,
    rows_from_items,
)
from scraper.scraper import DINING_HALLS, HILL_HOUSE, DiningHall, MenuItem, MenuScraper


LOGGER = logging.getLogger("pennplate.ingest")


def load_items(
    dining_hall: DiningHall,
    html_path: str | None,
    meal: str | None,
    menu_date: str | None = None,
) -> tuple[list[MenuItem], list[MenuItem]]:
    scraper = MenuScraper(dining_hall)
    html = open(html_path, encoding="utf-8").read() if html_path else scraper.fetch_html(menu_date=menu_date)
    raw_items = scraper.parse_raw(html, menu_date=menu_date)
    if meal:
        raw_items = [item for item in raw_items if item.meal.lower() == meal]
    items = scraper._deduplicate_items(raw_items)
    return raw_items, items


def ingest_dining_hall(
    dining_hall: DiningHall,
    html_path: str | None = None,
    meal: str | None = None,
    menu_date: str | None = None,
    dry_run: bool = False,
) -> int:
    raw_items, items = load_items(dining_hall, html_path, meal, menu_date=menu_date)
    if not items:
        raise RuntimeError("No menu items parsed for ingestion")

    duplicate_sources = sum(max(len(item.duplicate_source_item_ids) - 1, 0) for item in items)
    conflict_count = count_metadata_conflicts(items)
    menu_date = items[0].date

    if dry_run:
        LOGGER.info(
            "Dry run parsed %s final items for %s %s; duplicate sources=%s conflicts=%s",
            len(items),
            dining_hall.name,
            meal or "all meals",
            duplicate_sources,
            conflict_count,
        )
        return len(items)

    client = SupabaseClient()
    dining_hall_id = client.upsert_dining_hall(dining_hall)
    run_id = client.create_scrape_run(dining_hall_id, meal)
    rows = rows_from_items(items, dining_hall_id)

    try:
        inserted = client.upsert_menu_items(rows)
        client.complete_scrape_run(
            run_id,
            status="completed",
            menu_date=menu_date,
            raw_item_count=len(raw_items),
            final_item_count=len(items),
            duplicate_count=duplicate_sources,
            metadata_conflict_count=conflict_count,
        )
    except Exception as exc:
        client.complete_scrape_run(
            run_id,
            status="failed",
            menu_date=menu_date,
            raw_item_count=len(raw_items),
            final_item_count=len(items),
            duplicate_count=duplicate_sources,
            metadata_conflict_count=conflict_count,
            error_message=str(exc),
        )
        raise

    LOGGER.info("Upserted %s rows into Supabase", len(inserted))
    return len(inserted)


def ingest_hill_house(
    html_path: str | None = None,
    meal: str | None = None,
    menu_date: str | None = None,
    dry_run: bool = False,
) -> int:
    return ingest_dining_hall(HILL_HOUSE, html_path=html_path, meal=meal, menu_date=menu_date, dry_run=dry_run)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest PennPlate scraper output into Supabase.")
    parser.add_argument("--hall", choices=sorted(DINING_HALLS), default=HILL_HOUSE.id)
    parser.add_argument("--html", help="Parse a saved cafe HTML file instead of requesting the site.")
    parser.add_argument("--date", help="Fetch and store a specific menu date, YYYY-MM-DD.")
    parser.add_argument("--meal", choices=["breakfast", "lunch", "dinner"], help="Only ingest one meal.")
    parser.add_argument(
        "--skip-unavailable",
        action="store_true",
        help="Skip a hall when Bon Appetit publishes no menu payload for the date.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and summarize without contacting Supabase.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    try:
        count = ingest_dining_hall(
            DINING_HALLS[args.hall],
            html_path=args.html,
            meal=args.meal,
            menu_date=args.date,
            dry_run=args.dry_run,
        )
    except ValueError as exc:
        if args.skip_unavailable and str(exc) == "Could not find Bamco.menu_items JSON in page HTML":
            LOGGER.warning("No published menu payload for %s on %s; skipping", args.hall, args.date or "today")
            print(f"No menu published for {args.hall}; skipped.")
            return
        raise
    except SupabaseConfigError as exc:
        raise SystemExit(f"{exc}. Copy .env.example to .env and export the values before ingestion.") from exc

    print(f"Ingestion prepared {count} item rows.")


if __name__ == "__main__":
    main()
