import unittest

from backend.models.filters import MenuFilters
from backend.services.filtering import build_menu_response, item_allergens


HALL = {"id": "hall-1", "name": "Hill House", "slug": "hill-house"}

ROWS = [
    {
        "id": "1",
        "station": "global fusion",
        "name": "Chana Masala",
        "description": "spiced chickpeas",
        "calories": 210,
        "vegetarian": False,
        "vegan": True,
        "contains_wheat_gluten": False,
        "contains_milk": False,
        "contains_egg": False,
        "contains_soy": False,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": False,
        "info_unavailable": False,
    },
    {
        "id": "2",
        "station": "mezze",
        "name": "White Pita Bread",
        "description": None,
        "calories": 90,
        "vegetarian": True,
        "vegan": False,
        "contains_wheat_gluten": True,
        "contains_milk": True,
        "contains_egg": False,
        "contains_soy": True,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": True,
        "info_unavailable": False,
    },
    {
        "id": "3",
        "station": "salad bar",
        "name": "Salad Bar",
        "description": "ask staff",
        "calories": None,
        "vegetarian": False,
        "vegan": False,
        "contains_wheat_gluten": False,
        "contains_milk": False,
        "contains_egg": False,
        "contains_soy": False,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": False,
        "info_unavailable": True,
    },
    {
        "id": "4",
        "station": "kettles",
        "name": "Tomato Soup",
        "description": None,
        "calories": 50,
        "vegetarian": False,
        "vegan": True,
        "contains_wheat_gluten": False,
        "contains_milk": False,
        "contains_egg": False,
        "contains_soy": True,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": False,
        "info_unavailable": False,
    },
    {
        "id": "5",
        "station": "hill grill",
        "name": "Smash Burger",
        "description": "local beef from Roseda Farm",
        "calories": 510,
        "vegetarian": False,
        "vegan": False,
        "contains_wheat_gluten": False,
        "contains_milk": False,
        "contains_egg": False,
        "contains_soy": False,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": False,
        "info_unavailable": False,
    },
    {
        "id": "6",
        "station": "breakfast bar",
        "name": "Bacon",
        "description": None,
        "calories": 90,
        "vegetarian": False,
        "vegan": False,
        "contains_wheat_gluten": False,
        "contains_milk": False,
        "contains_egg": False,
        "contains_soy": False,
        "contains_peanut": False,
        "contains_tree_nut": False,
        "contains_sesame": False,
        "info_unavailable": False,
    },
]


def filters(**overrides):
    data = {
        "hall": "hill-house",
        "date": "2026-08-31",
        "meal": "Lunch",
        "vegetarian": False,
        "vegan": False,
        "excluded_allergens": (),
        "avoided_ingredients": (),
    }
    data.update(overrides)
    return MenuFilters(**data)


class FilteringTest(unittest.TestCase):
    def test_vegan_filter(self):
        response = build_menu_response(HALL, ROWS, filters(vegan=True))
        names = {item["name"] for station in response["stations"] for item in station["items"]}
        self.assertEqual(names, {"Chana Masala", "Tomato Soup"})

    def test_vegetarian_includes_vegan(self):
        response = build_menu_response(HALL, ROWS, filters(vegetarian=True))
        names = {item["name"] for station in response["stations"] for item in station["items"]}
        self.assertEqual(names, {"Chana Masala", "White Pita Bread", "Tomato Soup"})

    def test_single_allergen_exclusion(self):
        response = build_menu_response(HALL, ROWS, filters(excluded_allergens=("soy",)))
        names = {item["name"] for station in response["stations"] for item in station["items"]}
        self.assertEqual(names, {"Chana Masala", "Smash Burger", "Bacon"})

    def test_multiple_allergen_exclusions(self):
        response = build_menu_response(HALL, ROWS, filters(excluded_allergens=("soy", "sesame")))
        names = {item["name"] for station in response["stations"] for item in station["items"]}
        self.assertEqual(names, {"Chana Masala", "Smash Burger", "Bacon"})

    def test_info_unavailable_separated_only_for_allergen_searches(self):
        without_allergens = build_menu_response(HALL, ROWS, filters())
        self.assertEqual(len(without_allergens["check_with_staff"]), 0)
        self.assertIn("Salad Bar", {item["name"] for station in without_allergens["stations"] for item in station["items"]})

        with_allergens = build_menu_response(HALL, ROWS, filters(excluded_allergens=("sesame",)))
        self.assertEqual([item["name"] for item in with_allergens["check_with_staff"]], ["Salad Bar"])

    def test_avoided_ingredient_filter_uses_item_name_description_and_station(self):
        response = build_menu_response(HALL, ROWS, filters(avoided_ingredients=("beef", "pork")))
        names = {item["name"] for station in response["stations"] for item in station["items"]}

        self.assertNotIn("Smash Burger", names)
        self.assertNotIn("Bacon", names)
        self.assertIn("Chana Masala", names)

    def test_grouping_by_station_and_station_coverage(self):
        response = build_menu_response(HALL, ROWS, filters(vegan=True))
        self.assertEqual(response["summary"]["total_station_count"], 6)
        self.assertEqual(response["summary"]["matching_station_count"], 2)
        self.assertEqual(response["summary"]["station_coverage"], 0.333)
        self.assertEqual({station["name"] for station in response["stations"]}, {"global fusion", "kettles"})

    def test_allergen_array_serialization(self):
        pita = ROWS[1]
        self.assertEqual(item_allergens(pita), ["wheat-gluten", "milk", "soy", "sesame"])


if __name__ == "__main__":
    unittest.main()
