import type { Allergen, AvoidedIngredient, FilterState, Meal, SortMode } from "../types/api";

export const meals: Meal[] = ["Breakfast", "Lunch", "Dinner"];

export const allergens: Array<{ value: Allergen; label: string }> = [
  { value: "wheat-gluten", label: "Wheat / Gluten" },
  { value: "milk", label: "Milk" },
  { value: "egg", label: "Egg" },
  { value: "soy", label: "Soy" },
  { value: "peanut", label: "Peanut" },
  { value: "tree-nut", label: "Tree Nuts" },
  { value: "sesame", label: "Sesame" }
];

export const avoidedIngredients: Array<{ value: AvoidedIngredient; label: string }> = [
  { value: "beef", label: "Beef" },
  { value: "pork", label: "Pork" }
];

export const sortOptions: Array<{ value: SortMode; label: string }> = [
  { value: "items", label: "Most Options" },
  { value: "stations", label: "Most Stations" },
  { value: "name", label: "Name" }
];

export const defaultMenuDate = "2026-08-31";

export const defaultFilters: FilterState = {
  date: defaultMenuDate,
  meal: "Lunch",
  vegetarian: false,
  vegan: false,
  exclude: [],
  avoid: []
};

export function filtersFromSearch(search: string): FilterState {
  const params = new URLSearchParams(search);
  const meal = meals.includes(params.get("meal") as Meal) ? (params.get("meal") as Meal) : "Lunch";
  const exclude = (params.get("exclude") || "")
    .split(",")
    .map((value) => value.trim())
    .filter((value): value is Allergen => allergens.some((allergen) => allergen.value === value));
  const avoid = (params.get("avoid") || "")
    .split(",")
    .map((value) => value.trim())
    .filter((value): value is AvoidedIngredient =>
      avoidedIngredients.some((ingredient) => ingredient.value === value)
    );

  return {
    date: params.get("date") || defaultMenuDate,
    meal,
    vegetarian: params.get("vegetarian") === "true",
    vegan: params.get("vegan") === "true",
    exclude,
    avoid
  };
}

export function filtersToSearch(filters: FilterState, extra?: Record<string, string | undefined>): string {
  const params = new URLSearchParams();
  params.set("date", filters.date);
  params.set("meal", filters.meal);
  if (filters.vegetarian) params.set("vegetarian", "true");
  if (filters.vegan) params.set("vegan", "true");
  if (filters.exclude.length > 0) params.set("exclude", filters.exclude.join(","));
  if (filters.avoid.length > 0) params.set("avoid", filters.avoid.join(","));
  for (const [key, value] of Object.entries(extra || {})) {
    if (value) params.set(key, value);
  }
  return params.toString();
}

export function filterLabelParts(filters: FilterState): string[] {
  const parts = [formatMenuDate(filters.date), filters.meal];
  if (filters.vegan) parts.push("Vegan");
  if (filters.vegetarian) parts.push("Vegetarian");
  for (const value of filters.exclude) {
    parts.push(`Avoid ${allergens.find((allergen) => allergen.value === value)?.label || value}`);
  }
  for (const value of filters.avoid) {
    parts.push(`Avoid ${avoidedIngredients.find((ingredient) => ingredient.value === value)?.label || value}`);
  }
  return parts;
}

export function formatMenuDate(date: string): string {
  const parsed = new Date(`${date}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return date;
  return parsed.toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function formatStationName(name: string): string {
  const lowercaseWords = new Set(["and", "of", "the"]);
  return name
    .split(/\s+/)
    .filter(Boolean)
    .map((word, index) => {
      if (word === "&") return word;
      if (index > 0 && lowercaseWords.has(word)) return word;
      return word.charAt(0).toUpperCase() + word.slice(1);
    })
    .join(" ");
}
