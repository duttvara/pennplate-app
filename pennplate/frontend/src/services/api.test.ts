import { describe, expect, it } from "vitest";
import { buildDiningOptionsPath, buildMenuPath } from "./api";
import type { FilterState } from "../types/api";

const filters: FilterState = {
  date: "2026-08-31",
  meal: "Lunch",
  vegan: true,
  vegetarian: false,
  exclude: ["milk", "egg"],
  avoid: ["pork"]
};

describe("API path builders", () => {
  it("builds dining-options URLs with preserved filters and sort mode", () => {
    const url = new URL(buildDiningOptionsPath(filters, "name"), "http://local.test");

    expect(url.pathname).toBe("/api/dining-options");
    expect(url.searchParams.get("date")).toBe("2026-08-31");
    expect(url.searchParams.get("meal")).toBe("Lunch");
    expect(url.searchParams.get("vegan")).toBe("true");
    expect(url.searchParams.get("exclude")).toBe("milk,egg");
    expect(url.searchParams.get("avoid")).toBe("pork");
    expect(url.searchParams.get("sort")).toBe("name");
  });

  it("builds menu URLs with the selected hall", () => {
    const url = new URL(buildMenuPath("hill-house", filters), "http://local.test");

    expect(url.pathname).toBe("/api/menu");
    expect(url.searchParams.get("hall")).toBe("hill-house");
    expect(url.searchParams.get("date")).toBe("2026-08-31");
  });
});
