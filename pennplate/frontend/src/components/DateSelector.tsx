import { CalendarDays } from "lucide-react";

interface DateSelectorProps {
  value: string;
  onChange: (date: string) => void;
}

export default function DateSelector({ value, onChange }: DateSelectorProps) {
  return (
    <label className="block">
      <span className="mb-2 block text-sm font-bold text-ink/70">Date</span>
      <span className="flex min-h-11 items-center gap-2 rounded-md border border-neutral bg-card px-3 py-2 focus-within:border-cranberry/45 focus-within:ring-2 focus-within:ring-cranberry/15">
        <CalendarDays aria-hidden="true" size={18} className="text-cranberry" />
        <input
          type="date"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          className="w-full bg-transparent text-base font-bold text-ink outline-none"
        />
      </span>
    </label>
  );
}
