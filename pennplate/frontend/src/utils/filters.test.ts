import { describe, expect, it } from "vitest";
import { defaultMenuDate, filterLabelParts, filtersFromSearch, filtersToSearch, formatStationName } from "./filters";
import type { FilterState } from "../types/api";

describe("filter URL helpers", () => {
  it("defaults to the seeded menu date and lunch", () => {
    expect(filtersFromSearch("")).toEqual({
      date: defaultMenuDate,
      meal: "Lunch",
      vegetarian: false,
      vegan: false,
      exclude: [],
      avoid: []
    });
  });

  it("parses and serializes supported filters", () => {
    const filters: FilterState = {
      date: "2026-08-31",
      meal: "Dinner",
      vegetarian: true,
      vegan: false,
      exclude: ["milk", "soy"],
      avoid: ["beef", "pork"]
    };

    const search = filtersToSearch(filters, { sort: "stations" });
    const params = new URLSearchParams(search);

    expect(params.get("date")).toBe("2026-08-31");
    expect(params.get("meal")).toBe("Dinner");
    expect(params.get("vegetarian")).toBe("true");
    expect(params.get("exclude")).toBe("milk,soy");
    expect(params.get("avoid")).toBe("beef,pork");
    expect(params.get("sort")).toBe("stations");
    expect(filtersFromSearch(`?${search}`)).toEqual(filters);
  });

  it("drops unsupported allergens from incoming URLs", () => {
    const filters = filtersFromSearch("?exclude=milk,unsupported,sesame");

    expect(filters.exclude).toEqual(["milk", "sesame"]);
  });

  it("drops unsupported avoided ingredients from incoming URLs", () => {
    const filters = filtersFromSearch("?avoid=beef,chicken,pork");

    expect(filters.avoid).toEqual(["beef", "pork"]);
  });

  it("builds readable filter labels", () => {
    const labels = filterLabelParts({
      date: "2026-08-31",
      meal: "Lunch",
      vegan: true,
      vegetarian: false,
      exclude: ["wheat-gluten"],
      avoid: ["pork"]
    });

    expect(labels).toContain("Aug 31, 2026");
    expect(labels).toContain("Lunch");
    expect(labels).toContain("Vegan");
    expect(labels).toContain("Avoid Wheat / Gluten");
    expect(labels).toContain("Avoid Pork");
  });

  it("formats normalized station names for display", () => {
    expect(formatStationName("global fusion")).toBe("Global Fusion");
    expect(formatStationName("fruit & yogurt")).toBe("Fruit & Yogurt");
    expect(formatStationName("fruit and yogurt")).toBe("Fruit and Yogurt");
  });
});
