import { Search } from "lucide-react";
import type { FilterState, Meal } from "../types/api";
import AllergenSelector from "./AllergenSelector";
import DateSelector from "./DateSelector";
import DietarySelector from "./DietarySelector";
import IngredientAvoidanceSelector from "./IngredientAvoidanceSelector";
import MealSelector from "./MealSelector";

interface FilterPanelProps {
  filters: FilterState;
  onChange: (filters: FilterState) => void;
  onSubmit: () => void;
  compact?: boolean;
}

export default function FilterPanel({ filters, onChange, onSubmit, compact = false }: FilterPanelProps) {
  return (
    <section className={["panel p-4 sm:p-6", compact ? "" : "slide-up"].join(" ")}>
      <div className="grid gap-6">
        <DateSelector value={filters.date} onChange={(date) => onChange({ ...filters, date })} />
        <MealSelector value={filters.meal} onChange={(meal: Meal) => onChange({ ...filters, meal })} />
        <DietarySelector
          vegetarian={filters.vegetarian}
          vegan={filters.vegan}
          onChange={(next) => onChange({ ...filters, ...next })}
        />
        <IngredientAvoidanceSelector value={filters.avoid} onChange={(avoid) => onChange({ ...filters, avoid })} />
        <AllergenSelector value={filters.exclude} onChange={(exclude) => onChange({ ...filters, exclude })} />
        <button
          type="button"
          onClick={onSubmit}
          className="primary-action inline-flex min-h-12 items-center justify-center gap-2 rounded-md px-5 py-3 text-base font-bold text-white transition hover:bg-ink"
        >
          <Search aria-hidden="true" size={18} />
          Find My Options
        </button>
      </div>
    </section>
  );
}
