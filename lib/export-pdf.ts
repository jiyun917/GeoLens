import jsPDF from "jspdf";
import type { CapturedScreen } from "@/app/providers/ReportProvider";
import type { ImageLabel } from "./image-labels";

const PAGE_W = 210; // A4 width mm
const PAGE_H = 297; // A4 height mm
const MARGIN = 15;
const CONTENT_W = PAGE_W - MARGIN * 2;

function renderLabeledImage(
  imageDataUrl: string,
  labels: ImageLabel[]
): Promise<string> {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      const ctx = canvas.getContext("2d")!;
      ctx.drawImage(img, 0, 0);

      const fs = Math.max(14, Math.min(img.width * 0.016, 28));
      for (const label of labels) {
        const px = label.x * img.width;
        const py = label.y * img.height;
        ctx.font = `bold ${fs}px sans-serif`;
        const m = ctx.measureText(label.text);
        const dotR = Math.round(fs * 0.2);
        const pad = Math.round(fs * 0.4);
        const bw = dotR * 2 + 4 + m.width + pad * 2;
        const bh = fs + pad * 2;
        const bx = px - bw / 2;
        const by = py - bh / 2;
        ctx.fillStyle = "rgba(0,0,0,0.7)";
        ctx.beginPath();
        ctx.roundRect(bx, by, bw, bh, 3);
        ctx.fill();
        ctx.strokeStyle = label.color;
        ctx.lineWidth = 1.5;
        ctx.stroke();
        ctx.fillStyle = label.color;
        ctx.beginPath();
        ctx.arc(bx + pad + dotR, py, dotR, 0, Math.PI * 2);
        ctx.fill();
        ctx.textAlign = "left";
        ctx.textBaseline = "middle";
        ctx.fillStyle = label.color;
        ctx.fillText(label.text, bx + pad + dotR * 2 + 4, py);
      }
      resolve(canvas.toDataURL("image/jpeg", 0.92));
    };
    img.src = imageDataUrl;
  });
}

export async function exportReportAsPdf(
  topic: string,
  captures: CapturedScreen[],
  reportContent: string,
  showLabels: boolean,
  imageLabels?: ImageLabel[]
): Promise<void> {
  const doc = new jsPDF({ unit: "mm", format: "a4", orientation: "portrait" });
  let y = MARGIN;

  const checkPage = (needed: number) => {
    if (y + needed > PAGE_H - MARGIN) {
      doc.addPage();
      y = MARGIN;
    }
  };

  // Title
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  const titleLines = doc.splitTextToSize(topic, CONTENT_W);
  checkPage(titleLines.length * 7 + 5);
  doc.text(titleLines, MARGIN, y);
  y += titleLines.length * 7 + 2;

  // Date
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(130);
  doc.text(`GeoLens Interpretation Report · ${new Date().toLocaleDateString("ko-KR")}`, MARGIN, y);
  doc.setTextColor(0);
  y += 8;

  // Images
  const hasLabels = showLabels && imageLabels && imageLabels.length > 0;
  for (let i = 0; i < captures.length; i++) {
    const imgSrc = hasLabels
      ? await renderLabeledImage(captures[i].image, imageLabels!)
      : captures[i].image;

    // Load image to get dimensions
    const img = await new Promise<HTMLImageElement>((resolve) => {
      const el = new Image();
      el.onload = () => resolve(el);
      el.src = imgSrc;
    });

    const imgW = CONTENT_W;
    const imgH = (img.height / img.width) * imgW;
    const cappedH = Math.min(imgH, PAGE_H - MARGIN * 2 - 15);

    checkPage(cappedH + 12);

    try {
      doc.addImage(imgSrc, "JPEG", MARGIN, y, imgW, cappedH);
    } catch {
      // fallback if JPEG fails
      doc.addImage(imgSrc, "PNG", MARGIN, y, imgW, cappedH);
    }
    y += cappedH + 2;

    // Caption
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8);
    doc.setTextColor(100);
    const caption = `Capture ${i + 1}: ${captures[i].description}${hasLabels ? " (with structural labels)" : ""}`;
    doc.text(caption, MARGIN, y + 3);
    doc.setTextColor(0);
    y += 8;
  }

  // Report text
  const lines = reportContent.split("\n");
  for (const line of lines) {
    const trimmed = line.trim();
    if (!trimmed) {
      y += 2;
      continue;
    }

    // Strip confidence tags
    const clean = trimmed
      .replace(/\[신뢰도:\s*(높음|중간|낮음)\]\s*$/, "")
      .replace(/\[Confidence:\s*(High|Medium|Low)\]\s*$/i, "")
      .replace(/```structures[\s\S]*?```/g, "")
      .trim();

    if (!clean) continue;

    if (clean.startsWith("## ")) {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(13);
      const heading = clean.slice(3);
      const hLines = doc.splitTextToSize(heading, CONTENT_W);
      checkPage(hLines.length * 5.5 + 4);
      y += 3;
      doc.text(hLines, MARGIN, y);
      y += hLines.length * 5.5 + 2;
    } else if (clean.startsWith("### ")) {
      doc.setFont("helvetica", "bold");
      doc.setFontSize(11);
      const heading = clean.slice(4);
      const hLines = doc.splitTextToSize(heading, CONTENT_W);
      checkPage(hLines.length * 4.5 + 3);
      y += 2;
      doc.text(hLines, MARGIN, y);
      y += hLines.length * 4.5 + 2;
    } else if (clean.match(/^[-*]\s/)) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const text = clean.replace(/^[-*]\s/, "").replace(/\*\*(.*?)\*\*/g, "$1");
      const bLines = doc.splitTextToSize(`• ${text}`, CONTENT_W - 5);
      checkPage(bLines.length * 4.2 + 1);
      doc.text(bLines, MARGIN + 3, y);
      y += bLines.length * 4.2 + 1;
    } else if (clean.match(/^\d+\.\s/)) {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const text = clean.replace(/\*\*(.*?)\*\*/g, "$1");
      const nLines = doc.splitTextToSize(text, CONTENT_W - 5);
      checkPage(nLines.length * 4.2 + 1);
      doc.text(nLines, MARGIN + 3, y);
      y += nLines.length * 4.2 + 1;
    } else {
      doc.setFont("helvetica", "normal");
      doc.setFontSize(10);
      const text = clean.replace(/\*\*(.*?)\*\*/g, "$1");
      const pLines = doc.splitTextToSize(text, CONTENT_W);
      checkPage(pLines.length * 4.2 + 1);
      doc.text(pLines, MARGIN, y);
      y += pLines.length * 4.2 + 1.5;
    }
  }

  doc.save(`GeoLens_Report_${new Date().toISOString().slice(0, 10)}.pdf`);
}
