from __future__ import annotations

from collections import Counter, defaultdict
import re
from typing import Any

from backend.models.filters import ALLERGEN_COLUMN_TO_API, ALLERGEN_QUERY_TO_COLUMN, MenuFilters

AVOIDED_INGREDIENT_PATTERNS = {
    "beef": re.compile(r"\b(beef|steak|brisket|veal)\b", re.IGNORECASE),
    "pork": re.compile(r"\b(pork|bacon|ham|prosciutto|salami|pepperoni|pancetta|chorizo)\b", re.IGNORECASE),
}


def item_allergens(row: dict[str, Any]) -> list[str]:
    return [
        allergen
        for column, allergen in ALLERGEN_COLUMN_TO_API.items()
        if row.get(column) is True
    ]


def serialize_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row.get("description"),
        "calories": row.get("calories"),
        "station": row["station"],
        "vegetarian": row.get("vegetarian", False),
        "vegan": row.get("vegan", False),
        "allergens": item_allergens(row),
        "info_unavailable": row.get("info_unavailable", False),
    }


def passes_dietary_filter(row: dict[str, Any], filters: MenuFilters) -> bool:
    if filters.vegan and not row.get("vegan", False):
        return False
    if filters.vegetarian and not (row.get("vegetarian", False) or row.get("vegan", False)):
        return False
    return True


def has_excluded_allergen(row: dict[str, Any], excluded_allergens: tuple[str, ...]) -> bool:
    return any(row.get(ALLERGEN_QUERY_TO_COLUMN[allergen], False) for allergen in excluded_allergens)


def has_avoided_ingredient(row: dict[str, Any], avoided_ingredients: tuple[str, ...]) -> bool:
    searchable_text = " ".join(
        str(value)
        for value in (row.get("name"), row.get("description"), row.get("station"))
        if value
    )
    return any(AVOIDED_INGREDIENT_PATTERNS[ingredient].search(searchable_text) for ingredient in avoided_ingredients)


def apply_filters(rows: list[dict[str, Any]], filters: MenuFilters) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    matching: list[dict[str, Any]] = []
    check_with_staff: list[dict[str, Any]] = []

    for row in rows:
        if not passes_dietary_filter(row, filters):
            continue

        if filters.excluded_allergens:
            if has_excluded_allergen(row, filters.excluded_allergens):
                continue
            if row.get("info_unavailable", False):
                check_with_staff.append(row)
                continue

        if filters.avoided_ingredients and has_avoided_ingredient(row, filters.avoided_ingredients):
            continue

        matching.append(row)

    return matching, check_with_staff


def group_by_station(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["station"]].append(serialize_item(row))

    return [
        {
            "name": station,
            "matching_item_count": len(items),
            "items": items,
        }
        for station, items in sorted(grouped.items(), key=lambda item: item[0].casefold())
    ]


def build_menu_response(
    hall: dict[str, Any],
    rows: list[dict[str, Any]],
    filters: MenuFilters,
) -> dict[str, Any]:
    total_station_count = len({row["station"] for row in rows})
    matching, check_with_staff = apply_filters(rows, filters)
    stations = group_by_station(matching)
    matching_station_count = len(stations)
    station_coverage = matching_station_count / total_station_count if total_station_count else 0

    return {
        "hall": {"name": hall["name"], "slug": hall["slug"]},
        "date": filters.date,
        "meal": filters.meal,
        "summary": {
            "matching_item_count": len(matching),
            "matching_station_count": matching_station_count,
            "total_station_count": total_station_count,
            "station_coverage": round(station_coverage, 3),
        },
        "stations": stations,
        "check_with_staff": [serialize_item(row) for row in check_with_staff],
    }


def build_dining_option(hall: dict[str, Any], rows: list[dict[str, Any]], filters: MenuFilters) -> dict[str, Any]:
    menu = build_menu_response(hall, rows, filters)
    station_counts = Counter()
    for station in menu["stations"]:
        station_counts[station["name"]] = station["matching_item_count"]

    return {
        "hall": {"name": hall["name"], "slug": hall["slug"]},
        "matching_item_count": menu["summary"]["matching_item_count"],
        "matching_station_count": menu["summary"]["matching_station_count"],
        "total_station_count": menu["summary"]["total_station_count"],
        "station_coverage": menu["summary"]["station_coverage"],
        "check_with_staff_count": len(menu["check_with_staff"]),
        "top_stations": [
            {"name": station, "matching_item_count": count}
            for station, count in station_counts.most_common(3)
        ],
    }


def sort_dining_options(options: list[dict[str, Any]], sort: str) -> list[dict[str, Any]]:
    if sort == "stations":
        return sorted(options, key=lambda option: (-option["matching_station_count"], option["hall"]["name"].casefold()))
    if sort == "name":
        return sorted(options, key=lambda option: option["hall"]["name"].casefold())
    return sorted(options, key=lambda option: (-option["matching_item_count"], option["hall"]["name"].casefold()))
