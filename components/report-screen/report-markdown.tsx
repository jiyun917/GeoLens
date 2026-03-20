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

      // Always strip the tag text from rendered children
      const stripped = level
        ? React.Children.map(liChildren, (child) => {
            if (typeof child === "string") {
              return child
                .replace(/\[신뢰도:\s*(높음|중간|낮음)\]\s*$/, "")
                .replace(/\[Confidence:\s*(High|Medium|Low)\]\s*$/i, "")
                .trimEnd();
            }
            return child;
          })
        : liChildren;

      return (
        <li className="py-1 ml-1 pl-2" {...props}>
          {stripped}
          {showConfidence && level && <ConfidenceBadge level={level} />}
        </li>
      );
    },
    ol: ({ node, children, ...props }) => (
      <ol className="list-decimal list-outside ml-4" {...props}>
        {children}
      </ol>
    ),
    ul: ({ node, children, ...props }) => (
      <ul className="list-disc list-outside ml-4" {...props}>
        {children}
      </ul>
    ),
    h2: ({ node, children, ...props }) => (
      <h2 className="text-lg font-semibold mt-4 mb-2" {...props}>
        {children}
      </h2>
    ),
    h3: ({ node, children, ...props }) => (
      <h3 className="text-base font-semibold mt-3 mb-1" {...props}>
        {children}
      </h3>
    ),
    p: ({ node, children, ...props }) => (
      <p className="mb-2 break-words" {...props}>
        {children}
      </p>
    ),
    strong: ({ node, children, ...props }) => (
      <span className="font-semibold" {...props}>
        {children}
      </span>
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
