"use client";

import { useManuals } from "@/app/providers/ManualProvider";

export const ManualStatus = () => {
  const { manuals } = useManuals();

  const processingCount = manuals.filter(
    (m) => m.status === "processing"
  ).length;

  if (processingCount === 0) return null;

  return (
    <div className="flex items-center gap-2 text-sm text-amber-600">
      <div className="w-4 h-4 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
      <span>
        Processing {processingCount} manual{processingCount > 1 ? "s" : ""}...
      </span>
    </div>
  );
};
