import Chip from "./Chip";

interface DietarySelectorProps {
  vegetarian: boolean;
  vegan: boolean;
  onChange: (value: { vegetarian: boolean; vegan: boolean }) => void;
}

export default function DietarySelector({ vegetarian, vegan, onChange }: DietarySelectorProps) {
  return (
    <div>
      <p className="mb-2 text-sm font-bold text-ink/70">Diet</p>
      <div className="flex flex-wrap gap-2">
        <Chip selected={vegetarian} onClick={() => onChange({ vegetarian: !vegetarian, vegan })}>
          Vegetarian
        </Chip>
        <Chip selected={vegan} onClick={() => onChange({ vegetarian, vegan: !vegan })}>
          Vegan
        </Chip>
      </div>
    </div>
  );
}
