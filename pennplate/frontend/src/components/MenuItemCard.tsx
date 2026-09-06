import type { MenuItem } from "../types/api";
import { allergens as allergenLabels } from "../utils/filters";

interface MenuItemCardProps {
  item: MenuItem;
}

export default function MenuItemCard({ item }: MenuItemCardProps) {
  return (
    <article className="rounded-lg border border-neutral bg-card p-5 shadow-soft">
      <div className="flex min-h-16 flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-xl font-black leading-tight">{item.name}</h3>
          {item.description && <p className="mt-1 text-sm leading-6 text-ink/65">{item.description}</p>}
        </div>
        {item.calories !== null && <span className="shrink-0 self-end text-sm font-semibold text-ink/55">{item.calories} cal</span>}
      </div>
      <div className="mt-3 flex flex-wrap gap-2">
        {item.vegan && <Badge tone="green">Vegan</Badge>}
        {item.vegetarian && <Badge tone="green">Vegetarian</Badge>}
        {item.allergens.map((allergen) => (
          <Badge key={allergen} tone="amber">
            {allergenLabels.find((label) => label.value === allergen)?.label || allergen}
          </Badge>
        ))}
        {item.info_unavailable && <Badge tone="gray">Info unavailable</Badge>}
      </div>
    </article>
  );
}

function Badge({ children, tone }: { children: string; tone: "green" | "amber" | "gray" }) {
  const styles = {
    green: "bg-[#F8D7DF] text-cranberry",
    amber: "bg-neutral text-ink/70",
    gray: "bg-ink/10 text-ink/60"
  };
  return <span className={`rounded px-3 py-1.5 text-sm font-bold leading-none ${styles[tone]}`}>{children}</span>;
}
