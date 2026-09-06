import type { MenuItem } from "../types/api";
import { allergens as allergenLabels } from "../utils/filters";

interface MenuItemCardProps {
  item: MenuItem;
}

export default function MenuItemCard({ item }: MenuItemCardProps) {
  return (
    <article className="menu-item p-4 sm:p-5">
      <div className="flex min-h-16 flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-xl font-black leading-tight">{item.name}</h3>
          {item.description && <p className="muted-copy mt-1 text-sm leading-6">{item.description}</p>}
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
    green: "badge-vegan",
    amber: "badge-allergen",
    gray: "badge-unavailable"
  };
  return <span className={`rounded px-3 py-1.5 text-sm font-bold leading-none ${styles[tone]}`}>{children}</span>;
}
