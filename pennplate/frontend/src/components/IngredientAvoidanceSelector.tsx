import type { AvoidedIngredient } from "../types/api";
import { avoidedIngredients } from "../utils/filters";
import Chip from "./Chip";

interface IngredientAvoidanceSelectorProps {
  value: AvoidedIngredient[];
  onChange: (ingredients: AvoidedIngredient[]) => void;
}

export default function IngredientAvoidanceSelector({ value, onChange }: IngredientAvoidanceSelectorProps) {
  function toggle(ingredient: AvoidedIngredient) {
    onChange(value.includes(ingredient) ? value.filter((item) => item !== ingredient) : [...value, ingredient]);
  }

  return (
    <div>
      <p className="mb-2 text-sm font-bold text-ink/70">Religious / preference</p>
      <div className="flex flex-wrap gap-2">
        {avoidedIngredients.map((ingredient) => (
          <Chip key={ingredient.value} selected={value.includes(ingredient.value)} onClick={() => toggle(ingredient.value)}>
            Avoid {ingredient.label}
          </Chip>
        ))}
      </div>
      <p className="mt-2 text-xs font-semibold leading-5 text-ink/50">
        Screens item names, descriptions, and station labels only.
      </p>
    </div>
  );
}
