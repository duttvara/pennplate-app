# PennPlate

PennPlate is a full-stack Penn Dining menu finder. It lets students choose a date and meal, compare the options available at Hill House, 1920 Commons, and English House, and filter those menus around dietary needs and food restrictions.

The project combines a React frontend, a Flask API, Supabase for storage and authentication, and a Python scraper that collects and normalizes menu data from Bon Appetit. The goal is to make it easier to answer a practical question: where can I eat today, given what I need to avoid?

## Live Project

Frontend: [PennPlate on Vercel](https://pennplate-app.vercel.app)

API: [PennPlate API on Render](https://pennplate-app.onrender.com/api/health)

## Features

- Search menus by date and meal: breakfast, lunch, or dinner.
- Compare matching dishes and station coverage across three Penn Dining halls.
- Filter for vegetarian or vegan options.
- Avoid listed allergens, including wheat/gluten, milk, egg, soy, peanut, tree nuts, and sesame.
- Avoid beef and pork using conservative ingredient and menu-text screening.
- Preserve Bon Appetit dietary labels, allergen metadata, calories, descriptions, and unavailable information.
- Show information-unavailable items separately instead of treating them as automatically safe.
- Open a hall-specific menu while preserving the selected date, meal, and filters.
- Create an account, log in, log out, and save dietary preferences with Supabase Auth.
- Ingest menus for all supported halls with deterministic deduplication.
- Run daily menu ingestion through GitHub Actions.

## Development Time

I spent approximately 15 to 20 focused hours developing and testing PennPlate. That time included the scraper, database schema and ingestion, Flask API, React interface, authentication, deployment setup, and validation of the menu filtering behavior.

## Run Locally

### Requirements

Install the following first:

- Python 3.12 or newer
- Node.js 18 or newer
- Yarn
- A Supabase project with the PennPlate schema applied

### 1. Clone the repository

```bash
git clone https://github.com/duttvara/pennplate-app.git
cd pennplate-app/pennplate
```

### 2. Configure the backend

Create a backend environment file:

```bash
cp .env.example .env
```

Add the Supabase project URL and service-role key to `.env`:

```text
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

The service-role key is for the backend only. Do not put it in the frontend or commit it to GitHub.

Apply `supabase/schema.sql` in the Supabase SQL editor before starting the API.

Create and activate a Python virtual environment, then install the dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pip install -r scraper/requirements.txt
```

Start the Flask API:

```bash
python backend/app.py
```

The API runs at `http://localhost:5000`.

### 3. Configure the frontend

Open a second terminal and move into the frontend directory:

```bash
cd pennplate/frontend
cp .env.example .env
```

Set the frontend environment variables:

```text
VITE_API_BASE_URL=http://localhost:5000
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

The anon key is safe for browser use when Supabase Row Level Security is configured. Do not use the service-role key here.

Install the frontend dependencies and start Vite:

```bash
yarn install
yarn dev
```

Open the local URL printed by Vite, usually `http://127.0.0.1:5173`.

### 4. Run the tests

From the `pennplate` directory, run the backend and scraper tests:

```bash
python3 -m pytest backend/tests scraper/tests
```

From `pennplate/frontend`, run the frontend tests and production build:

```bash
yarn test
yarn build
```

### 5. Run ingestion manually

With the backend environment variables configured, ingest a particular date for a hall:

```bash
python scraper/ingest.py --hall hill-house --date 2026-09-01
python scraper/ingest.py --hall 1920-commons --date 2026-09-01
python scraper/ingest.py --hall english-house --date 2026-09-01
```

The GitHub Actions workflow at `.github/workflows/daily-ingest.yml` runs the same process automatically each day. It uses the `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` repository secrets. The workflow can also be started manually for a specific date when historical data needs to be backfilled.

## Data and Filtering Notes

Menu items are deduplicated by date, dining hall, meal, station, and normalized item name. Duplicate source IDs and metadata conflicts are retained for auditability.

Vegetarian and vegan values preserve the labels supplied by Bon Appetit. Application filtering treats a vegan item as satisfying a vegetarian preference without rewriting the scraped source labels.

An allergen flag means Bon Appetit explicitly listed that allergen. A false flag means the allergen was not listed by the source, not that the item is medically confirmed allergen-free. Items marked information unavailable are excluded from conservative allergen-sensitive matches.
