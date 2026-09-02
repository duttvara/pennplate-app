create extension if not exists pgcrypto;

create table if not exists public.dining_halls (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  slug text unique not null,
  source_url text not null,
  latitude double precision,
  longitude double precision,
  created_at timestamptz not null default now()
);

insert into public.dining_halls (id, name, slug, source_url)
values
(
  '11111111-1111-4111-8111-111111111111',
  'Hill House',
  'hill-house',
  'https://university-of-pennsylvania.cafebonappetit.com/cafe/hill-house/'
),
(
  '22222222-2222-4222-8222-222222222222',
  '1920 Commons',
  '1920-commons',
  'https://university-of-pennsylvania.cafebonappetit.com/cafe/1920-commons/'
),
(
  '33333333-3333-4333-8333-333333333333',
  'English House',
  'english-house',
  'https://university-of-pennsylvania.cafebonappetit.com/cafe/kings-court-english-house/'
)
on conflict (slug) do update
set
  name = excluded.name,
  source_url = excluded.source_url;

create table if not exists public.menu_items (
  id uuid primary key default gen_random_uuid(),
  dining_hall_id uuid not null references public.dining_halls(id) on delete cascade,
  date date not null,
  meal text not null,
  station text not null,
  name text not null,
  normalized_name text not null,
  description text,
  calories integer,
  vegetarian boolean not null default false,
  vegan boolean not null default false,
  contains_wheat_gluten boolean not null default false,
  contains_milk boolean not null default false,
  contains_egg boolean not null default false,
  contains_soy boolean not null default false,
  contains_peanut boolean not null default false,
  contains_tree_nut boolean not null default false,
  contains_sesame boolean not null default false,
  info_unavailable boolean not null default false,
  source_item_ids text[] not null default '{}',
  metadata_conflicts jsonb not null default '{}'::jsonb,
  scraped_at timestamptz not null default now(),
  constraint menu_items_unique_logical_item unique (
    dining_hall_id,
    date,
    meal,
    station,
    normalized_name
  )
);

create index if not exists menu_items_lookup_idx
on public.menu_items (date, meal, dining_hall_id);

create table if not exists public.user_preferences (
  user_id uuid primary key references auth.users(id) on delete cascade,
  vegetarian boolean not null default false,
  vegan boolean not null default false,
  avoid_wheat_gluten boolean not null default false,
  avoid_milk boolean not null default false,
  avoid_egg boolean not null default false,
  avoid_soy boolean not null default false,
  avoid_peanut boolean not null default false,
  avoid_tree_nut boolean not null default false,
  avoid_sesame boolean not null default false,
  avoid_beef boolean not null default false,
  avoid_pork boolean not null default false,
  updated_at timestamptz not null default now()
);

alter table public.user_preferences add column if not exists avoid_beef boolean not null default false;
alter table public.user_preferences add column if not exists avoid_pork boolean not null default false;

create table if not exists public.scrape_runs (
  id uuid primary key default gen_random_uuid(),
  dining_hall_id uuid references public.dining_halls(id) on delete set null,
  date date,
  meal text,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  status text not null,
  raw_item_count integer,
  final_item_count integer,
  duplicate_count integer,
  metadata_conflict_count integer,
  error_message text
);

alter table public.dining_halls enable row level security;
alter table public.menu_items enable row level security;
alter table public.user_preferences enable row level security;
alter table public.scrape_runs enable row level security;

drop policy if exists "Dining halls are publicly readable" on public.dining_halls;
create policy "Dining halls are publicly readable"
on public.dining_halls for select
to anon, authenticated
using (true);

drop policy if exists "Menu items are publicly readable" on public.menu_items;
create policy "Menu items are publicly readable"
on public.menu_items for select
to anon, authenticated
using (true);

drop policy if exists "Users can select own preferences" on public.user_preferences;
create policy "Users can select own preferences"
on public.user_preferences for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can insert own preferences" on public.user_preferences;
create policy "Users can insert own preferences"
on public.user_preferences for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users can update own preferences" on public.user_preferences;
create policy "Users can update own preferences"
on public.user_preferences for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users can delete own preferences" on public.user_preferences;
create policy "Users can delete own preferences"
on public.user_preferences for delete
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Scrape runs are publicly readable" on public.scrape_runs;
create policy "Scrape runs are publicly readable"
on public.scrape_runs for select
to anon, authenticated
using (true);
