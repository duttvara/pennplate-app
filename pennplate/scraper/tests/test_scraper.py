import logging
import unittest

from scraper.scraper import DINING_HALLS, ENGLISH_HOUSE, HILL_HOUSE, MenuScraper


HTML = """
<html>
<body>
  <a class="site-panel__cafenav-itemlink" href="https://example.test/cafe/hill-house/2026-08-31/">Today</a>
  <section class="panel" data-js="panel" data-type="daypart" data-jump-nav-title="Breakfast">
    <h3 class="site-panel__daypart-station-title">kettles</h3>
    <div data-js="site-panel__daypart-item" data-id="1">
      <button data-js="site-panel__daypart-item-title">Oatmeal</button>
    </div>
  </section>
  <section class="panel" data-js="panel" data-type="daypart" data-jump-nav-title="Lunch">
    <h3 class="site-panel__daypart-station-title">global fusion</h3>
    <div data-js="site-panel__daypart-item" data-id="2">
      <button data-js="site-panel__daypart-item-title">Chana Masala</button>
    </div>
    <div data-js="site-panel__daypart-item" data-id="3">
      <button data-js="site-panel__daypart-item-title">Paneer Curry</button>
    </div>
    <div data-js="site-panel__daypart-item" data-id="4">
      <button data-js="site-panel__daypart-item-title">Naan</button>
    </div>
    <h3 class="site-panel__daypart-station-title">mezze</h3>
    <div data-js="site-panel__daypart-item" data-id="5">
      <button data-js="site-panel__daypart-item-title">Mezze</button>
      <div class="site-panel__daypart-item-description">ask staff for today's options</div>
    </div>
    <div data-js="site-panel__daypart-item" data-id="6">
      <button data-js="site-panel__daypart-item-title">Mystery Side</button>
      <div class="site-panel__daypart-item-calories"></div>
    </div>
  </section>
  <section class="panel" data-js="panel" data-type="wysiwyg">
    <h3 class="site-panel__daypart-station-title">not a station</h3>
    <div data-js="site-panel__daypart-item" data-id="999">
      <button data-js="site-panel__daypart-item-title">Not Food</button>
    </div>
  </section>
  <script>
    Bamco.menu_items = {
      "1": {
        "label": "oatmeal",
        "description": "",
        "nutrition": {"kcal": "190"},
        "ordered_cor_icon": {"0005-0004": {"label": "Vegan"}},
        "cor_icon": {"4": "Vegan"}
      },
      "2": {
        "label": "chana masala",
        "description": "spiced chickpeas",
        "nutrition": {"kcal": "210"},
        "ordered_cor_icon": {"0005-0004": {"label": "Vegan"}},
        "cor_icon": {"4": "Vegan"}
      },
      "3": {
        "label": "paneer curry",
        "description": "",
        "nutrition": {"kcal": "260"},
        "ordered_cor_icon": {
          "0004-0001": {"label": "Vegetarian"},
          "0287-0258": {"label": "Milk"}
        },
        "cor_icon": {"1": "Vegetarian", "258": "Milk"}
      },
      "4": {
        "label": "naan",
        "description": "",
        "nutrition": {"kcal": "160"},
        "ordered_cor_icon": {
          "0004-0001": {"label": "Vegetarian"},
          "0286-0257": {"label": "Wheat/Gluten"},
          "0287-0258": {"label": "Milk"},
          "0288-0259": {"label": "Egg"}
        },
        "cor_icon": {"1": "Vegetarian", "257": "Wheat/Gluten", "258": "Milk", "259": "Egg"}
      },
      "5": {
        "label": "mezze",
        "description": "",
        "nutrition": {"kcal": ""},
        "ordered_cor_icon": {"0290-0262": {"label": "Information Unavailable"}},
        "cor_icon": {"262": "Information Unavailable"}
      },
      "6": {
        "label": "mystery side",
        "description": "",
        "nutrition": {"kcal": ""},
        "ordered_cor_icon": [],
        "cor_icon": []
      }
    };
    Bamco.cor_icons = {};
  </script>
</body>
</html>
"""


class MenuScraperTest(unittest.TestCase):
    def setUp(self):
        self.items = MenuScraper(HILL_HOUSE).parse(HTML)

    def by_name(self, name):
        return next(item for item in self.items if item.name == name)

    def test_meal_parsing_ignores_non_daypart_panels(self):
        self.assertEqual({item.meal for item in self.items}, {"Breakfast", "Lunch"})
        self.assertNotIn("Not Food", {item.name for item in self.items})

    def test_station_parsing(self):
        lunch_stations = {item.station for item in self.items if item.meal == "Lunch"}
        self.assertEqual(lunch_stations, {"global fusion", "mezze"})

    def test_item_name_and_calories(self):
        item = self.by_name("Chana Masala")
        self.assertEqual(item.calories, 210)
        self.assertEqual(item.description, "spiced chickpeas")

    def test_vegan_label_does_not_rewrite_vegetarian(self):
        item = self.by_name("Chana Masala")
        self.assertTrue(item.vegan)
        self.assertFalse(item.vegetarian)

    def test_vegetarian_label(self):
        item = self.by_name("Paneer Curry")
        self.assertTrue(item.vegetarian)
        self.assertFalse(item.vegan)

    def test_single_allergen(self):
        item = self.by_name("Paneer Curry")
        self.assertEqual(item.allergens, ["milk"])
        self.assertTrue(item.contains_milk)

    def test_multiple_allergens(self):
        item = self.by_name("Naan")
        self.assertEqual(item.allergens, ["egg", "milk", "wheat_gluten"])
        self.assertTrue(item.contains_wheat_gluten)
        self.assertTrue(item.contains_milk)
        self.assertTrue(item.contains_egg)

    def test_information_unavailable_and_missing_calories(self):
        item = self.by_name("Mezze")
        self.assertTrue(item.info_unavailable)
        self.assertIsNone(item.calories)

    def test_missing_calories_without_icons(self):
        item = self.by_name("Mystery Side")
        self.assertIsNone(item.calories)
        self.assertEqual(item.allergens, [])

    def test_dining_hall_registry_includes_supported_halls(self):
        self.assertEqual(
            sorted(DINING_HALLS),
            ["1920-commons", "english-house", "hill-house"],
        )
        self.assertEqual(ENGLISH_HOUSE.name, "English House")

    def test_dining_hall_date_url(self):
        self.assertEqual(
            HILL_HOUSE.url_for_date("2026-08-31"),
            "https://university-of-pennsylvania.cafebonappetit.com/cafe/hill-house/2026-08-31/",
        )
        self.assertEqual(HILL_HOUSE.url_for_date(), HILL_HOUSE.source_url)


DUPLICATE_HTML = """
<html>
<body>
  <section class="panel" data-js="panel" data-type="daypart" data-jump-nav-title="Breakfast">
    <h3 class="site-panel__daypart-station-title">kettles</h3>
    <div data-js="site-panel__daypart-item" data-id="b1">
      <button data-js="site-panel__daypart-item-title">Rice</button>
    </div>
  </section>
  <section class="panel" data-js="panel" data-type="daypart" data-jump-nav-title="Lunch">
    <div class="site-panel__daypart-tab-content" id="lunch-specials">
      <h3 class="site-panel__daypart-station-title">global fusion</h3>
      <div data-js="site-panel__daypart-item" data-id="l1">
        <button data-js="site-panel__daypart-item-title">Rice</button>
      </div>
      <div data-js="site-panel__daypart-item" data-id="l2">
        <button data-js="site-panel__daypart-item-title">Rice</button>
      </div>
      <div data-js="site-panel__daypart-item" data-id="l3">
        <button data-js="site-panel__daypart-item-title">Beans</button>
      </div>
      <h3 class="site-panel__daypart-station-title">salad bar</h3>
      <div data-js="site-panel__daypart-item" data-id="l4">
        <button data-js="site-panel__daypart-item-title">Rice</button>
      </div>
    </div>
    <div class="site-panel__daypart-tab-content" id="lunch-condiments">
      <h3 class="site-panel__daypart-station-title">global fusion</h3>
      <div data-js="site-panel__daypart-item" data-id="l5">
        <button data-js="site-panel__daypart-item-title">Rice</button>
      </div>
    </div>
  </section>
  <script>
    Bamco.menu_items = {
      "b1": {"label": "rice", "description": "", "nutrition": {"kcal": "100"}, "ordered_cor_icon": {}, "cor_icon": {}},
      "l1": {"label": "rice", "description": "", "nutrition": {"kcal": "110"}, "ordered_cor_icon": {"v": {"label": "Vegan"}}, "cor_icon": {"4": "Vegan"}},
      "l2": {"label": "rice", "description": "", "nutrition": {"kcal": "110"}, "ordered_cor_icon": {"v": {"label": "Vegan"}}, "cor_icon": {"4": "Vegan"}},
      "l3": {"label": "beans", "description": "", "nutrition": {"kcal": "90"}, "ordered_cor_icon": {}, "cor_icon": {}},
      "l4": {"label": "rice", "description": "", "nutrition": {"kcal": "110"}, "ordered_cor_icon": {}, "cor_icon": {}},
      "l5": {"label": "rice", "description": "", "nutrition": {"kcal": "120"}, "ordered_cor_icon": {"v": {"label": "Vegan"}}, "cor_icon": {"4": "Vegan"}}
    };
    Bamco.cor_icons = {};
  </script>
</body>
</html>
"""


TABBED_DAYPART_HTML = """
<html>
<body>
  <section class="panel" data-js="panel" data-type="daypart" data-jump-nav-title="Dinner">
    <div class="site-panel__daypart-tabs">
      <div class="c-tabs">
        <div class="c-tab__content site-panel__daypart-tab-content c-tab__content--active">
          <h3 class="site-panel__daypart-station-title">kettles</h3>
          <div data-js="site-panel__daypart-item" data-id="d1">
            <button data-js="site-panel__daypart-item-title">Tomato Basil Soup</button>
          </div>
        </div>
        <div class="c-tab__content site-panel__daypart-tab-content">
          <h3 class="site-panel__daypart-station-title">breakfast</h3>
          <div data-js="site-panel__daypart-item" data-id="d2">
            <button data-js="site-panel__daypart-item-title">Bacon</button>
          </div>
        </div>
      </div>
    </div>
  </section>
  <script>
    Bamco.menu_items = {
      "d1": {"label": "tomato basil soup", "description": "", "nutrition": {"kcal": "50"}, "ordered_cor_icon": {}, "cor_icon": {}},
      "d2": {"label": "bacon", "description": "", "nutrition": {"kcal": "90"}, "ordered_cor_icon": {}, "cor_icon": {}}
    };
    Bamco.cor_icons = {};
  </script>
</body>
</html>
"""


class MenuScraperDuplicateTest(unittest.TestCase):
    def setUp(self):
        logger = logging.getLogger("pennplate.scraper")
        was_disabled = logger.disabled
        logger.disabled = True
        try:
            self.items = MenuScraper(HILL_HOUSE).parse(DUPLICATE_HTML, menu_date="2026-08-31")
        finally:
            logger.disabled = was_disabled

    def test_exact_duplicate_item_is_deduplicated(self):
        rice_global = [
            item for item in self.items
            if item.meal == "Lunch" and item.station == "global fusion" and item.name == "Rice"
        ]
        self.assertEqual(len(rice_global), 1)
        self.assertEqual(rice_global[0].duplicate_source_item_ids, ["l1", "l2", "l5"])

    def test_same_item_repeated_in_page_sections_deduplicates(self):
        lunch_global_names = [
            item.name for item in self.items
            if item.meal == "Lunch" and item.station == "global fusion"
        ]
        self.assertEqual(sorted(lunch_global_names), ["Beans", "Rice"])

    def test_same_item_name_at_different_stations_remains_separate(self):
        rice_items = [item for item in self.items if item.meal == "Lunch" and item.name == "Rice"]
        self.assertEqual({item.station for item in rice_items}, {"global fusion", "salad bar"})

    def test_same_item_name_at_different_meals_remains_separate(self):
        rice_items = [item for item in self.items if item.name == "Rice"]
        self.assertEqual({item.meal for item in rice_items}, {"Breakfast", "Lunch"})
        self.assertIn(("Breakfast", "kettles", "Rice"), {(i.meal, i.station, i.name) for i in self.items})
        self.assertIn(("Lunch", "global fusion", "Rice"), {(i.meal, i.station, i.name) for i in self.items})

    def test_conflicting_duplicate_metadata_is_recorded(self):
        rice = next(
            item for item in self.items
            if item.meal == "Lunch" and item.station == "global fusion" and item.name == "Rice"
        )
        self.assertEqual(rice.calories, 110)
        self.assertEqual(rice.metadata_conflicts[0]["source_item_id"], "l5")
        self.assertEqual(rice.metadata_conflicts[0]["fields"]["calories"], {"kept": 110, "duplicate": 120})


class MenuScraperTabbedDaypartTest(unittest.TestCase):
    def test_only_active_daypart_tab_is_parsed(self):
        items = MenuScraper(HILL_HOUSE).parse(TABBED_DAYPART_HTML, menu_date="2026-08-31")

        self.assertEqual([item.name for item in items], ["Tomato Basil Soup"])
        self.assertEqual([item.station for item in items], ["kettles"])
        self.assertEqual({item.meal for item in items}, {"Dinner"})
        self.assertNotIn("Bacon", {item.name for item in items})
        self.assertNotIn("breakfast", {item.station for item in items})


if __name__ == "__main__":
    unittest.main()
