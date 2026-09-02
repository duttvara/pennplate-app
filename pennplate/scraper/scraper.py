from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import date
from html import unescape
from typing import Any

from bs4 import BeautifulSoup


LOGGER = logging.getLogger("pennplate.scraper")

SUPPORTED_ALLERGENS = {
    "Wheat/Gluten": "wheat_gluten",
    "Milk": "milk",
    "Egg": "egg",
    "Soy": "soy",
    "Peanut": "peanut",
    "Tree Nut": "tree_nut",
    "Tree Nuts": "tree_nut",
    "Sesame": "sesame",
}


@dataclass(frozen=True)
class DiningHall:
    id: str
    name: str
    source_url: str

    def url_for_date(self, menu_date: str | None = None) -> str:
        if not menu_date:
            return self.source_url
        return f"{self.source_url.rstrip('/')}/{menu_date}/"


@dataclass
class MenuItem:
    dining_hall: str
    date: str
    meal: str
    station: str
    name: str
    description: str | None
    calories: int | None
    vegetarian: bool
    vegan: bool
    allergens: list[str]
    contains_wheat_gluten: bool
    contains_milk: bool
    contains_egg: bool
    contains_soy: bool
    contains_peanut: bool
    contains_tree_nut: bool
    contains_sesame: bool
    info_unavailable: bool
    source_item_id: str
    duplicate_source_item_ids: list[str] = field(default_factory=list)
    metadata_conflicts: list[dict[str, Any]] = field(default_factory=list)


class MenuScraper:
    def __init__(self, dining_hall: DiningHall, timeout_seconds: int = 20) -> None:
        self.dining_hall = dining_hall
        self.timeout_seconds = timeout_seconds

    def fetch_html(self, menu_date: str | None = None) -> str:
        import requests

        response = requests.get(
            self.dining_hall.url_for_date(menu_date),
            timeout=self.timeout_seconds,
            headers={"User-Agent": "PennPlate/0.1 (+student project scraper)"},
        )
        response.raise_for_status()
        return response.text

    def parse(self, html: str, menu_date: str | None = None) -> list[MenuItem]:
        return self._deduplicate_items(self.parse_raw(html, menu_date=menu_date))

    def parse_raw(self, html: str, menu_date: str | None = None) -> list[MenuItem]:
        item_metadata = self._extract_menu_items_json(html)
        parsed_date = menu_date or self._extract_menu_date(BeautifulSoup(html, "html.parser"))
        raw_items: list[MenuItem] = []

        for meal, panel_html in self._daypart_sections(html):
            panel = BeautifulSoup(panel_html, "html.parser")
            menu_scope = self._canonical_daypart_scope(panel)

            station = "Unlabeled Station"
            for node in menu_scope.select('.site-panel__daypart-station-title, div[data-js="site-panel__daypart-item"]'):
                node_classes = node.get("class", [])
                if "site-panel__daypart-station-title" in node_classes:
                    station = self._normalize_text(node.get_text(" ", strip=True)) or "Unlabeled Station"
                    continue

                source_item_id = node.get("data-id", "").strip()
                try:
                    item = self._build_menu_item(
                        item_node=node,
                        item_metadata=item_metadata.get(source_item_id, {}),
                        menu_date=parsed_date,
                        meal=meal,
                        station=station,
                        source_item_id=source_item_id,
                    )
                except Exception as exc:  # Defensive parsing keeps one malformed card from ending the scrape.
                    LOGGER.warning("Skipping malformed item %s: %s", source_item_id or "<missing id>", exc)
                    continue

                raw_items.append(item)

        return raw_items

    def _canonical_daypart_scope(self, panel: BeautifulSoup) -> Any:
        active_tab = panel.select_one(".site-panel__daypart-tab-content.c-tab__content--active")
        if active_tab is not None:
            return active_tab
        return panel

    def scrape(self, menu_date: str | None = None) -> list[MenuItem]:
        return self.parse(self.fetch_html(menu_date=menu_date), menu_date=menu_date)

    def _build_menu_item(
        self,
        item_node: Any,
        item_metadata: dict[str, Any],
        menu_date: str,
        meal: str,
        station: str,
        source_item_id: str,
    ) -> MenuItem:
        title_node = item_node.select_one('[data-js="site-panel__daypart-item-title"]')
        if not title_node:
            raise ValueError("missing title node")

        name = self._normalize_text(next(title_node.stripped_strings, ""))
        if not name:
            name = self._normalize_text(item_metadata.get("label", ""))
        if not name:
            raise ValueError("missing item name")

        description = self._normalize_text(item_metadata.get("description", ""))
        if not description:
            description_node = item_node.select_one(".site-panel__daypart-item-description")
            if description_node:
                for unwanted in description_node.select(".site-panel__daypart-item-sides"):
                    unwanted.decompose()
                description = self._normalize_text(description_node.get_text(" ", strip=True))
        description = description or None

        calories = self._parse_calories(item_metadata)
        labels = self._metadata_labels(item_metadata) or self._dom_icon_labels(item_node)
        allergens = sorted(
            {
                slug
                for label, slug in SUPPORTED_ALLERGENS.items()
                if label in labels
            }
        )

        return MenuItem(
            dining_hall=self.dining_hall.name,
            date=menu_date,
            meal=meal.title(),
            station=station,
            name=name,
            description=description,
            calories=calories,
            vegetarian="Vegetarian" in labels,
            vegan="Vegan" in labels,
            allergens=allergens,
            contains_wheat_gluten="wheat_gluten" in allergens,
            contains_milk="milk" in allergens,
            contains_egg="egg" in allergens,
            contains_soy="soy" in allergens,
            contains_peanut="peanut" in allergens,
            contains_tree_nut="tree_nut" in allergens,
            contains_sesame="sesame" in allergens,
            info_unavailable="Information Unavailable" in labels,
            source_item_id=source_item_id,
        )

    def _extract_menu_items_json(self, html: str) -> dict[str, Any]:
        match = re.search(r"Bamco\.menu_items\s*=\s*(\{.*?\});\s*Bamco\.cor_icons", html, re.S)
        if not match:
            raise ValueError("Could not find Bamco.menu_items JSON in page HTML")
        return json.loads(match.group(1))

    def _deduplicate_items(self, items: list[MenuItem]) -> list[MenuItem]:
        deduped: dict[tuple[str, str, str, str, str], MenuItem] = {}

        for item in items:
            key = (
                self.dining_hall.id,
                item.date,
                item.meal.casefold(),
                item.station.casefold(),
                item.name.casefold(),
            )
            existing = deduped.get(key)
            if existing is None:
                existing = item
                existing.duplicate_source_item_ids = [item.source_item_id] if item.source_item_id else []
                deduped[key] = existing
                continue

            self._merge_duplicate(existing, item)

        return list(deduped.values())

    def _merge_duplicate(self, existing: MenuItem, duplicate: MenuItem) -> None:
        if duplicate.source_item_id and duplicate.source_item_id not in existing.duplicate_source_item_ids:
            existing.duplicate_source_item_ids.append(duplicate.source_item_id)

        conflict_fields: dict[str, dict[str, Any]] = {}

        for field_name in ("description", "calories"):
            current = getattr(existing, field_name)
            incoming = getattr(duplicate, field_name)
            if current in (None, "") and incoming not in (None, ""):
                setattr(existing, field_name, incoming)
            elif incoming not in (None, "") and current != incoming:
                conflict_fields[field_name] = {"kept": current, "duplicate": incoming}

        for field_name in ("vegetarian", "vegan", "info_unavailable"):
            current = getattr(existing, field_name)
            incoming = getattr(duplicate, field_name)
            if current != incoming:
                resolved = current or incoming
                conflict_fields[field_name] = {
                    "kept": current,
                    "duplicate": incoming,
                    "resolved": resolved,
                }
                setattr(existing, field_name, resolved)

        merged_allergens = sorted(set(existing.allergens) | set(duplicate.allergens))
        if merged_allergens != existing.allergens:
            if existing.allergens and duplicate.allergens and set(existing.allergens) != set(duplicate.allergens):
                conflict_fields["allergens"] = {"kept": existing.allergens, "duplicate": duplicate.allergens}
            existing.allergens = merged_allergens

        existing.contains_wheat_gluten = "wheat_gluten" in existing.allergens
        existing.contains_milk = "milk" in existing.allergens
        existing.contains_egg = "egg" in existing.allergens
        existing.contains_soy = "soy" in existing.allergens
        existing.contains_peanut = "peanut" in existing.allergens
        existing.contains_tree_nut = "tree_nut" in existing.allergens
        existing.contains_sesame = "sesame" in existing.allergens

        if conflict_fields:
            conflict = {
                "source_item_id": duplicate.source_item_id,
                "fields": conflict_fields,
            }
            existing.metadata_conflicts.append(conflict)
            LOGGER.warning(
                "Conflicting duplicate metadata for %s / %s / %s: %s",
                existing.meal,
                existing.station,
                existing.name,
                conflict_fields,
            )

    def _daypart_sections(self, html: str) -> list[tuple[str, str]]:
        panel_starts = list(re.finditer(r"<section\b[^>]*\bdata-js=\"panel\"[^>]*>", html, re.S))
        sections: list[tuple[str, str]] = []

        for index, match in enumerate(panel_starts):
            opening_tag = match.group(0)
            if 'data-type="daypart"' not in opening_tag:
                continue

            meal_match = re.search(r'data-jump-nav-title="([^"]+)"', opening_tag)
            meal = self._normalize_text(meal_match.group(1) if meal_match else "")
            if not meal:
                LOGGER.warning("Skipping daypart panel with no meal title")
                continue

            next_start = panel_starts[index + 1].start() if index + 1 < len(panel_starts) else len(html)
            sections.append((meal, html[match.start() : next_start]))

        return sections

    def _extract_menu_date(self, soup: BeautifulSoup) -> str:
        active_day = soup.select_one(".site-panel__cafenav-itemlink--active")
        if active_day:
            match = re.search(r"/(\d{4}-\d{2}-\d{2})/?$", active_day.get("href", ""))
            if match:
                return match.group(1)

        canonical = soup.find("link", rel="canonical")
        if canonical:
            match = re.search(r"/(\d{4}-\d{2}-\d{2})/?$", canonical.get("href", ""))
            if match:
                return match.group(1)

        return date.today().isoformat()

    def _metadata_labels(self, item_metadata: dict[str, Any]) -> set[str]:
        labels: set[str] = set()
        ordered_icons = item_metadata.get("ordered_cor_icon", {})
        if isinstance(ordered_icons, list):
            ordered_icons = {}
        for icon in ordered_icons.values():
            label = self._normalize_text(icon.get("label", ""))
            if label:
                labels.add(label)
        cor_icons = item_metadata.get("cor_icon", {})
        if isinstance(cor_icons, list):
            cor_icons = {}
        for label in cor_icons.values():
            normalized = self._normalize_text(str(label))
            if normalized:
                labels.add(normalized)
        return labels

    def _dom_icon_labels(self, item_node: Any) -> set[str]:
        labels: set[str] = set()
        for icon in item_node.select(".site-panel__daypart-item-cor-icons img"):
            label = self._normalize_text(icon.get("alt", "").split(":", 1)[0])
            if label:
                labels.add(label)
        return labels

    def _parse_calories(self, item_metadata: dict[str, Any]) -> int | None:
        kcal = item_metadata.get("nutrition", {}).get("kcal")
        if kcal in (None, ""):
            return None
        match = re.search(r"\d+", str(kcal))
        return int(match.group(0)) if match else None

    def _normalize_text(self, value: str) -> str:
        return re.sub(r"\s+", " ", unescape(value)).strip()


HILL_HOUSE = DiningHall(
    id="hill-house",
    name="Hill House",
    source_url="https://university-of-pennsylvania.cafebonappetit.com/cafe/hill-house/",
)

COMMONS_1920 = DiningHall(
    id="1920-commons",
    name="1920 Commons",
    source_url="https://university-of-pennsylvania.cafebonappetit.com/cafe/1920-commons/",
)

ENGLISH_HOUSE = DiningHall(
    id="english-house",
    name="English House",
    source_url="https://university-of-pennsylvania.cafebonappetit.com/cafe/kings-court-english-house/",
)

DINING_HALLS = {
    HILL_HOUSE.id: HILL_HOUSE,
    COMMONS_1920.id: COMMONS_1920,
    ENGLISH_HOUSE.id: ENGLISH_HOUSE,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Penn Dining menu data.")
    parser.add_argument("--hall", choices=sorted(DINING_HALLS), default=HILL_HOUSE.id)
    parser.add_argument("--html", help="Parse a saved Hill House HTML file instead of requesting the site.")
    parser.add_argument("--date", help="Fetch and store a specific menu date, YYYY-MM-DD.")
    parser.add_argument("--meal", choices=["breakfast", "lunch", "dinner"], help="Only print one meal.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
    scraper = MenuScraper(DINING_HALLS[args.hall])
    html = open(args.html, encoding="utf-8").read() if args.html else scraper.fetch_html(menu_date=args.date)
    items = scraper.parse(html, menu_date=args.date)
    if args.meal:
        items = [item for item in items if item.meal.lower() == args.meal]

    LOGGER.info("Parsed %s menu items", len(items))
    print(json.dumps([asdict(item) for item in items], indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
