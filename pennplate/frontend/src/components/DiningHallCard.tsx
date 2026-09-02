import { ArrowRight, AlertCircle, MapPin } from "lucide-react";
import { Link } from "react-router-dom";
import type { DiningOption, FilterState } from "../types/api";
import { filtersToSearch, formatStationName } from "../utils/filters";

interface DiningHallCardProps {
  option: DiningOption;
  filters: FilterState;
}

export default function DiningHallCard({ option, filters }: DiningHallCardProps) {
  return (
    <article className="slide-up flex h-full flex-col rounded-lg border border-neutral bg-card p-5 shadow-soft transition hover:border-cranberry/35">
      <div className="mb-4 flex items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-black leading-tight">{option.hall.name}</h2>
          <p className="mt-1 flex items-center gap-1 text-sm text-ink/55">
            <MapPin aria-hidden="true" size={15} />
            Penn Dining hall
          </p>
        </div>
        <div className="rounded-md bg-cranberry px-3 py-2 text-right text-white">
          <div className="text-2xl font-black leading-none">{option.matching_item_count}</div>
          <div className="text-xs font-bold">matches</div>
        </div>
      </div>

      <p className="mb-5 text-sm font-bold text-ink/70">
        Options at {option.matching_station_count} of {option.total_station_count} stations
      </p>

      <div className="mb-5 grow">
        <h3 className="mb-2 text-sm font-black uppercase tracking-wide text-ink/50">Top stations</h3>
        {option.top_stations.length > 0 ? (
          <div className="space-y-2">
            {option.top_stations.map((station) => (
              <div key={station.name} className="flex items-center justify-between rounded-md bg-oat px-3 py-2 text-sm">
                <span className="font-bold">{formatStationName(station.name)}</span>
                <span className="text-ink/60">{station.matching_item_count}</span>
              </div>
            ))}
          </div>
        ) : (
          <p className="rounded-md bg-oat px-3 py-2 text-sm text-ink/55">No matching stations.</p>
        )}
      </div>

      {option.check_with_staff_count > 0 && (
        <p className="mb-4 flex items-center gap-2 rounded-md bg-oat px-3 py-2 text-sm font-bold text-ink/70">
          <AlertCircle aria-hidden="true" size={16} />
          {option.check_with_staff_count} items need staff confirmation
        </p>
      )}

      <Link
        to={`/hall/${option.hall.slug}?${filtersToSearch(filters)}`}
        className="inline-flex min-h-11 items-center justify-center gap-2 rounded-md bg-cranberry px-4 py-2 font-bold text-white transition hover:bg-ink focus:outline-none focus:ring-2 focus:ring-cranberry/35"
      >
        View Menu
        <ArrowRight aria-hidden="true" size={17} />
      </Link>
    </article>
  );
}
