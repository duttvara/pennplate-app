from __future__ import annotations

from typing import Any

import requests

from backend.config import Config


MENU_ITEM_SELECT = ",".join(
    [
        "id",
        "date",
        "meal",
        "station",
        "name",
        "description",
        "calories",
        "vegetarian",
        "vegan",
        "contains_wheat_gluten",
        "contains_milk",
        "contains_egg",
        "contains_soy",
        "contains_peanut",
        "contains_tree_nut",
        "contains_sesame",
        "info_unavailable",
    ]
)


class SupabaseReadClient:
    def __init__(self, config: Config | None = None) -> None:
        self.config = config or Config()
        self.config.require_supabase()

    @property
    def rest_url(self) -> str:
        return f"{self.config.supabase_url}/rest/v1"

    @property
    def headers(self) -> dict[str, str]:
        key = self.config.supabase_service_role_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        }

    def _get(self, table: str, params: dict[str, str]) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.rest_url}/{table}",
            params=params,
            headers=self.headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def list_halls(self) -> list[dict[str, Any]]:
        return self._get(
            "dining_halls",
            {"select": "id,name,slug", "order": "name.asc"},
        )

    def get_hall_by_slug(self, slug: str) -> dict[str, Any] | None:
        rows = self._get(
            "dining_halls",
            {"slug": f"eq.{slug}", "select": "id,name,slug"},
        )
        return rows[0] if rows else None

    def menu_items(self, dining_hall_id: str, date: str, meal: str) -> list[dict[str, Any]]:
        return self._get(
            "menu_items",
            {
                "dining_hall_id": f"eq.{dining_hall_id}",
                "date": f"eq.{date}",
                "meal": f"eq.{meal}",
                "select": MENU_ITEM_SELECT,
                "order": "station.asc,name.asc",
            },
        )
