# PennPlate Scraper Notes

## Phase 1 Source Choice

Hill House exposes three useful menu sources:

- Normal cafe page: `https://university-of-pennsylvania.cafebonappetit.com/cafe/hill-house/`
- Print menu: `https://legacy.cafebonappetit.com/print-menu/cafe/636/menu/622912/days/today/pgbrks/0/`
- Weekly menu: `https://legacy.cafebonappetit.com/weekly-menu/622912`

The normal cafe page is the best Phase 1 source. Its HTML includes the collapsed menu content, stable daypart panels, item IDs, station headings, calories, descriptions, and a `Bamco.menu_items` JavaScript object with normalized nutrition and icon metadata. The print page is smaller and easier to scan visually, but it does not preserve enough structured metadata for the MVP, especially calories and stable item IDs.

The scraper does not click or automate a browser. It requests the static HTML and parses:

- `[data-type="daypart"]` for Breakfast/Lunch/Dinner groupings
- `.site-panel__daypart-station-title` station headings, traversed in document order so each item is assigned to the closest preceding station
- `div[data-js="site-panel__daypart-item"]` menu item IDs
- `Bamco.menu_items` for source metadata such as descriptions, calories, dietary labels, allergens, and information-unavailable flags
- deterministic deduplication by `date + dining hall + meal + station + normalized item name`

## Metadata Semantics

The scraper preserves Bon Appétit's raw dietary labels. If the source marks an item as Vegan only, `vegan` is `true` and `vegetarian` remains `false`. Later application filtering should treat vegan items as satisfying a user's vegetarian preference, but the scraped source flags should not be rewritten unless Bon Appétit explicitly provides both labels.

Allergen booleans mean Bon Appétit explicitly listed that allergen for the item. A `false` value means the allergen was not listed by the source; it must not be interpreted as medically confirmed allergen-free. PennPlate should not infer allergens from item names, descriptions, or ingredients.

When `info_unavailable` is `true`, preserve that value. For allergen-sensitive searches, the app should exclude those items from default matching results and optionally show them separately under a label such as "Check with dining staff."

## Deduplication Semantics

Bon Appétit can repeat the same logical item in more than one tab, such as the main specials tab and a condiments/extras tab. The scraper emits one record per logical item using:

`date + dining hall + meal + station + normalized item name`

The first source occurrence in rendered order is kept as canonical. Duplicate source item IDs are retained in `duplicate_source_item_ids`. If duplicate records disagree on useful metadata such as calories, description, dietary flags, allergens, or information-unavailable status, the scraper logs a warning and stores the disagreement in `metadata_conflicts`.

## Run

```bash
pip install -r scraper/requirements.txt
python scraper/scraper.py --hall hill-house --meal lunch --pretty
python scraper/scraper.py --hall 1920-commons --meal lunch --pretty
python scraper/scraper.py --hall english-house --meal lunch --pretty
```

To parse a previously saved HTML file:

```bash
python scraper/scraper.py --hall hill-house --html ../work/html/hill-house.html --meal lunch --pretty
```

## Tests

```bash
python -m unittest discover scraper/tests
```
