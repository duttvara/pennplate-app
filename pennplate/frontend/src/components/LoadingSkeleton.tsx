export function CardSkeleton() {
  return (
    <div className="rounded-lg border border-neutral bg-card p-5 shadow-soft">
      <div className="skeleton mb-4 h-7 w-2/3 rounded" />
      <div className="skeleton mb-5 h-4 w-1/2 rounded" />
      <div className="space-y-2">
        <div className="skeleton h-10 rounded" />
        <div className="skeleton h-10 rounded" />
        <div className="skeleton h-10 rounded" />
      </div>
    </div>
  );
}

export function ResultsSkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      <CardSkeleton />
      <CardSkeleton />
      <CardSkeleton />
    </div>
  );
}
