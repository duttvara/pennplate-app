import unittest

from scraper.database import menu_item_to_row, normalize_item_name, upsert_key_for_row
from scraper.scraper import MenuItem


class DatabasePayloadTest(unittest.TestCase):
    def make_item(self, **overrides):
        data = {
            "dining_hall": "Hill House",
            "date": "2026-08-31",
            "meal": "Lunch",
            "station": "global fusion",
            "name": "  Chana   Masala ",
            "description": "spiced chickpeas",
            "calories": 210,
            "vegetarian": False,
            "vegan": True,
            "allergens": ["soy", "wheat_gluten"],
            "contains_wheat_gluten": True,
            "contains_milk": False,
            "contains_egg": False,
            "contains_soy": True,
            "contains_peanut": False,
            "contains_tree_nut": False,
            "contains_sesame": False,
            "info_unavailable": False,
            "source_item_id": "abc123",
            "duplicate_source_item_ids": ["abc123", "def456"],
            "metadata_conflicts": [{"source_item_id": "def456", "fields": {"calories": {"kept": 210, "duplicate": 220}}}],
        }
        data.update(overrides)
        return MenuItem(**data)

    def test_normalized_item_to_db_row(self):
        row = menu_item_to_row(self.make_item(), "hall-id")
        self.assertEqual(row["dining_hall_id"], "hall-id")
        self.assertEqual(row["normalized_name"], "chana masala")
        self.assertEqual(row["description"], "spiced chickpeas")
        self.assertEqual(row["calories"], 210)
        self.assertTrue(row["vegan"])
        self.assertFalse(row["vegetarian"])

    def test_allergens_mapped_correctly(self):
        row = menu_item_to_row(self.make_item(), "hall-id")
        self.assertTrue(row["contains_wheat_gluten"])
        self.assertTrue(row["contains_soy"])
        self.assertFalse(row["contains_milk"])
        self.assertFalse(row["contains_egg"])
        self.assertFalse(row["contains_peanut"])
        self.assertFalse(row["contains_tree_nut"])
        self.assertFalse(row["contains_sesame"])

    def test_null_calories(self):
        row = menu_item_to_row(self.make_item(calories=None), "hall-id")
        self.assertIsNone(row["calories"])

    def test_source_item_ids(self):
        row = menu_item_to_row(self.make_item(), "hall-id")
        self.assertEqual(row["source_item_ids"], ["abc123", "def456"])

    def test_source_item_ids_fall_back_to_primary_id(self):
        row = menu_item_to_row(self.make_item(duplicate_source_item_ids=[]), "hall-id")
        self.assertEqual(row["source_item_ids"], ["abc123"])

    def test_metadata_conflicts(self):
        row = menu_item_to_row(self.make_item(), "hall-id")
        self.assertEqual(row["metadata_conflicts"][0]["source_item_id"], "def456")

    def test_uniqueness_upsert_key_construction(self):
        row = menu_item_to_row(self.make_item(), "hall-id")
        self.assertEqual(
            upsert_key_for_row(row),
            ("hall-id", "2026-08-31", "Lunch", "global fusion", "chana masala"),
        )

    def test_normalize_item_name(self):
        self.assertEqual(normalize_item_name("  White   Pita Bread "), "white pita bread")


if __name__ == "__main__":
    unittest.main()
