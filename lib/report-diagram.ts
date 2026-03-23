/**
 * Parse STRUCTURES_JSON from report markdown.
 * The VLM outputs a ```structures code block at the end of the report.
 */

const VALID_TYPES = new Set([
  "salt_diapir", "normal_fault", "reverse_fault", "strike_slip_fault",
  "unconformity", "anticline", "syncline", "growth_strata",
  "post_kinematic", "pre_kinematic", "basement", "horizon",
  "amplitude_anomaly", "channel", "delta", "reef",
]);

const VALID_POSITIONS = new Set([
  "top-left", "top-center", "top-right",
  "mid-left", "mid-center", "mid-right",
  "bottom-left", "bottom-center", "bottom-right",
]);

export interface ReportStructure {
  type: string;
  label: string;
  position: string;
}

export function parseStructuresFromReport(reportMarkdown: string): ReportStructure[] {
  // Try ```structures block first
  const match = reportMarkdown.match(/```structures\s*\n([\s\S]*?)\n```/);
  if (!match) return [];

  try {
    const raw = JSON.parse(match[1].trim());
    if (!Array.isArray(raw)) return [];
    return raw.filter(
      (s: ReportStructure) =>
        s.type && VALID_TYPES.has(s.type) &&
        s.position && VALID_POSITIONS.has(s.position) &&
        s.label &&
        !["post_kinematic", "basement"].includes(s.type)
    ).slice(0, 8);
  } catch {
    return [];
  }
}

export function stripStructuresBlock(reportMarkdown: string): string {
  return reportMarkdown.replace(/```structures\s*\n[\s\S]*?\n```/g, "").trim();
}
