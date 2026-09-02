import Chip from "./Chip";
import { meals } from "../utils/filters";
import type { Meal } from "../types/api";

interface MealSelectorProps {
  value: Meal;
  onChange: (meal: Meal) => void;
}

export default function MealSelector({ value, onChange }: MealSelectorProps) {
  return (
    <div>
      <p className="mb-2 text-sm font-bold text-ink/70">Meal</p>
      <div className="flex flex-wrap gap-2">
        {meals.map((meal) => (
          <Chip key={meal} selected={value === meal} onClick={() => onChange(meal)}>
            {meal}
          </Chip>
        ))}
      </div>
    </div>
  );
}
