import type { ReactNode } from "react";

interface ChipProps {
  selected?: boolean;
  children: ReactNode;
  onClick: () => void;
}

export default function Chip({ selected = false, children, onClick }: ChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        "filter-chip min-h-10 rounded-md border px-3 py-2 text-sm font-bold transition",
        selected
          ? "border-cranberry bg-cranberry text-white"
          : ""
      ].join(" ")}
      aria-pressed={selected}
    >
      {children}
    </button>
  );
}
