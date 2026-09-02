import { Link } from "react-router-dom";

interface EmptyStateProps {
  title: string;
  message: string;
  showHomeLink?: boolean;
}

export default function EmptyState({ title, message, showHomeLink = false }: EmptyStateProps) {
  return (
    <div className="rounded-lg border border-dashed border-neutral bg-card p-8 text-center">
      <h2 className="text-xl font-black">{title}</h2>
      <p className="mx-auto mt-2 max-w-md text-ink/60">{message}</p>
      {showHomeLink && (
        <Link className="mt-5 inline-flex rounded-md bg-cranberry px-4 py-2 font-bold text-white" to="/">
          Change filters
        </Link>
      )}
    </div>
  );
}
