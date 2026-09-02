import type { SortMode } from "../types/api";
import { sortOptions } from "../utils/filters";

interface SortControlProps {
  value: SortMode;
  onChange: (sort: SortMode) => void;
}

export default function SortControl({ value, onChange }: SortControlProps) {
  return (
    <label className="flex items-center gap-2 text-sm font-bold text-ink/70">
      Sort
      <select
        value={value}
        onChange={(event) => onChange(event.target.value as SortMode)}
        className="min-h-10 rounded-md border border-neutral bg-card px-3 py-2 text-sm font-bold text-ink shadow-soft focus:outline-none focus:ring-2 focus:ring-cranberry/30"
      >
        {sortOptions.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}
