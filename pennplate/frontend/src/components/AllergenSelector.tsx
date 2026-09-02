import type { Allergen } from "../types/api";
import { allergens } from "../utils/filters";
import Chip from "./Chip";

interface AllergenSelectorProps {
  value: Allergen[];
  onChange: (allergens: Allergen[]) => void;
}

export default function AllergenSelector({ value, onChange }: AllergenSelectorProps) {
  function toggle(allergen: Allergen) {
    onChange(value.includes(allergen) ? value.filter((item) => item !== allergen) : [...value, allergen]);
  }

  return (
    <div>
      <p className="mb-2 text-sm font-bold text-ink/70">Avoid</p>
      <div className="flex flex-wrap gap-2">
        {allergens.map((allergen) => (
          <Chip key={allergen.value} selected={value.includes(allergen.value)} onClick={() => toggle(allergen.value)}>
            {allergen.label}
          </Chip>
        ))}
      </div>
    </div>
  );
}
