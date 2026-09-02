import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter, Route, Routes, useLocation } from "react-router-dom";
import { describe, expect, it } from "vitest";
import Home from "./Home";
import { AuthProvider } from "../auth/AuthContext";

function LocationProbe() {
  const location = useLocation();
  return <div data-testid="location">{location.pathname + location.search}</div>;
}

describe("Home", () => {
  it("preserves a Dinner meal selection when navigating to results", async () => {
    const user = userEvent.setup();

    render(
      <AuthProvider><MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter></AuthProvider>
    );

    await user.click(screen.getByRole("button", { name: "Dinner" }));
    await user.click(screen.getByRole("button", { name: "Find My Options" }));

    expect(screen.getByTestId("location")).toHaveTextContent("/results?date=2026-08-31&meal=Dinner");
  });

  it("preserves avoided ingredient selections when navigating to results", async () => {
    const user = userEvent.setup();

    render(
      <AuthProvider><MemoryRouter initialEntries={["/"]}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<LocationProbe />} />
        </Routes>
      </MemoryRouter></AuthProvider>
    );

    await user.click(screen.getByRole("button", { name: "Avoid Pork" }));
    await user.click(screen.getByRole("button", { name: "Find My Options" }));

    expect(screen.getByTestId("location")).toHaveTextContent("/results?date=2026-08-31&meal=Lunch&avoid=pork");
  });
});
