import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import EmptyState from "./EmptyState";

describe("EmptyState", () => {
  it("renders the supplied empty message", () => {
    render(
      <MemoryRouter>
        <EmptyState title="No dining options found" message="No matching menu items found for these filters." showHomeLink />
      </MemoryRouter>
    );

    expect(screen.getByRole("heading", { name: "No dining options found" })).toBeInTheDocument();
    expect(screen.getByText("No matching menu items found for these filters.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Change filters" })).toHaveAttribute("href", "/");
  });
});
