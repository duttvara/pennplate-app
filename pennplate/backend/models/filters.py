from __future__ import annotations

from dataclasses import dataclass


SUPPORTED_MEALS = {"Breakfast", "Lunch", "Dinner"}
SUPPORTED_SORTS = {"items", "stations", "name"}
SUPPORTED_AVOIDED_INGREDIENTS = {"beef", "pork"}

ALLERGEN_QUERY_TO_COLUMN = {
    "wheat-gluten": "contains_wheat_gluten",
    "milk": "contains_milk",
    "egg": "contains_egg",
    "soy": "contains_soy",
    "peanut": "contains_peanut",
    "tree-nut": "contains_tree_nut",
    "sesame": "contains_sesame",
}

ALLERGEN_COLUMN_TO_API = {
    "contains_wheat_gluten": "wheat-gluten",
    "contains_milk": "milk",
    "contains_egg": "egg",
    "contains_soy": "soy",
    "contains_peanut": "peanut",
    "contains_tree_nut": "tree-nut",
    "contains_sesame": "sesame",
}


@dataclass(frozen=True)
class MenuFilters:
    hall: str
    date: str
    meal: str
    vegetarian: bool = False
    vegan: bool = False
    excluded_allergens: tuple[str, ...] = ()
    avoided_ingredients: tuple[str, ...] = ()
