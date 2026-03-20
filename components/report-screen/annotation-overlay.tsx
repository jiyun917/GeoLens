"use client";

import type { GeoAnnotation } from "@/lib/ai";

const FEATURE_COLORS: Record<string, string> = {
  fault: "#ef4444",
  horizon: "#3b82f6",
  unconformity: "#f59e0b",
  anomaly: "#a855f7",
  stratigraphic_boundary: "#22c55e",
  fold: "#ec4899",
  intrusion: "#f97316",
  contact: "#14b8a6",
  fracture_zone: "#ef4444",
  amplitude_anomaly: "#a855f7",
  velocity_anomaly: "#8b5cf6",
  well_marker: "#06b6d4",
  formation_top: "#22c55e",
  log_anomaly: "#f59e0b",
};

function getColor(featureType: string) {
  return FEATURE_COLORS[featureType] || "#6b7280";
}

/** Convert points to a smooth Catmull-Rom spline SVG path */
function toSmoothPath(pts: Array<{ x: number; y: number }>): string {
  if (pts.length < 2) return "";
  const s = (p: { x: number; y: number }) => ({ x: p.x * 1000, y: p.y * 1000 });

  if (pts.length === 2) {
    const a = s(pts[0]), b = s(pts[1]);
    return `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
  }

  const scaled = pts.map(s);
  let d = `M ${scaled[0].x} ${scaled[0].y}`;

  for (let i = 0; i < scaled.length - 1; i++) {
    const p0 = scaled[Math.max(i - 1, 0)];
    const p1 = scaled[i];
    const p2 = scaled[i + 1];
    const p3 = scaled[Math.min(i + 2, scaled.length - 1)];

    const cp1x = p1.x + (p2.x - p0.x) / 6;
    const cp1y = p1.y + (p2.y - p0.y) / 6;
    const cp2x = p2.x - (p3.x - p1.x) / 6;
    const cp2y = p2.y - (p3.y - p1.y) / 6;

    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`;
  }

  return d;
}

export function AnnotationOverlay({
  annotations,
  visible,
  compact = false,
}: {
  annotations?: GeoAnnotation[];
  visible: boolean;
  compact?: boolean;
}) {
  if (!visible || !annotations?.length) return null;

  const sw = compact ? 1.5 : 2;

  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      <svg
        className="absolute inset-0 w-full h-full"
        viewBox="0 0 1000 1000"
        preserveAspectRatio="none"
      >
        {annotations.map((a) => {
          const color = getColor(a.feature_type);

          if (a.geometry.type === "line" && a.geometry.points?.length) {
            const pts = a.geometry.points;
            const pathD = toSmoothPath(pts);
            const mid = pts[Math.floor(pts.length / 2)];
            return (
              <g key={a.id}>
                <path
                  d={pathD}
                  stroke={color}
                  strokeWidth={sw}
                  fill="none"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  vectorEffect="non-scaling-stroke"
                />
                {!compact && (
                  <text
                    x={mid.x * 1000}
                    y={mid.y * 1000 - 6}
                    fill={color}
                    fontSize="28"
                    fontWeight="bold"
                    textAnchor="middle"
                    paintOrder="stroke"
                    stroke="rgba(0,0,0,0.7)"
                    strokeWidth="8"
                  >
                    {a.label}
                  </text>
                )}
              </g>
            );
          }

          if (a.geometry.type === "bbox") {
            const { x = 0, y = 0, width = 0, height = 0 } = a.geometry;
            return (
              <g key={a.id}>
                <rect
                  x={x * 1000}
                  y={y * 1000}
                  width={width * 1000}
                  height={height * 1000}
                  stroke={color}
                  strokeWidth={sw}
                  fill={color}
                  fillOpacity={0.1}
                  vectorEffect="non-scaling-stroke"
                />
                {!compact && (
                  <text
                    x={x * 1000 + 4}
                    y={y * 1000 - 4}
                    fill={color}
                    fontSize="24"
                    fontWeight="bold"
                    paintOrder="stroke"
                    stroke="rgba(0,0,0,0.7)"
                    strokeWidth="6"
                  >
                    {a.label}
                  </text>
                )}
              </g>
            );
          }

          if (a.geometry.type === "point") {
            const { x = 0, y = 0 } = a.geometry;
            return (
              <g key={a.id}>
                <circle
                  cx={x * 1000}
                  cy={y * 1000}
                  r={compact ? 10 : 15}
                  stroke={color}
                  strokeWidth={sw}
                  fill={color}
                  fillOpacity={0.3}
                  vectorEffect="non-scaling-stroke"
                />
                {!compact && (
                  <text
                    x={x * 1000 + 20}
                    y={y * 1000 + 6}
                    fill={color}
                    fontSize="24"
                    fontWeight="bold"
                    paintOrder="stroke"
                    stroke="rgba(0,0,0,0.7)"
                    strokeWidth="6"
                  >
                    {a.label}
                  </text>
                )}
              </g>
            );
          }

          return null;
        })}
      </svg>
    </div>
  );
}
