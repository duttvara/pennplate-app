from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from typing import Any

from scraper import scraper as menu_scraper


UPSERT_CONFLICT_COLUMNS = "dining_hall_id,date,meal,station,normalized_name"


def normalize_item_name(name: str) -> str:
    return re.sub(r"\s+", " ", name).strip().casefold()


def menu_item_to_row(item: menu_scraper.MenuItem, dining_hall_id: str) -> dict[str, Any]:
    source_item_ids = item.duplicate_source_item_ids or [item.source_item_id]
    source_item_ids = [source_id for source_id in source_item_ids if source_id]

    return {
        "dining_hall_id": dining_hall_id,
        "date": item.date,
        "meal": item.meal,
        "station": item.station,
        "name": item.name,
        "normalized_name": normalize_item_name(item.name),
        "description": item.description,
        "calories": item.calories,
        "vegetarian": item.vegetarian,
        "vegan": item.vegan,
        "contains_wheat_gluten": item.contains_wheat_gluten,
        "contains_milk": item.contains_milk,
        "contains_egg": item.contains_egg,
        "contains_soy": item.contains_soy,
        "contains_peanut": item.contains_peanut,
        "contains_tree_nut": item.contains_tree_nut,
        "contains_sesame": item.contains_sesame,
        "info_unavailable": item.info_unavailable,
        "source_item_ids": source_item_ids,
        "metadata_conflicts": item.metadata_conflicts,
        "scraped_at": datetime.now(timezone.utc).isoformat(),
    }


def upsert_key_for_row(row: dict[str, Any]) -> tuple[Any, ...]:
    return tuple(row[column] for column in UPSERT_CONFLICT_COLUMNS.split(","))


class SupabaseConfigError(RuntimeError):
    pass


class SupabaseClient:
    def __init__(self, url: str | None = None, service_role_key: str | None = None) -> None:
        self.url = (url or os.environ.get("SUPABASE_URL") or "").rstrip("/")
        self.service_role_key = service_role_key or os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or ""
        if not self.url or not self.service_role_key:
            raise SupabaseConfigError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required")

    @property
    def rest_url(self) -> str:
        return f"{self.url}/rest/v1"

    @property
    def headers(self) -> dict[str, str]:
        return {
            "apikey": self.service_role_key,
            "Authorization": f"Bearer {self.service_role_key}",
            "Content-Type": "application/json",
        }

    def get_dining_hall_id(self, slug: str) -> str:
        import requests

        response = requests.get(
            f"{self.rest_url}/dining_halls",
            params={"slug": f"eq.{slug}", "select": "id"},
            headers=self.headers,
            timeout=20,
        )
        response.raise_for_status()
        rows = response.json()
        if not rows:
            raise LookupError(f"No dining hall found for slug: {slug}")
        return rows[0]["id"]

    def upsert_dining_hall(self, dining_hall: menu_scraper.DiningHall) -> str:
        import requests

        payload = {
            "name": dining_hall.name,
            "slug": dining_hall.id,
            "source_url": dining_hall.source_url,
        }
        response = requests.post(
            f"{self.rest_url}/dining_halls",
            params={"on_conflict": "slug"},
            headers={
                **self.headers,
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()[0]["id"]

    def upsert_menu_items(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        if not rows:
            return []

        import requests

        response = requests.post(
            f"{self.rest_url}/menu_items",
            params={"on_conflict": UPSERT_CONFLICT_COLUMNS},
            headers={
                **self.headers,
                "Prefer": "resolution=merge-duplicates,return=representation",
            },
            json=rows,
            timeout=60,
        )
        response.raise_for_status()
        return response.json()

    def create_scrape_run(self, dining_hall_id: str, meal: str | None) -> str:
        import requests

        payload = {
            "dining_hall_id": dining_hall_id,
            "meal": meal.title() if meal else None,
            "status": "running",
        }
        response = requests.post(
            f"{self.rest_url}/scrape_runs",
            headers={**self.headers, "Prefer": "return=representation"},
            json=payload,
            timeout=20,
        )
        response.raise_for_status()
        return response.json()[0]["id"]

    def complete_scrape_run(
        self,
        run_id: str,
        *,
        status: str,
        menu_date: str | None,
        raw_item_count: int,
        final_item_count: int,
        duplicate_count: int,
        metadata_conflict_count: int,
        error_message: str | None = None,
    ) -> None:
        import requests

        payload = {
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "status": status,
            "date": menu_date,
            "raw_item_count": raw_item_count,
            "final_item_count": final_item_count,
            "duplicate_count": duplicate_count,
            "metadata_conflict_count": metadata_conflict_count,
            "error_message": error_message,
        }
        response = requests.patch(
            f"{self.rest_url}/scrape_runs",
            params={"id": f"eq.{run_id}"},
            headers=self.headers,
            json=payload,
            timeout=20,
        )
        response.raise_for_status()


def rows_from_items(items: list[menu_scraper.MenuItem], dining_hall_id: str) -> list[dict[str, Any]]:
    return [menu_item_to_row(item, dining_hall_id) for item in items]


def count_metadata_conflicts(items: list[menu_scraper.MenuItem]) -> int:
    return sum(len(item.metadata_conflicts) for item in items)
