import type { DiningOptionsResponse, FilterState, Hall, MenuResponse, SortMode } from "../types/api";
import { filtersToSearch } from "../utils/filters";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000";

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || "Request failed");
  }
  return data as T;
}

export async function getHalls(): Promise<{ halls: Hall[] }> {
  return getJson("/api/halls");
}

export async function getDiningOptions(filters: FilterState, sort: SortMode = "items"): Promise<DiningOptionsResponse> {
  return getJson(`/api/dining-options?${filtersToSearch(filters, { sort })}`);
}

export async function getMenu(hallSlug: string, filters: FilterState): Promise<MenuResponse> {
  return getJson(`/api/menu?${filtersToSearch(filters, { hall: hallSlug })}`);
}

export function buildDiningOptionsPath(filters: FilterState, sort: SortMode = "items"): string {
  return `/api/dining-options?${filtersToSearch(filters, { sort })}`;
}

export function buildMenuPath(hallSlug: string, filters: FilterState): string {
  return `/api/menu?${filtersToSearch(filters, { hall: hallSlug })}`;
}
