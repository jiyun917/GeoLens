"use client";

import { useManuals, Manual } from "@/app/providers/ManualProvider";
import { Button } from "@/components/ui/button";
import { X } from "@geist-ui/icons";

const TypeIcon = ({ type }: { type: Manual["type"] }) => {
  switch (type) {
    case "pdf":
      return <span className="text-red-500 text-xs font-bold">PDF</span>;
    case "url":
      return <span className="text-blue-500 text-xs font-bold">URL</span>;
    case "github":
      return <span className="text-gray-700 text-xs font-bold">GH</span>;
  }
};

const StatusBadge = ({ status }: { status: Manual["status"] }) => {
  switch (status) {
    case "processing":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-2 py-0.5 rounded-full">
          <span className="w-1.5 h-1.5 bg-amber-500 rounded-full animate-pulse" />
          Processing
        </span>
      );
    case "ready":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-green-600 bg-green-50 px-2 py-0.5 rounded-full">
          <span className="w-1.5 h-1.5 bg-green-500 rounded-full" />
          Ready
        </span>
      );
    case "error":
      return (
        <span className="inline-flex items-center gap-1 text-xs text-red-600 bg-red-50 px-2 py-0.5 rounded-full">
          Error
        </span>
      );
  }
};

export const ManualList = ({ mode }: { mode?: "guide" | "report" }) => {
  const { manuals, guideManuals, reportManuals, deleteManual } = useManuals();

  const filtered = mode === "guide" ? guideManuals : mode === "report" ? reportManuals : manuals;

  if (filtered.length === 0) return null;

  return (
    <div className="w-full space-y-2">
      {filtered.map((manual) => (
        <div
          key={manual.id}
          className="flex items-center justify-between px-3 py-2 bg-white border border-gray-200 rounded-md"
        >
          <div className="flex items-center gap-3 min-w-0">
            <TypeIcon type={manual.type} />
            <span className="text-sm truncate">{manual.name}</span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            <StatusBadge status={manual.status} />
            <button
              onClick={() => deleteManual(manual.id)}
              className="p-1 text-gray-400 hover:text-red-500 transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};
