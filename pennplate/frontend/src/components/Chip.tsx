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
        "min-h-10 rounded-md border px-3 py-2 text-sm font-bold transition",
        "focus:outline-none focus:ring-2 focus:ring-cranberry/35",
        selected
          ? "border-cranberry bg-cranberry text-white"
          : "border-neutral bg-card text-ink/70 hover:border-cranberry/45 hover:text-ink"
      ].join(" ")}
    >
      {children}
    </button>
  );
}
