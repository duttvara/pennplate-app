import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FilterPanel from "../components/FilterPanel";
import { defaultFilters, filtersToSearch } from "../utils/filters";
import { useAuth } from "../auth/AuthContext";

export default function Home() {
  const navigate = useNavigate();
  const [filters, setFilters] = useState(defaultFilters);
  const { user, loadPreferences, savePreferences } = useAuth();
  const [preferenceStatus, setPreferenceStatus] = useState("");

  useEffect(() => {
    if (!user) return;
    loadPreferences().then((preferences) => {
      if (preferences) setFilters((current) => ({ ...current, ...preferences }));
    }).catch(() => setPreferenceStatus("Could not load saved preferences."));
  }, [user]);

  async function saveCurrentPreferences() {
    try { await savePreferences(filters); setPreferenceStatus("Preferences saved."); }
    catch (error) { setPreferenceStatus(error instanceof Error ? error.message : "Could not save preferences."); }
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-6 px-4 py-8 sm:px-6 lg:py-12">
      <section>
        <p className="mb-2 text-sm font-black uppercase tracking-wide text-cranberry">PennPlate</p>
        <h1 className="text-4xl font-black leading-tight text-ink sm:text-5xl">Dining Search</h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-ink/65">
          Pick a date, meal, and dietary filters to compare Penn dining options.
        </p>
      </section>

      <FilterPanel
        filters={filters}
        onChange={setFilters}
        onSubmit={() => navigate(`/results?${filtersToSearch(filters)}`)}
      />
      {user && <div className="flex items-center justify-between gap-3 text-sm"><button type="button" onClick={() => void saveCurrentPreferences()} className="rounded-md border border-cranberry px-4 py-2 font-bold text-cranberry hover:bg-cranberry hover:text-white">Save my preferences</button>{preferenceStatus && <span className="text-ink/65">{preferenceStatus}</span>}</div>}
    </div>
  );
}
