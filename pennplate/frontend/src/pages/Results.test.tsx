import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Results from "./Results";
import { getDiningOptions } from "../services/api";

vi.mock("../services/api", () => ({
  getDiningOptions: vi.fn()
}));

const mockedGetDiningOptions = vi.mocked(getDiningOptions);

describe("Results", () => {
  beforeEach(() => {
    mockedGetDiningOptions.mockReset();
  });

  it("renders dining options returned by the API", async () => {
    mockedGetDiningOptions.mockResolvedValue({
      date: "2026-08-31",
      meal: "Lunch",
      options: [
        {
          hall: { name: "Hill House", slug: "hill-house" },
          matching_item_count: 158,
          matching_station_count: 20,
          total_station_count: 22,
          station_coverage: 0.91,
          check_with_staff_count: 4,
          top_stations: [{ name: "Global Fusion", matching_item_count: 14 }]
        }
      ]
    });

    render(
      <MemoryRouter initialEntries={["/results?date=2026-08-31&meal=Lunch&vegan=true"]}>
        <Routes>
          <Route path="/results" element={<Results />} />
        </Routes>
      </MemoryRouter>
    );

    await waitFor(() => expect(mockedGetDiningOptions).toHaveBeenCalled());
    expect(await screen.findByRole("heading", { name: "Hill House" })).toBeInTheDocument();
    expect(screen.getByText("158")).toBeInTheDocument();
    expect(screen.getByText("Global Fusion")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /view menu/i })).toHaveAttribute(
      "href",
      "/hall/hill-house?date=2026-08-31&meal=Lunch&vegan=true"
    );
  });

  it("preserves meal, diet, allergen, and date filters in View Menu links", async () => {
    mockedGetDiningOptions.mockResolvedValue({
      date: "2026-08-31",
      meal: "Dinner",
      options: [
        {
          hall: { name: "Hill House", slug: "hill-house" },
          matching_item_count: 42,
          matching_station_count: 8,
          total_station_count: 11,
          station_coverage: 0.73,
          check_with_staff_count: 0,
          top_stations: [{ name: "chef's table", matching_item_count: 6 }]
        }
      ]
    });

    render(
      <MemoryRouter initialEntries={["/results?date=2026-08-31&meal=Dinner&vegan=true&vegetarian=true&exclude=wheat-gluten,milk&avoid=beef,pork&sort=items"]}>
        <Routes>
          <Route path="/results" element={<Results />} />
        </Routes>
      </MemoryRouter>
    );

    const link = await screen.findByRole("link", { name: /view menu/i });
    expect(link).toHaveAttribute(
      "href",
      "/hall/hill-house?date=2026-08-31&meal=Dinner&vegetarian=true&vegan=true&exclude=wheat-gluten%2Cmilk&avoid=beef%2Cpork"
    );
  });

  it("does not display the station coverage percentage on dining hall cards", async () => {
    mockedGetDiningOptions.mockResolvedValue({
      date: "2026-08-31",
      meal: "Dinner",
      options: [
        {
          hall: { name: "Hill House", slug: "hill-house" },
          matching_item_count: 42,
          matching_station_count: 8,
          total_station_count: 11,
          station_coverage: 0.73,
          check_with_staff_count: 0,
          top_stations: []
        }
      ]
    });

    render(
      <MemoryRouter initialEntries={["/results?date=2026-08-31&meal=Dinner"]}>
        <Routes>
          <Route path="/results" element={<Results />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByText("Options at 8 of 11 stations")).toBeInTheDocument();
    expect(screen.queryByText(/coverage/i)).not.toBeInTheDocument();
  });

  it("renders an empty state for no matches", async () => {
    mockedGetDiningOptions.mockResolvedValue({
      date: "2026-08-31",
      meal: "Lunch",
      options: []
    });

    render(
      <MemoryRouter initialEntries={["/results?date=2026-08-31&meal=Lunch&exclude=milk"]}>
        <Routes>
          <Route path="/results" element={<Results />} />
        </Routes>
      </MemoryRouter>
    );

    expect(await screen.findByRole("heading", { name: "No dining options found" })).toBeInTheDocument();
  });
});
