import type { StationGroup } from "../types/api";
import { formatStationName } from "../utils/filters";
import MenuItemCard from "./MenuItemCard";

interface StationSectionProps {
  station: StationGroup;
}

export default function StationSection({ station }: StationSectionProps) {
  return (
    <section className="fade-in">
      <div className="section-rule mb-4 flex items-center justify-between gap-4 border-b pb-3">
        <h2 className="text-xl font-black uppercase leading-none tracking-wide sm:text-2xl">{formatStationName(station.name)}</h2>
        <span className="station-count rounded-md px-3 py-2 text-xs font-bold leading-none">
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
