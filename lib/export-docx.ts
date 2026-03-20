import {
  Document,
  Packer,
  Paragraph,
  TextRun,
  ImageRun,
  HeadingLevel,
  AlignmentType,
  LevelFormat,
} from "docx";
import type { GeoAnnotation } from "./ai";
import type { CapturedScreen } from "@/app/providers/ReportProvider";

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

function getColor(featureType: string): string {
  return FEATURE_COLORS[featureType] || "#6b7280";
}

function drawLabel(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  color: string
) {
  const fontSize = Math.max(12, ctx.canvas.width * 0.018);
  ctx.font = `bold ${fontSize}px sans-serif`;
  ctx.textAlign = "left";
  ctx.strokeStyle = "rgba(0,0,0,0.7)";
  ctx.lineWidth = fontSize * 0.3;
  ctx.strokeText(text, x, y);
  ctx.fillStyle = color;
  ctx.fillText(text, x, y);
  ctx.lineWidth = 2;
}

async function renderAnnotatedImage(
  imageDataUrl: string,
  annotations?: GeoAnnotation[],
  visible: boolean = true
): Promise<{ buffer: ArrayBuffer; width: number; height: number }> {
  const img = new Image();
  img.src = imageDataUrl;
  await new Promise<void>((resolve) => {
    img.onload = () => resolve();
  });

  const canvas = document.createElement("canvas");
  canvas.width = img.width;
  canvas.height = img.height;
  const ctx = canvas.getContext("2d")!;
  ctx.drawImage(img, 0, 0);

  if (visible && annotations?.length) {
    const w = canvas.width;
    const h = canvas.height;

    for (const a of annotations) {
      const color = getColor(a.feature_type);
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";

      if (a.geometry.type === "line" && a.geometry.points?.length) {
        const pts = a.geometry.points;
        const scaled = pts.map((p) => ({ x: p.x * w, y: p.y * h }));
        ctx.beginPath();
        ctx.moveTo(scaled[0].x, scaled[0].y);
        if (scaled.length === 2) {
          ctx.lineTo(scaled[1].x, scaled[1].y);
        } else {
          for (let si = 0; si < scaled.length - 1; si++) {
            const p0 = scaled[Math.max(si - 1, 0)];
            const p1 = scaled[si];
            const p2 = scaled[si + 1];
            const p3 = scaled[Math.min(si + 2, scaled.length - 1)];
            const cp1x = p1.x + (p2.x - p0.x) / 6;
            const cp1y = p1.y + (p2.y - p0.y) / 6;
            const cp2x = p2.x - (p3.x - p1.x) / 6;
            const cp2y = p2.y - (p3.y - p1.y) / 6;
            ctx.bezierCurveTo(cp1x, cp1y, cp2x, cp2y, p2.x, p2.y);
          }
        }
        ctx.stroke();
        const mid = scaled[Math.floor(scaled.length / 2)];
        drawLabel(ctx, a.label, mid.x, mid.y - 6, color);
      }

      if (a.geometry.type === "bbox") {
        const { x = 0, y = 0, width: bw = 0, height: bh = 0 } = a.geometry;
        ctx.strokeRect(x * w, y * h, bw * w, bh * h);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.1;
        ctx.fillRect(x * w, y * h, bw * w, bh * h);
        ctx.globalAlpha = 1;
        drawLabel(ctx, a.label, x * w + 4, y * h - 4, color);
      }

      if (a.geometry.type === "point") {
        const { x = 0, y = 0 } = a.geometry;
        ctx.beginPath();
        ctx.arc(x * w, y * h, 8, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.3;
        ctx.fill();
        ctx.globalAlpha = 1;
        ctx.stroke();
        drawLabel(ctx, a.label, x * w + 12, y * h + 4, color);
      }
    }
  }

  const blob = await new Promise<Blob>((resolve) => {
    canvas.toBlob((b) => resolve(b!), "image/jpeg", 0.95);
  });

  return {
    buffer: await blob.arrayBuffer(),
    width: canvas.width,
    height: canvas.height,
  };
}

function parseInlineFormatting(text: string): TextRun[] {
  const runs: TextRun[] = [];
  const regex = /\*\*(.*?)\*\*/g;
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      runs.push(new TextRun({ text: text.slice(lastIndex, match.index), size: 22 }));
    }
    runs.push(new TextRun({ text: match[1], bold: true, size: 22 }));
    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    runs.push(new TextRun({ text: text.slice(lastIndex), size: 22 }));
  }

  return runs.length > 0 ? runs : [new TextRun({ text, size: 22 })];
}

function markdownToDocxParagraphs(markdown: string): Paragraph[] {
  const paragraphs: Paragraph[] = [];
  const lines = markdown.split("\n");

  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) continue;

    const clean = trimmed
      .replace(/\[신뢰도:\s*(높음|중간|낮음)\]\s*$/, "")
      .replace(/\[Confidence:\s*(High|Medium|Low)\]\s*$/i, "")
      .trim();

    if (clean.startsWith("## ")) {
      paragraphs.push(
        new Paragraph({
          children: [new TextRun({ text: clean.slice(3), bold: true, size: 28 })],
          heading: HeadingLevel.HEADING_2,
          spacing: { before: 300, after: 120 },
        })
      );
    } else if (clean.startsWith("### ")) {
      paragraphs.push(
        new Paragraph({
          children: [new TextRun({ text: clean.slice(4), bold: true, size: 24 })],
          heading: HeadingLevel.HEADING_3,
          spacing: { before: 200, after: 80 },
        })
      );
    } else if (clean.match(/^[-*]\s/)) {
      const text = clean.replace(/^[-*]\s/, "");
      paragraphs.push(
        new Paragraph({
          children: parseInlineFormatting(text),
          bullet: { level: 0 },
          spacing: { before: 40, after: 40 },
        })
      );
    } else if (clean.match(/^\d+\.\s/)) {
      const text = clean.replace(/^\d+\.\s/, "");
      paragraphs.push(
        new Paragraph({
          children: parseInlineFormatting(text),
          numbering: { reference: "report-numbering", level: 0 },
          spacing: { before: 40, after: 40 },
        })
      );
    } else {
      paragraphs.push(
        new Paragraph({
          children: parseInlineFormatting(clean),
          spacing: { before: 80, after: 80 },
        })
      );
    }
  }

  return paragraphs;
}

export async function exportReportAsDocx(
  topic: string,
  captures: CapturedScreen[],
  reportContent: string
): Promise<void> {
  const imageResults = await Promise.all(
    captures.map((c) =>
      renderAnnotatedImage(c.image)
    )
  );

  const imageParagraphs: Paragraph[] = [];
  for (let i = 0; i < captures.length; i++) {
    const { buffer, width, height } = imageResults[i];
    const maxWidth = 550;
    const scale = Math.min(maxWidth / width, 1);
    const displayWidth = Math.round(width * scale);
    const displayHeight = Math.round(height * scale);

    imageParagraphs.push(
      new Paragraph({
        children: [
          new ImageRun({
            type: "jpg",
            data: buffer,
            transformation: { width: displayWidth, height: displayHeight },
          }),
        ],
        spacing: { before: 120, after: 40 },
      })
    );
    imageParagraphs.push(
      new Paragraph({
        children: [
          new TextRun({
            text: `Capture ${i + 1}: ${captures[i].description}`,
            size: 18,
            italics: true,
            color: "666666",
          }),
        ],
        spacing: { after: 160 },
      })
    );
  }

  const reportParagraphs = markdownToDocxParagraphs(reportContent);

  const doc = new Document({
    numbering: {
      config: [
        {
          reference: "report-numbering",
          levels: [
            {
              level: 0,
              format: LevelFormat.DECIMAL,
              text: "%1.",
              alignment: AlignmentType.START,
              style: {
                paragraph: {
                  indent: { left: 720, hanging: 360 },
                },
              },
            },
          ],
        },
      ],
    },
    sections: [
      {
        children: [
          new Paragraph({
            children: [new TextRun({ text: topic, bold: true, size: 36 })],
            heading: HeadingLevel.HEADING_1,
            spacing: { after: 80 },
          }),
          new Paragraph({
            children: [
              new TextRun({
                text: `GeoLens Interpretation Report · ${new Date().toLocaleDateString("ko-KR")}`,
                size: 18,
                color: "888888",
              }),
            ],
            spacing: { after: 300 },
          }),
          ...imageParagraphs,
          ...reportParagraphs,
        ],
      },
    ],
  });

  const blob = await Packer.toBlob(doc);
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `GeoLens_Report_${new Date().toISOString().slice(0, 10)}.docx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
