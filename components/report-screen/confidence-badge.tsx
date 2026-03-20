type ConfidenceLevel = "high" | "medium" | "low";

const styles: Record<ConfidenceLevel, string> = {
  high: "bg-green-500/20 text-green-400 border-green-500/30",
  medium: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  low: "bg-red-500/20 text-red-400 border-red-500/30",
};

const printStyles: Record<ConfidenceLevel, string> = {
  high: "print:bg-green-100 print:text-green-700 print:border-green-300",
  medium: "print:bg-amber-100 print:text-amber-700 print:border-amber-300",
  low: "print:bg-red-100 print:text-red-700 print:border-red-300",
};

const labels: Record<ConfidenceLevel, string> = {
  high: "높음",
  medium: "중간",
  low: "낮음",
};

export function ConfidenceBadge({ level }: { level: ConfidenceLevel }) {
  return (
    <span
      className={`inline-flex items-center ml-2 px-1.5 py-0.5 text-[10px] font-medium rounded border ${styles[level]} ${printStyles[level]}`}
    >
      {labels[level]}
    </span>
  );
}

const koRegex = /\[신뢰도:\s*(높음|중간|낮음)\]\s*$/;
const enRegex = /\[Confidence:\s*(High|Medium|Low)\]\s*$/i;

const levelMap: Record<string, ConfidenceLevel> = {
  높음: "high",
  중간: "medium",
  낮음: "low",
  high: "high",
  medium: "medium",
  low: "low",
};

export function parseConfidence(text: string): {
  text: string;
  level: ConfidenceLevel | null;
} {
  const koMatch = text.match(koRegex);
  if (koMatch) {
    return {
      text: text.replace(koRegex, "").trimEnd(),
      level: levelMap[koMatch[1]] || null,
    };
  }
  const enMatch = text.match(enRegex);
  if (enMatch) {
    return {
      text: text.replace(enRegex, "").trimEnd(),
      level: levelMap[enMatch[1].toLowerCase()] || null,
    };
  }
  return { text, level: null };
}
