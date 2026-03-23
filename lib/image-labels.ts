export interface ImageLabel {
  text: string;
  x: number;
  y: number;
  color: string;
  type: string;
}

const GRID_POSITIONS: Record<string, { x: number; y: number }> = {
  "top-left":      { x: 0.15, y: 0.10 },
  "top-center":    { x: 0.50, y: 0.10 },
  "top-right":     { x: 0.85, y: 0.10 },
  "mid-left":      { x: 0.12, y: 0.50 },
  "mid-center":    { x: 0.50, y: 0.50 },
  "mid-right":     { x: 0.88, y: 0.50 },
  "bottom-left":   { x: 0.15, y: 0.88 },
  "bottom-center": { x: 0.50, y: 0.88 },
  "bottom-right":  { x: 0.85, y: 0.88 },
};

const TYPE_COLORS: Record<string, string> = {
  salt_diapir:       "#4ade80",
  normal_fault:      "#f87171",
  reverse_fault:     "#f87171",
  strike_slip_fault: "#f87171",
  unconformity:      "#fbbf24",
  anticline:         "#60a5fa",
  syncline:          "#60a5fa",
  growth_strata:     "#22d3ee",
  horizon:           "#60a5fa",
  amplitude_anomaly: "#c084fc",
  channel:           "#22d3ee",
  delta:             "#22d3ee",
  reef:              "#4ade80",
};

export function structuresToLabels(structures: { type: string; label: string; position: string }[]): ImageLabel[] {
  const regionCount: Record<string, number> = {};
  const regionIndex: Record<string, number> = {};

  for (const s of structures) {
    regionCount[s.position] = (regionCount[s.position] || 0) + 1;
  }

  const labels: ImageLabel[] = [];

  for (const s of structures) {
    const base = GRID_POSITIONS[s.position];
    if (!base) continue;

    const count = regionCount[s.position] || 1;
    const idx = regionIndex[s.position] || 0;
    regionIndex[s.position] = idx + 1;

    // Spread stacked labels with 10% vertical spacing + zigzag horizontal
    const spacing = 0.10;
    const totalH = (count - 1) * spacing;
    const yOff = -totalH / 2 + idx * spacing;
    const xOff = count > 1 ? (idx % 2 === 0 ? -0.04 : 0.04) : 0;

    labels.push({
      text: s.label,
      x: Math.max(0.08, Math.min(0.92, base.x + xOff)),
      y: Math.max(0.05, Math.min(0.95, base.y + yOff)),
      color: TYPE_COLORS[s.type] || "#94a3b8",
      type: s.type,
    });
  }

  return labels;
}
