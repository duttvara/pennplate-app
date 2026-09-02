import { useEffect, useState } from "react";
import { Link, useLocation, useParams } from "react-router-dom";
import { ArrowLeft, AlertCircle } from "lucide-react";
import EmptyState from "../components/EmptyState";
import { CardSkeleton } from "../components/LoadingSkeleton";
import MenuItemCard from "../components/MenuItemCard";
import StationSection from "../components/StationSection";
import { getMenu } from "../services/api";
import type { MenuResponse } from "../types/api";
import { filterLabelParts, filtersFromSearch } from "../utils/filters";

export default function DiningHall() {
  const { hallSlug = "" } = useParams();
  const location = useLocation();
  const filters = filtersFromSearch(location.search);
  const [data, setData] = useState<MenuResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    getMenu(hallSlug, filters)
      .then(setData)
      .catch(() => setError("Couldn't load this menu. Try again."))
      .finally(() => setLoading(false));
  }, [hallSlug, location.search]);

  return (
    <div className="mx-auto max-w-5xl px-4 py-8 sm:px-6">
      <Link to={`/results${location.search}`} className="mb-7 inline-flex items-center gap-3 text-xl font-black text-cranberry hover:text-ink">
        <ArrowLeft aria-hidden="true" size={23} strokeWidth={2.5} />
        Back to results
      </Link>

      {loading && (
        <div className="grid gap-4">
          <CardSkeleton />
          <CardSkeleton />
        </div>
      )}

      {error && <EmptyState title="Menu unavailable" message={error} showHomeLink />}

      {!loading && !error && data && (
        <div className="fade-in">
          <section className="mb-8 rounded-lg border border-neutral bg-card p-6 shadow-soft">
            <p className="text-sm font-black uppercase tracking-wide text-cranberry">{data.meal}</p>
            <h1 className="mt-3 text-4xl font-black leading-none tracking-normal sm:text-5xl">{data.hall.name}</h1>
            <div className="mt-7 grid gap-4 sm:grid-cols-2">
              <Metric label="Matching dishes" value={data.summary.matching_item_count} />
              <Metric
                label="Stations with options"
                value={`${data.summary.matching_station_count} of ${data.summary.total_station_count}`}
              />
            </div>
            <div className="mt-7 flex max-w-full flex-wrap gap-3 overflow-hidden">
              {filterLabelParts(filters).map((part) => (
                <span
                  key={part}
                  className="rounded-md border border-cranberry/20 bg-card px-4 py-3 text-base font-bold leading-none text-ink/75 shadow-soft"
                >
                  {part}
                </span>
              ))}
            </div>
          </section>

          {data.stations.length === 0 ? (
            <EmptyState title="No matching menu items found" message="Try changing your meal, diet, or allergen filters." showHomeLink />
          ) : (
            <div className="grid gap-8">
              {data.stations.map((station) => (
                <StationSection key={station.name} station={station} />
              ))}
            </div>
          )}

          {data.check_with_staff.length > 0 && (
            <section className="mt-10 rounded-lg border border-neutral bg-oat p-5">
              <div className="mb-4 flex items-start gap-3">
                <AlertCircle aria-hidden="true" className="mt-1 text-cranberry" size={20} />
                <div>
                  <h2 className="text-xl font-black">Check with dining staff</h2>
                  <p className="mt-1 text-sm leading-6 text-ink/65">
                    Bon Appetit does not provide complete allergen information for these items.
                  </p>
                </div>
              </div>
              <div className="grid gap-3">
                {data.check_with_staff.map((item) => (
                  <MenuItemCard key={item.id} item={item} />
                ))}
              </div>
            </section>
          )}

          <p className="mt-10 rounded-lg border border-neutral bg-card p-4 text-sm leading-6 text-ink/60">
            PennPlate uses dietary and allergen information published by Penn Dining / Bon Appetit. Menu information may change,
            and allergen filters do not guarantee absence of cross-contact. Confirm with dining staff when needed.
          </p>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="rounded-md border border-neutral bg-oat p-5">
      <div className="text-4xl font-black leading-none text-cranberry sm:text-5xl">{value}</div>
      <div className="mt-3 text-lg font-medium leading-6 text-ink/55">{label}</div>
    </div>
  );
}
