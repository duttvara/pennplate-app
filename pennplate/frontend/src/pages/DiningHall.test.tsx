import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import DiningHall from "./DiningHall";
import { getMenu } from "../services/api";
import type { Meal, MenuResponse } from "../types/api";

vi.mock("../services/api", () => ({
  getMenu: vi.fn()
}));

const mockedGetMenu = vi.mocked(getMenu);

function menuResponse(meal: Meal): MenuResponse {
  return {
    hall: { name: "Hill House", slug: "hill-house" },
    date: "2026-08-31",
    meal,
    summary: {
      matching_item_count: 1,
      matching_station_count: 1,
      total_station_count: 3,
      station_coverage: 0.33
    },
    stations: [
      {
        name: `${meal.toLowerCase()} station`,
        matching_item_count: 1,
        items: [
          {
            id: `${meal}-item`,
            name: `${meal} Only Item`,
            description: null,
            calories: null,
            station: `${meal.toLowerCase()} station`,
            vegetarian: false,
            vegan: true,
            allergens: [],
            info_unavailable: false
          }
        ]
      }
    ],
    check_with_staff: []
  };
}

function renderDiningHall(search: string) {
  render(
    <MemoryRouter initialEntries={[`/hall/hill-house${search}`]}>
      <Routes>
        <Route path="/hall/:hallSlug" element={<DiningHall />} />
      </Routes>
    </MemoryRouter>
  );
}

describe("DiningHall", () => {
  beforeEach(() => {
    mockedGetMenu.mockReset();
  });

  it.each<Meal>(["Breakfast", "Lunch", "Dinner"])("requests and renders only the selected %s menu", async (meal) => {
    mockedGetMenu.mockResolvedValue(menuResponse(meal));

    renderDiningHall(`?date=2026-08-31&meal=${meal}&vegan=true&exclude=wheat-gluten&avoid=pork`);

    await waitFor(() =>
      expect(mockedGetMenu).toHaveBeenCalledWith("hill-house", {
        date: "2026-08-31",
        meal,
        vegetarian: false,
        vegan: true,
        exclude: ["wheat-gluten"],
        avoid: ["pork"]
      })
    );
    expect(await screen.findByRole("heading", { name: `${meal} Only Item` })).toBeInTheDocument();
    expect(screen.getAllByText(meal).length).toBeGreaterThan(0);
    expect(screen.getByText("1 of 3")).toBeInTheDocument();
    expect(screen.queryByText(/Station coverage/i)).not.toBeInTheDocument();
  });

  it("preserves filters when navigating back to results", async () => {
    mockedGetMenu.mockResolvedValue(menuResponse("Dinner"));

    renderDiningHall("?date=2026-08-31&meal=Dinner&vegetarian=true&vegan=true&exclude=wheat-gluten,milk&avoid=beef");

    expect(await screen.findByRole("link", { name: "Back to results" })).toHaveAttribute(
      "href",
      "/results?date=2026-08-31&meal=Dinner&vegetarian=true&vegan=true&exclude=wheat-gluten,milk&avoid=beef"
    );
  });
});
