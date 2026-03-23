"use client";

import type { ImageLabel } from "@/lib/image-labels";

export function ImageLabelOverlay({
  labels,
  visible,
}: {
  labels: ImageLabel[];
  visible: boolean;
}) {
  if (!visible || labels.length === 0) return null;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {labels.map((label, i) => (
        <div
          key={i}
          className="absolute flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold whitespace-nowrap"
          style={{
            left: `${label.x * 100}%`,
            top: `${label.y * 100}%`,
            transform: "translate(-50%, -50%)",
            backgroundColor: "rgba(0,0,0,0.7)",
            border: `1px solid ${label.color}`,
            color: label.color,
            lineHeight: 1.2,
            maxWidth: "30%",
            overflow: "hidden",
            textOverflow: "ellipsis",
          }}
        >
          <span
            className="w-1.5 h-1.5 rounded-full shrink-0"
            style={{ backgroundColor: label.color }}
          />
          <span className="truncate">{label.text}</span>
        </div>
      ))}
    </div>
  );
}
