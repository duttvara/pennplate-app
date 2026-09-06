import type { StationGroup } from "../types/api";
import { formatStationName } from "../utils/filters";
import MenuItemCard from "./MenuItemCard";

interface StationSectionProps {
  station: StationGroup;
}

export default function StationSection({ station }: StationSectionProps) {
  return (
    <section className="fade-in">
      <div className="mb-4 flex items-center justify-between gap-4 border-b border-neutral pb-3">
        <h2 className="text-2xl font-black uppercase leading-none">{formatStationName(station.name)}</h2>
        <span className="rounded-md bg-ink px-3 py-2 text-sm font-bold leading-none text-white">
          {station.matching_item_count} items
        </span>
      </div>
      <div className="grid gap-3">
        {station.items.map((item) => (
          <MenuItemCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  );
}
