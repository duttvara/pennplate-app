import unittest

from backend.app import create_app


class FakeDB:
    def __init__(self):
        self.hall = {"id": "hall-1", "name": "Hill House", "slug": "hill-house"}
        self.rows = [
            {
                "id": "1",
                "station": "global fusion",
                "name": "Chana Masala",
                "description": None,
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
                "name": "Naan",
                "description": None,
                "calories": 160,
                "vegetarian": True,
                "vegan": False,
                "contains_wheat_gluten": True,
                "contains_milk": True,
                "contains_egg": True,
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
                "description": None,
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
                "id": "5",
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

    def list_halls(self):
        return [self.hall, {"id": "hall-2", "name": "Empty Hall", "slug": "empty-hall"}]

    def get_hall_by_slug(self, slug):
        return self.hall if slug == "hill-house" else None

    def menu_items(self, dining_hall_id, date, meal):
        return self.rows if dining_hall_id == "hall-1" and date == "2026-08-31" and meal == "Lunch" else []


class FlaskAppTest(unittest.TestCase):
    def setUp(self):
        self.client = create_app(db_client=FakeDB()).test_client()

    def test_health(self):
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"status": "ok"})

    def test_halls(self):
        response = self.client.get("/api/halls")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([hall["slug"] for hall in response.get_json()["halls"]], ["hill-house", "empty-hall"])

    def test_cors_allows_local_dev_hosts(self):
        for origin in ["http://localhost:5173", "http://127.0.0.1:5173"]:
            with self.subTest(origin=origin):
                response = self.client.get("/api/health", headers={"Origin": origin})
                self.assertEqual(response.headers["Access-Control-Allow-Origin"], origin)

    def test_menu_response_shape(self):
        response = self.client.get("/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data["hall"], {"name": "Hill House", "slug": "hill-house"})
        self.assertEqual(data["summary"]["matching_item_count"], 5)
        self.assertEqual(data["summary"]["total_station_count"], 5)
        self.assertIn("stations", data)
        self.assertIn("check_with_staff", data)

    def test_menu_filters_and_staff_bucket(self):
        response = self.client.get("/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch&exclude=sesame")
        data = response.get_json()
        names = {item["name"] for station in data["stations"] for item in station["items"]}
        self.assertEqual(names, {"Chana Masala", "Smash Burger", "Bacon"})
        self.assertEqual([item["name"] for item in data["check_with_staff"]], ["Salad Bar"])

    def test_menu_filters_avoided_ingredients_by_source_text(self):
        response = self.client.get("/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch&avoid=beef,pork")
        data = response.get_json()
        names = {item["name"] for station in data["stations"] for item in station["items"]}

        self.assertNotIn("Smash Burger", names)
        self.assertNotIn("Bacon", names)
        self.assertIn("Chana Masala", names)

    def test_dining_options_sort(self):
        response = self.client.get("/api/dining-options?date=2026-08-31&meal=Lunch&sort=items")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["options"]), 1)
        self.assertEqual(data["options"][0]["hall"]["slug"], "hill-house")
        self.assertEqual(data["options"][0]["total_station_count"], 5)

    def test_invalid_inputs(self):
        cases = [
            "/api/menu?hall=hill-house&date=2026-08-31&meal=Snack",
            "/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch&exclude=shellfish",
            "/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch&avoid=chicken",
            "/api/menu?hall=hill-house&date=2026-08-31&meal=Lunch&vegan=maybe",
            "/api/dining-options?date=2026-08-31&meal=Lunch&sort=score",
            "/api/menu?hall=commons&date=2026-08-31&meal=Lunch",
        ]
        for path in cases:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.get_json())


if __name__ == "__main__":
    unittest.main()
