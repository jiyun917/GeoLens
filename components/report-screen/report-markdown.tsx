import React, { memo } from "react";
import ReactMarkdown, { type Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { ConfidenceBadge, parseConfidence } from "./confidence-badge";

function extractText(children: React.ReactNode): string {
  let text = "";
  React.Children.forEach(children, (child) => {
    if (typeof child === "string") {
      text += child;
    } else if (React.isValidElement(child) && child.props?.children) {
      text += extractText(child.props.children);
    }
  });
  return text;
}

function stripConfidenceTags(children: React.ReactNode): React.ReactNode {
  return React.Children.map(children, (child) => {
    if (typeof child === "string") {
      return child
        .replace(/\[신뢰도:\s*(높음|중간|낮음)\][.\s]*/g, "")
        .replace(/\[Confidence:\s*(High|Medium|Low)\][.\s]*/gi, "")
        .trimEnd();
    }
    return child;
  });
}

const SECTION_ICONS: Record<string, string> = {
  "자료 개요": "📋", "data overview": "📋",
  "주요 관찰": "🔍", "key observations": "🔍",
  "구조 해석": "🏗️", "structural": "🏗️",
  "층서 해석": "📐", "stratigraphic": "📐",
  "지질학적 과정": "⚙️", "geological process": "⚙️",
  "종합 평가": "📊", "summary": "📊",
  "결론": "✅", "conclusions": "✅",
  "요약": "📝", "abstract": "📝",
  "자료 및 방법": "🔬", "data and methods": "🔬",
  "해석 및 논의": "💡", "interpretation": "💡",
  "교차 대비": "🔗", "cross-comparison": "🔗",
  "qc 판정": "✅", "qc verdict": "✅",
  "노이즈": "📡", "noise": "📡",
  "반사면": "📶", "reflector": "📶",
  "인공물": "⚠️", "artifacts": "⚠️",
  "권고": "💡", "recommend": "💡",
  "자료 정보": "📂", "data information": "📂",
};

function getSectionIcon(title: string): string {
  const lower = title.toLowerCase();
  for (const [key, icon] of Object.entries(SECTION_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return "📌";
}

const TEXT_SIZE = "text-[13.5px]";

const NonMemoizedReportMarkdown = ({
  children,
  showConfidence = true,
}: {
  children: string;
  showConfidence?: boolean;
}) => {
  const components: Partial<Components> = {
    li: ({ node, children: liChildren, ...props }) => {
      const fullText = extractText(liChildren);
      const { level } = parseConfidence(fullText);
      const stripped = stripConfidenceTags(liChildren);

      return (
        <li className={`py-1 ml-1 pl-1 text-white ${TEXT_SIZE} leading-relaxed`} {...props}>
          {stripped}
          {showConfidence && level && <ConfidenceBadge level={level} />}
        </li>
      );
    },
    ol: ({ node, children, ...props }) => (
      <ol className="list-decimal list-outside ml-5 my-1" {...props}>
        {children}
      </ol>
    ),
    ul: ({ node, children, ...props }) => (
      <ul className="list-disc list-outside ml-4 my-1" {...props}>
        {children}
      </ul>
    ),
    h2: ({ node, children, ...props }) => {
      const text = extractText(children);
      const icon = getSectionIcon(text);
      return (
        <h2
          className="flex items-center gap-2 text-[15px] font-bold text-blue-400 mt-5 mb-2 pb-1 border-b border-blue-400/25"
          {...props}
        >
          <span>{icon}</span>
          {children}
        </h2>
      );
    },
    h3: ({ node, children, ...props }) => (
      <h3 className={`font-semibold mt-3 mb-1 text-teal-400 ${TEXT_SIZE}`} {...props}>
        {children}
      </h3>
    ),
    p: ({ node, children: pChildren, ...props }) => {
      const fullText = extractText(pChildren);
      const { level } = parseConfidence(fullText);
      const stripped = stripConfidenceTags(pChildren);

      return (
        <p className={`mb-2 text-white break-words leading-relaxed ${TEXT_SIZE}`} {...props}>
          {stripped}
          {showConfidence && level && <ConfidenceBadge level={level} />}
        </p>
      );
    },
    strong: ({ node, children, ...props }) => (
      <span className="font-semibold text-amber-300" {...props}>
        {children}
      </span>
    ),
    hr: ({ node, ...props }) => (
      <hr className="my-4 border-gray-700/50" {...props} />
    ),
    blockquote: ({ node, children, ...props }) => (
      <blockquote className="border-l-2 border-blue-500/40 pl-3 my-2 text-gray-300 italic" {...props}>
        {children}
      </blockquote>
    ),
    table: ({ node, children, ...props }) => (
      <div className="my-2 overflow-x-auto rounded-lg border border-gray-700">
        <table className={`w-full ${TEXT_SIZE}`} {...props}>
          {children}
        </table>
      </div>
    ),
    th: ({ node, children, ...props }) => (
      <th className={`bg-gray-800 px-3 py-1.5 text-left font-semibold text-white border-b border-gray-700 ${TEXT_SIZE}`} {...props}>
        {children}
      </th>
    ),
    td: ({ node, children, ...props }) => (
      <td className={`px-3 py-1.5 text-gray-200 border-b border-gray-800 ${TEXT_SIZE}`} {...props}>
        {children}
      </td>
    ),
  };

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
      {children}
    </ReactMarkdown>
  );
};

export const ReportMarkdown = memo(
  NonMemoizedReportMarkdown,
  (prev, next) =>
    prev.children === next.children &&
    prev.showConfidence === next.showConfidence
);
