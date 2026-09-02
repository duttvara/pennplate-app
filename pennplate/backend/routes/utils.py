from __future__ import annotations

import re
from datetime import date

from flask import Request

from backend.models.filters import (
    ALLERGEN_QUERY_TO_COLUMN,
    SUPPORTED_AVOIDED_INGREDIENTS,
    SUPPORTED_MEALS,
    SUPPORTED_SORTS,
    MenuFilters,
)


class BadRequest(ValueError):
    pass


def parse_bool(value: str | None, name: str) -> bool:
    if value is None or value == "":
        return False
    normalized = value.strip().casefold()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise BadRequest(f"Invalid boolean for {name}: {value}")


def parse_date(value: str | None) -> str:
    if not value:
        return date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise BadRequest(f"Invalid date: {value}")
    return value


def parse_meal(value: str | None) -> str:
    if not value:
        raise BadRequest("Missing required meal")
    meal = value.strip().title()
    if meal not in SUPPORTED_MEALS:
        raise BadRequest(f"Invalid meal: {value}")
    return meal


def parse_excluded_allergens(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    allergens = tuple(allergen.strip().casefold() for allergen in value.split(",") if allergen.strip())
    for allergen in allergens:
        if allergen not in ALLERGEN_QUERY_TO_COLUMN:
            raise BadRequest(f"Invalid allergen: {allergen}")
    return allergens


def parse_avoided_ingredients(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    ingredients = tuple(ingredient.strip().casefold() for ingredient in value.split(",") if ingredient.strip())
    for ingredient in ingredients:
        if ingredient not in SUPPORTED_AVOIDED_INGREDIENTS:
            raise BadRequest(f"Invalid avoided ingredient: {ingredient}")
    return ingredients


def parse_sort(value: str | None) -> str:
    sort = (value or "items").strip().casefold()
    if sort not in SUPPORTED_SORTS:
        raise BadRequest(f"Invalid sort option: {sort}")
    return sort


def menu_filters_from_request(request: Request, require_hall: bool = True) -> MenuFilters:
    hall = (request.args.get("hall") or "").strip()
    if require_hall and not hall:
        raise BadRequest("Missing required hall")

    return MenuFilters(
        hall=hall,
        date=parse_date(request.args.get("date")),
        meal=parse_meal(request.args.get("meal")),
        vegetarian=parse_bool(request.args.get("vegetarian"), "vegetarian"),
        vegan=parse_bool(request.args.get("vegan"), "vegan"),
        excluded_allergens=parse_excluded_allergens(request.args.get("exclude")),
        avoided_ingredients=parse_avoided_ingredients(request.args.get("avoid")),
    )
