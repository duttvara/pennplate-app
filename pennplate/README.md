# PennPlate

PennPlate is a Penn Dining dietary finder for comparing dining hall menu options by meal, dietary preference, and listed allergens.

This repository is currently complete through Phase 2:

- Phase 1: Hill House scraper validation
- Phase 2: Supabase schema and ingestion preparation

## Current Structure

```text
pennplate/
  backend/
    app.py
    routes/
    services/
    tests/
  scraper/
    scraper.py
    database.py
    ingest.py
    tests/
  supabase/
    schema.sql
  .env.example
```

## Phase 2 Commands

```bash
cd pennplate
python3 -m unittest discover scraper/tests
python3 scraper/ingest.py --html ../work/html/hill-house.html --meal lunch --dry-run
```

To ingest into Supabase, first run `supabase/schema.sql` in your Supabase SQL editor and export the variables from `.env.example`.

The scraper currently supports:

- Hill House: `hill-house`
- 1920 Commons: `1920-commons`
- English House: `english-house`

Example ingestion commands:

```bash
python3 scraper/ingest.py --hall hill-house
python3 scraper/ingest.py --hall 1920-commons
python3 scraper/ingest.py --hall english-house
```

The repository includes a GitHub Actions workflow at `.github/workflows/daily-ingest.yml`.
Add `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` as GitHub Actions secrets, then run it
manually with a `YYYY-MM-DD` date to backfill a menu or let it run daily. Ingestion is
idempotent for the same hall, date, meal, station, and normalized item name.

## Phase 3 Backend

```bash
cd pennplate
python3 -m venv .venv
source .venv/bin/activate
pip install -r scraper/requirements.txt
pip install -r backend/requirements.txt
python backend/app.py
```

The API runs at `http://localhost:5000`.

## Phase 5 Auth and Saved Preferences

Run the updated `supabase/schema.sql` in the Supabase SQL editor. It creates the RLS-protected `user_preferences` row for each authenticated user and adds `avoid_beef` and `avoid_pork` fields.

For the React app, create `frontend/.env` from `frontend/.env.example` and fill in the Supabase browser-safe values from Project Settings > API:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

The service-role key must stay in the backend `.env`; it must never be placed in `frontend/.env`. Without the frontend Supabase values, PennPlate continues to work anonymously and simply does not show auth controls.

Authenticated users can sign up, log in, log out, load saved dietary/allergen/beef/pork preferences, and save the current Home filters. Anonymous users retain the full menu search flow.
