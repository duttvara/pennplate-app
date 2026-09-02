export type Meal = "Breakfast" | "Lunch" | "Dinner";
export type SortMode = "items" | "stations" | "name";
export type Allergen = "wheat-gluten" | "milk" | "egg" | "soy" | "peanut" | "tree-nut" | "sesame";
export type AvoidedIngredient = "beef" | "pork";

export interface FilterState {
  date: string;
  meal: Meal;
  vegetarian: boolean;
  vegan: boolean;
  exclude: Allergen[];
  avoid: AvoidedIngredient[];
}

export interface SavedPreferences {
  vegetarian: boolean;
  vegan: boolean;
  exclude: Allergen[];
  avoid: AvoidedIngredient[];
}

export interface Hall {
  id?: string;
  name: string;
  slug: string;
}

export interface MenuItem {
  id: string;
  name: string;
  description: string | null;
  calories: number | null;
  station: string;
  vegetarian: boolean;
  vegan: boolean;
  allergens: Allergen[];
  info_unavailable: boolean;
}

export interface StationGroup {
  name: string;
  matching_item_count: number;
  items: MenuItem[];
}

export interface MenuSummary {
  matching_item_count: number;
  matching_station_count: number;
  total_station_count: number;
  station_coverage: number;
}

export interface MenuResponse {
  hall: Hall;
  date: string;
  meal: Meal;
  summary: MenuSummary;
  stations: StationGroup[];
  check_with_staff: MenuItem[];
}

export interface TopStation {
  name: string;
  matching_item_count: number;
}

export interface DiningOption {
  hall: Hall;
  matching_item_count: number;
  matching_station_count: number;
  total_station_count: number;
  station_coverage: number;
  check_with_staff_count: number;
  top_stations: TopStation[];
}

export interface DiningOptionsResponse {
  date: string;
  meal: Meal;
  options: DiningOption[];
}
