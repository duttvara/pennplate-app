import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import DiningHallCard from "../components/DiningHallCard";
import EmptyState from "../components/EmptyState";
import { ResultsSkeleton } from "../components/LoadingSkeleton";
import SortControl from "../components/SortControl";
import { getDiningOptions } from "../services/api";
import type { DiningOptionsResponse, SortMode } from "../types/api";
import { filterLabelParts, filtersFromSearch, filtersToSearch } from "../utils/filters";

export default function Results() {
  const location = useLocation();
  const navigate = useNavigate();
  const filters = filtersFromSearch(location.search);
  const params = new URLSearchParams(location.search);
  const [sort, setSort] = useState<SortMode>((params.get("sort") as SortMode) || "items");
  const [data, setData] = useState<DiningOptionsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    getDiningOptions(filters, sort)
      .then(setData)
      .catch(() => setError("Couldn't load dining options. Try again."))
      .finally(() => setLoading(false));
  }, [location.search, sort]);

  function updateSort(nextSort: SortMode) {
    setSort(nextSort);
    navigate(`/results?${filtersToSearch(filters, { sort: nextSort })}`, { replace: true });
  }

  return (
    <div className="page-wrap mx-auto max-w-6xl px-4 py-9 sm:px-6 lg:py-12">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <Link to="/" className="mb-4 inline-flex items-center gap-2 text-sm font-bold text-cranberry hover:text-ink">
            <ArrowLeft aria-hidden="true" size={16} />
            Change filters
          </Link>
          <h1 className="display-title text-3xl font-black leading-none sm:text-4xl">Dining hall comparison</h1>
          <div className="mt-3 flex flex-wrap gap-2">
            {filterLabelParts(filters).map((part) => (
              <span
                key={part}
                className="result-chip rounded-md px-3 py-2 text-sm font-bold leading-none"
              >
                {part}
              </span>
            ))}
          </div>
        </div>
        <SortControl value={sort} onChange={updateSort} />
      </div>

      {loading && <ResultsSkeleton />}
      {error && <EmptyState title="Couldn't load dining options" message={error} showHomeLink />}
      {!loading && !error && data?.options.length === 0 && (
        <EmptyState title="No dining options found" message="No matching menu items found for these filters." showHomeLink />
      )}
      {!loading && !error && data && data.options.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {data.options.map((option) => (
            <DiningHallCard key={option.hall.slug} option={option} filters={filters} />
          ))}
        </div>
      )}
    </div>
  );
}
