"use client";

import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import { motion } from "framer-motion";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { CropModal } from "./crop-modal";
import { ReportMarkdown } from "./report-markdown";
import { ManualUpload } from "../manual/manual-upload";
import { ManualList } from "../manual/manual-list";
import { ManualStatus } from "../manual/manual-status";
import { exportReportAsDocx } from "@/lib/export-docx";
import { exportReportAsPdf } from "@/lib/export-pdf";
import { DATA_TYPES, type DataType } from "@/app/providers/ReportProvider";
import type { ReportContextType, CapturedScreen } from "@/app/providers/ReportProvider";
import type { ReportTemplate } from "@/lib/prompts/report";
import { ALL_SECTIONS } from "@/lib/prompts/report";
import { parseStructuresFromReport, stripStructuresBlock } from "@/lib/report-diagram";
import { structuresToLabels } from "@/lib/image-labels";
import { ImageLabelOverlay } from "./image-labels";

const PRINT_ICONS: Record<string, string> = {
  "자료 개요": "📋", "data overview": "📋",
  "주요 관찰": "🔍", "key observations": "🔍",
  "구조 해석": "🏗️", "structural": "🏗️",
  "층서 해석": "📐", "stratigraphic": "📐",
  "지질학적 과정": "⚙️", "geological process": "⚙️",
  "종합 평가": "📊", "summary": "📊",
  "결론": "✅", "conclusions": "✅",
  "요약": "📝", "abstract": "📝",
  "해석 및 논의": "💡", "interpretation": "💡",
  "권고": "💡", "recommend": "💡",
  "자료 정보": "📂", "data information": "📂",
};
function getPrintSectionIcon(title: string): string {
  const lower = title.toLowerCase();
  for (const [key, icon] of Object.entries(PRINT_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return "📌";
}

function markdownToInlineHtml(md: string): string {
  // Pre-process: split inline bullets onto separate lines
  const preprocessed = md
    .replace(/([.!?。])\s*\*\s+/g, "$1\n* ")     // "sentence. * next" → separate lines
    .replace(/([.!?。])\s*-\s+/g, "$1\n- ")       // "sentence. - next" → separate lines
    .replace(/([.!?。])\s*●\s*/g, "$1\n- ")       // "sentence. ● next" → convert ● to -
    .replace(/●\s*/g, "\n- ")                      // standalone ● → -
    .replace(/\*\s{2,}/g, "\n* ");                 // "* " with extra spaces → clean
  const lines = preprocessed.split("\n");
  let html = "";
  let inList = false;
  let listType = "";

  const closeList = () => {
    if (inList) {
      html += listType === "ul" ? "</ul>" : "</ol>";
      inList = false;
    }
  };

  const formatInline = (text: string): string => {
    return text
      .replace(/\*\*(.*?)\*\*/g, '<strong style="font-weight:600">$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>');
  };

  for (const line of lines) {
    const trimmed = line.trim();

    if (!trimmed) {
      closeList();
      continue;
    }

    // Headings: ## Title, ### Title, or standalone **Title** (bold-only heading)
    if (trimmed.match(/^#{2}\s/) || trimmed.match(/^##[^\s#]/)) {
      closeList();
      const title = trimmed.replace(/^#{2,3}\s*/, "");
      const icon = getPrintSectionIcon(title);
      const text = formatInline(title);
      html += `<h2 style="font-size:13px;font-weight:700;color:#1e40af;margin:16px 0 6px 0;padding-bottom:4px;border-bottom:1.5px solid #93c5fd">${icon} ${text}</h2>`;
      continue;
    }
    if (trimmed.match(/^#{3}\s/) || trimmed.match(/^###[^\s#]/)) {
      closeList();
      const title = trimmed.replace(/^#{2,3}\s*/, "");
      const text = formatInline(title);
      html += `<h3 style="font-size:11px;font-weight:600;color:#0d9488;margin:10px 0 4px 0">${text}</h3>`;
      continue;
    }
    // Bold-only line as section heading (e.g., **자료 개요**)
    if (trimmed.match(/^\*\*[^*]+\*\*$/) && !inList) {
      closeList();
      const title = trimmed.replace(/^\*\*|\*\*$/g, "");
      const icon = getPrintSectionIcon(title);
      html += `<h2 style="font-size:13px;font-weight:700;color:#1e40af;margin:16px 0 6px 0;padding-bottom:4px;border-bottom:1.5px solid #93c5fd">${icon} ${title}</h2>`;
      continue;
    }

    // Horizontal rule
    if (trimmed === "---" || trimmed === "***") {
      closeList();
      html += '<hr style="border:none;border-top:1px solid #d1d5db;margin:10px 0">';
      continue;
    }

    // Bullet list
    if (trimmed.match(/^[-*]\s/)) {
      if (!inList || listType !== "ul") {
        closeList();
        html += '<ul style="list-style:disc;margin:4px 0 4px 20px;padding:0">';
        inList = true;
        listType = "ul";
      }
      const text = formatInline(trimmed.replace(/^[-*]\s/, ""));
      html += `<li style="font-size:11px;color:#111;margin:3px 0;line-height:1.6">${text}</li>`;
      continue;
    }

    // Numbered list
    if (trimmed.match(/^\d+\.\s/)) {
      if (!inList || listType !== "ol") {
        closeList();
        html += '<ol style="list-style:decimal;margin:4px 0 4px 20px;padding:0">';
        inList = true;
        listType = "ol";
      }
      const text = formatInline(trimmed.replace(/^\d+\.\s/, ""));
      html += `<li style="font-size:11px;color:#111;margin:3px 0;line-height:1.6">${text}</li>`;
      continue;
    }

    // Paragraph
    closeList();
    const text = formatInline(trimmed);
    html += `<p style="font-size:11px;color:#111;margin:4px 0;line-height:1.7">${text}</p>`;
  }

  closeList();
  return html;
}

const TEMPLATES: { id: ReportTemplate; label: string; desc: string }[] = [
  { id: "detailed", label: "Exploration", desc: "6 sections, detailed" },
  { id: "academic", label: "Academic", desc: "Paper structure" },
  { id: "brief", label: "Brief", desc: "Quick summary" },
  { id: "qc", label: "Data QC", desc: "Quality control" },
];

/* ──────────────────── Section Card wrapper ──────────────────── */
function SectionCard({
  title,
  badge,
  defaultOpen = true,
  children,
}: {
  title: string;
  badge?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="border border-gray-700 rounded-2xl overflow-hidden bg-zinc-900">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-5 py-3.5 hover:bg-zinc-800 transition-colors"
      >
        <div className="flex items-center gap-2">
          <h2 className="text-sm font-semibold tracking-wide uppercase text-white">{title}</h2>
          {badge && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-blue-600/20 text-blue-400 font-medium">
              {badge}
            </span>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-gray-400 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
      {open && <div className="px-5 pb-5">{children}</div>}
    </div>
  );
}

/* ──────────────────── Main Component ──────────────────── */
interface ReportScreenProps extends ReportContextType {
  onStartOver: () => void;
}

export const ReportScreen = ({
  topic,
  captures,
  captureFullScreen,
  addCapture,
  removeCapture,
  reportContent,
  isGenerating,
  generateInterpretationReport,
  regenerateReportSection,
  regeneratingSection,
  reportLanguage,
  setReportLanguage,
  reportTemplate,
  setReportTemplate,
  customSections,
  setCustomSections,
  projectId,
  isSaving,
  saveProject,
  onStartOver,
}: ReportScreenProps) => {
  const [captureDesc, setCaptureDesc] = useState("");
  const [captureType, setCaptureType] = useState<DataType>("seismic");
  const [isCapturing, setIsCapturing] = useState(false);
  const [pendingImage, setPendingImage] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [isExportingDocx, setIsExportingDocx] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [showImageLabels, setShowImageLabels] = useState(false);
  const exportRef = useRef<HTMLDivElement>(null);
  const printRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Parse structures from report content (VLM outputs ```structures block)
  const reportStructures = useMemo(() => {
    if (!reportContent || isGenerating) return [];
    return parseStructuresFromReport(reportContent);
  }, [reportContent, isGenerating]);

  // Clean report text (strip ```structures block for display)
  const reportTextClean = useMemo(() => {
    if (!reportContent) return "";
    return stripStructuresBlock(reportContent);
  }, [reportContent]);

  // Text with confidence tags removed (for PDF/DOCX export)
  const reportTextNoConfidence = useMemo(() => {
    if (!reportTextClean) return "";
    return reportTextClean
      .replace(/\[신뢰도:\s*(높음|중간|낮음)\][.\s]*/g, "")
      .replace(/\[Confidence:\s*(High|Medium|Low)\][.\s]*/gi, "");
  }, [reportTextClean]);

  // Convert structures to image labels
  const imageLabels = useMemo(
    () => structuresToLabels(reportStructures),
    [reportStructures]
  );

  // Pre-render labeled images for PDF export (Canvas composited)
  const [labeledImages, setLabeledImages] = useState<string[]>([]);
  useEffect(() => {
    if (!showImageLabels || imageLabels.length === 0 || captures.length === 0) {
      setLabeledImages([]);
      return;
    }
    const renderAll = async () => {
      const results: string[] = [];
      for (const c of captures) {
        const img = new Image();
        img.src = c.image;
        await new Promise<void>((r) => { img.onload = () => r(); });
        const canvas = document.createElement("canvas");
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext("2d")!;
        ctx.drawImage(img, 0, 0);
        const fs = Math.max(14, Math.min(img.width * 0.016, 28));
        for (const label of imageLabels) {
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
        results.push(canvas.toDataURL("image/jpeg", 0.92));
      }
      setLabeledImages(results);
    };
    renderAll();
  }, [showImageLabels, imageLabels, captures]);

  useEffect(() => {
    if (!showExportMenu) return;
    const handleClickOutside = (e: MouseEvent) => {
      if (exportRef.current && !exportRef.current.contains(e.target as Node)) {
        setShowExportMenu(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [showExportMenu]);

  const handleCapture = async () => {
    if (isCapturing) return;
    setIsCapturing(true);
    const image = await captureFullScreen();
    if (image) setPendingImage(image);
    setIsCapturing(false);
  };

  const handleCropConfirm = (croppedImage: string) => {
    addCapture(croppedImage, captureDesc || `Capture ${captures.length + 1}`, captureType);
    setCaptureDesc("");
    setPendingImage(null);
  };

  const handleFileUpload = useCallback((files: FileList | null) => {
    if (!files) return;
    Array.from(files).forEach((file) => {
      if (!file.type.startsWith("image/")) return;
      const reader = new FileReader();
      reader.onload = (e) => {
        const dataUrl = e.target?.result as string;
        if (dataUrl) addCapture(dataUrl, file.name.replace(/\.[^.]+$/, ""), captureType);
      };
      reader.readAsDataURL(file);
    });
  }, [addCapture, captureType]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileUpload(e.dataTransfer.files);
  }, [handleFileUpload]);

  const handleCopyReport = () => { navigator.clipboard.writeText(reportContent); };

  const handleExportPdf = async () => {
    if (!printRef.current || isExporting) return;
    setIsExporting(true);
    try {
      const html2pdf = (await import("html2pdf.js")).default;

      // Clone the print div content, make it visible with white background
      const el = printRef.current!;
      const wrapper = el.parentElement!;
      wrapper.style.position = "fixed";
      wrapper.style.left = "0";
      wrapper.style.top = "0";
      wrapper.style.zIndex = "-1";
      wrapper.style.opacity = "0.01";

      await new Promise((r) => setTimeout(r, 400));
      const imgs = el.querySelectorAll("img");
      await Promise.all(Array.from(imgs).map((img) =>
        img.complete ? Promise.resolve() : new Promise<void>((r) => { img.onload = () => r(); img.onerror = () => r(); })
      ));

      // Inject page-break-inside:avoid on all child elements
      const allElements = el.querySelectorAll("h2, h3, li, p, div, img");
      allElements.forEach((child) => {
        (child as HTMLElement).style.pageBreakInside = "avoid";
        (child as HTMLElement).style.breakInside = "avoid";
      });

      await html2pdf().set({
        margin: [12, 12, 12, 12],
        filename: `GeoLens_Report_${new Date().toISOString().slice(0, 10)}.pdf`,
        image: { type: "jpeg", quality: 0.92 },
        html2canvas: { scale: 2, useCORS: true, logging: false, scrollY: 0 },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
        pagebreak: { mode: ["css"] } as any,
      }).from(el).save();

      wrapper.style.position = "absolute";
      wrapper.style.left = "-9999px";
      wrapper.style.zIndex = "";
      wrapper.style.opacity = "";
    } catch (e) { console.error("PDF export failed:", e); }
    finally { setIsExporting(false); }
  };

  const handleExportDocx = async () => {
    if (isExportingDocx) return;
    setIsExportingDocx(true);
    try { await exportReportAsDocx(topic, captures, reportTextNoConfidence || reportContent, showImageLabels ? imageLabels : undefined); }
    catch (e) { console.error("Word export failed:", e); }
    finally { setIsExportingDocx(false); }
  };

  // Split by ## headers - try multiple patterns for robustness
  const reportSections = (() => {
    const text = reportTextClean || reportContent;
    if (!text) return [];
    let sections = text.split(/(?=\n##\s)/).filter((s) => s.trim());
    if (sections.length <= 1) {
      sections = text.split(/(?=##\s)/).filter((s) => s.trim());
    }
    return sections;
  })();

  return (
    <div className="flex flex-col h-[100dvh]">
      {pendingImage && (
        <CropModal imageSrc={pendingImage} onConfirm={handleCropConfirm} onCancel={() => setPendingImage(null)} />
      )}

      {/* ── Header ── */}
      <div className="border-b border-gray-800 px-6 py-4 bg-zinc-950">
        <div className="max-w-[1000px] mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold tracking-tight">{topic}</h1>
            <p className="text-xs text-gray-400 mt-0.5">Interpretation Report Mode</p>
          </div>
          <Button variant="ghost" onClick={onStartOver} className="text-gray-400 hover:text-white text-xs">
            Start Over
          </Button>
        </div>
      </div>

      {/* ── Main Content ── */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[1000px] mx-auto px-6 py-6 space-y-4">

          {/* ════════════ PRE-GENERATION VIEW ════════════ */}
          {!reportContent && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

              {/* ── 1. Reference Data ── */}
              <SectionCard title="Reference Data" defaultOpen={false}>
                <p className="text-xs text-gray-400 mb-3">
                  Upload manuals, papers, or data docs for RAG-powered interpretation.
                </p>
                <div className="bg-zinc-800 rounded-lg p-4 border border-gray-700 [&_input]:bg-zinc-800 [&_input]:border-gray-700 [&_input]:text-white [&_input]:placeholder-gray-500 [&_button]:text-sm [&_.border-gray-200]:border-gray-700 [&_.bg-white]:bg-zinc-800 [&_.text-black]:text-white [&_.border-black]:border-blue-500 [&_.text-gray-500]:text-gray-400 [&_.hover\\:text-gray-700]:hover:text-gray-300 [&_.text-gray-600]:text-gray-400 [&_.text-gray-400]:text-gray-500 [&_.border-gray-300]:border-gray-600 [&_.hover\\:border-gray-400]:hover:border-gray-500 [&_.bg-gray-50]:bg-zinc-700">
                  <ManualUpload mode="report" />
                </div>
                <ManualList mode="report" />
                <ManualStatus />
              </SectionCard>

              {/* ── 2. Data Captures ── */}
              <SectionCard title="Data Captures" badge={captures.length > 0 ? `${captures.length}` : undefined}>
                {/* Data type pills */}
                <div className="flex flex-wrap gap-1.5 mb-3">
                  {DATA_TYPES.map((dt) => (
                    <button
                      key={dt.id}
                      onClick={() => setCaptureType(dt.id)}
                      className={`px-2.5 py-1 text-[11px] rounded-full border transition-colors ${
                        captureType === dt.id
                          ? "bg-blue-600 border-blue-500 text-white"
                          : "bg-transparent border-gray-700 text-gray-400 hover:border-gray-500 hover:text-gray-200"
                      }`}
                    >
                      {dt.label}
                    </button>
                  ))}
                </div>

                {/* Description + Capture button row */}
                <div className="flex gap-2 mb-3">
                  <Textarea
                    value={captureDesc}
                    onChange={(e) => setCaptureDesc(e.target.value)}
                    placeholder="Data description (software, content, depth range...)"
                    className="flex-1 min-h-[40px] max-h-[80px] resize-none rounded-lg bg-zinc-800 border-gray-700 text-xs text-white placeholder-gray-500"
                    rows={1}
                    onKeyDown={(e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleCapture(); } }}
                  />
                  <Button
                    onClick={handleCapture}
                    disabled={isCapturing}
                    className="bg-blue-600 hover:bg-blue-700 text-white text-xs px-4 rounded-lg shrink-0"
                  >
                    {isCapturing ? "..." : "Capture"}
                  </Button>
                </div>

                {/* Drop zone */}
                <div
                  onDrop={handleDrop}
                  onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                  onDragLeave={() => setIsDragging(false)}
                  onClick={() => fileInputRef.current?.click()}
                  className={`border border-dashed rounded-lg p-2.5 text-center text-xs cursor-pointer transition-colors mb-3 ${
                    isDragging ? "border-blue-500 bg-blue-500/5 text-blue-400" : "border-gray-700 text-gray-400 hover:text-gray-300 hover:border-gray-500"
                  }`}
                >
                  {isDragging ? "Drop images here" : "Click or drop image files"}
                  <input ref={fileInputRef} type="file" accept="image/*" multiple className="hidden" onChange={(e) => handleFileUpload(e.target.files)} />
                </div>

                {/* Thumbnails */}
                {captures.length > 0 && (
                  <div className="grid grid-cols-3 md:grid-cols-4 gap-2">
                    {captures.map((capture, index) => (
                      <CaptureCard key={capture.timestamp} capture={capture} index={index} onRemove={() => removeCapture(index)} />
                    ))}
                  </div>
                )}
              </SectionCard>

              {/* ── 3. Report Settings ── */}
              <SectionCard title="Report Settings">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Left: Template + Language */}
                  <div className="space-y-3">
                    <div>
                      <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium mb-1.5 block">Template</label>
                      <div className="flex gap-1.5">
                        {TEMPLATES.map((t) => (
                          <button
                            key={t.id}
                            onClick={() => setReportTemplate(t.id)}
                            title={t.desc}
                            className={`flex-1 py-2 text-xs rounded-lg border text-center transition-colors ${
                              reportTemplate === t.id
                                ? "bg-blue-600/20 border-blue-500 text-blue-300 font-medium"
                                : "bg-zinc-800 border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-500"
                            }`}
                          >
                            {t.label}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium mb-1.5 block">Language</label>
                      <div className="flex gap-1.5">
                        {([["ko", "Korean"], ["en", "English"]] as const).map(([id, label]) => (
                          <button
                            key={id}
                            onClick={() => setReportLanguage(id)}
                            className={`flex-1 py-2 text-xs rounded-lg border text-center transition-colors ${
                              reportLanguage === id
                                ? "bg-blue-600/20 border-blue-500 text-blue-300 font-medium"
                                : "bg-zinc-800 border-gray-700 text-gray-400 hover:text-gray-200 hover:border-gray-500"
                            }`}
                          >
                            {label}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>
                  {/* Right: Section editor */}
                  <div>
                    <label className="text-[10px] uppercase tracking-wider text-gray-400 font-medium mb-1.5 block">Sections</label>
                    <CustomSectionEditor sections={customSections} setSections={setCustomSections} />
                  </div>
                </div>
              </SectionCard>

              {/* ── Generate Button ── */}
              <Button
                onClick={generateInterpretationReport}
                disabled={captures.length === 0 || isGenerating}
                className="w-full bg-green-600 hover:bg-green-700 text-white py-5 text-base font-semibold rounded-2xl shadow-lg shadow-green-900/20"
              >
                {isGenerating
                  ? "Generating Report..."
                  : captures.length === 0
                  ? "Add at least one capture to generate"
                  : `Generate Report (${captures.length} capture${captures.length > 1 ? "s" : ""})`}
              </Button>
            </motion.div>
          )}

          {/* ════════════ POST-GENERATION VIEW ════════════ */}
          {(reportContent || isGenerating) && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-4">

              {/* Action bar */}
              {reportContent && !isGenerating && (
                <div className="flex items-center justify-between bg-zinc-900 border border-gray-700 rounded-xl px-4 py-2.5">
                  <span className="text-xs text-gray-400 font-medium uppercase tracking-wide">Report Actions</span>
                  <div className="flex items-center gap-1">
                    <div className="relative" ref={exportRef}>
                      <ActionBtn onClick={() => setShowExportMenu((v) => !v)}>Export</ActionBtn>
                      {showExportMenu && (
                        <div className="absolute right-0 top-full mt-1 z-50 bg-zinc-800 border border-gray-700 rounded-lg shadow-xl py-1 min-w-[130px]">
                          <DropdownItem onClick={() => { setShowExportMenu(false); handleExportPdf(); }} disabled={isExporting}>
                            {isExporting ? "Exporting..." : "PDF (.pdf)"}
                          </DropdownItem>
                          <DropdownItem onClick={() => { setShowExportMenu(false); handleExportDocx(); }} disabled={isExportingDocx}>
                            {isExportingDocx ? "Exporting..." : "Word (.docx)"}
                          </DropdownItem>
                        </div>
                      )}
                    </div>
                    <ActionBtn onClick={handleCopyReport}>Copy</ActionBtn>
                    {imageLabels.length > 0 && (
                      <button
                        onClick={() => setShowImageLabels((v) => !v)}
                        className={`px-3 py-1.5 text-[11px] rounded-md transition-colors ${
                          showImageLabels
                            ? "bg-blue-600/20 text-blue-300 border border-blue-500/40"
                            : "text-gray-400 hover:text-white hover:bg-zinc-800"
                        }`}
                      >
                        {showImageLabels ? "Labels ON" : "Labels OFF"}
                      </button>
                    )}
                    <ActionBtn onClick={() => generateInterpretationReport()}>Regenerate</ActionBtn>
                  </div>
                </div>
              )}

              {/* Capture images with optional labels */}
              {captures.length > 0 && (
                <div className={showImageLabels ? "space-y-2" : "flex gap-2 overflow-x-auto pb-1"}>
                  {captures.map((c, i) => (
                    <div key={c.timestamp} className={`rounded-lg overflow-hidden border border-gray-700 ${showImageLabels ? "w-full" : "shrink-0 w-36"}`}>
                      <div className="relative">
                        <img src={c.image} alt={c.description} className={`w-full ${showImageLabels ? "h-auto" : "h-20 object-cover"}`} />
                        <ImageLabelOverlay labels={imageLabels} visible={showImageLabels} />
                      </div>
                      <p className="text-[10px] text-gray-400 px-1.5 py-1 truncate">#{i + 1} {c.description}</p>
                    </div>
                  ))}
                </div>
              )}

              {/* Report body */}
              <div className="bg-zinc-900 rounded-2xl p-6 border border-gray-700 text-white [&_h2]:text-white [&_h3]:text-white [&_p]:text-gray-200 [&_li]:text-gray-200 [&_strong]:text-white">
                {isGenerating && !reportContent && (
                  <div className="flex items-center gap-3 text-gray-400 py-8 justify-center">
                    <div className="size-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    <span className="text-sm">Analyzing captures and generating report...</span>
                  </div>
                )}
                {/* Show content while streaming (isGenerating + has content) */}
                {reportContent && isGenerating && (
                  <div>
                    <ReportMarkdown>{reportContent}</ReportMarkdown>
                    <div className="flex items-center gap-2 text-gray-400 mt-4">
                      <div className="size-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                      <span className="text-xs">Writing...</span>
                    </div>
                  </div>
                )}
                {/* Show sections with Regenerate buttons after generation is complete */}
                {reportContent && !isGenerating && (
                  reportSections.length > 0 ? (
                    reportSections.map((section, idx) => {
                      const titleMatch = section.match(/##\s+(.+)/m);
                      const sectionTitle = titleMatch ? titleMatch[1].trim() : "";
                      const isRegenerating = !!sectionTitle && regeneratingSection === sectionTitle;
                      const lines = section.split("\n");
                      const headerLine = lines[0];
                      const bodyContent = lines.slice(1).join("\n");
                      return (
                        <div key={idx} className="mb-2">
                          {sectionTitle ? (
                            <div className="flex items-center gap-3 mt-6 mb-2 pb-2 border-b border-gray-600">
                              <div className="flex-1"><ReportMarkdown>{headerLine}</ReportMarkdown></div>
                              <button
                                onClick={() => regenerateReportSection(sectionTitle)}
                                disabled={!!regeneratingSection}
                                className="shrink-0 text-xs px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-40 transition-colors font-medium"
                              >
                                {isRegenerating ? "Regenerating..." : "Regenerate"}
                              </button>
                            </div>
                          ) : (
                            <ReportMarkdown>{headerLine}</ReportMarkdown>
                          )}
                          <div className={isRegenerating ? "opacity-30" : ""}>
                            {isRegenerating && (
                              <div className="flex items-center gap-2 text-xs text-gray-400 my-3">
                                <div className="size-3 border-2 border-current border-t-transparent rounded-full animate-spin" />
                                Regenerating this section...
                              </div>
                            )}
                            <ReportMarkdown>{bodyContent}</ReportMarkdown>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <ReportMarkdown>{reportContent}</ReportMarkdown>
                  )
                )}
              </div>

            </motion.div>
          )}
        </div>
      </div>

      {/* ── Hidden printable div (mirrors app structure) ── */}
      {reportContent && (
        <div style={{ position: "absolute", left: "-9999px", top: 0 }}>
          <div ref={printRef} style={{ width: "580px", backgroundColor: "white", color: "#111", padding: "12px 12px 12px 20px", fontFamily: "'Segoe UI', 'Malgun Gothic', sans-serif", fontSize: "11px", wordBreak: "break-word", overflowWrap: "break-word", overflow: "visible", lineHeight: 1.7, boxSizing: "border-box" }}>
            <h1 style={{ fontSize: "16px", fontWeight: 700, color: "#111", margin: "0 0 4px 0" }}>{topic}</h1>
            <p style={{ fontSize: "9px", color: "#888", margin: "0 0 14px 0" }}>GeoLens Interpretation Report &middot; {new Date().toLocaleDateString("ko-KR")}</p>
            {captures.length > 0 && (
              <div style={{ marginBottom: "16px" }}>
                {(showImageLabels && labeledImages.length > 0 ? labeledImages : captures.map((c) => c.image)).map((src, i) => (
                  <div key={i} style={{ marginBottom: "12px" }}>
                    <img src={src} alt={captures[i]?.description} style={{ width: "100%", maxWidth: "100%", height: "auto", display: "block", border: "1px solid #d1d5db", borderRadius: "4px", boxSizing: "border-box" }} />
                    <p style={{ fontSize: "9px", color: "#6b7280", marginTop: "2px" }}>
                      Capture {i + 1}: {captures[i]?.description}{showImageLabels && labeledImages.length > 0 ? " (with structural labels)" : ""}
                    </p>
                  </div>
                ))}
              </div>
            )}
            <div dangerouslySetInnerHTML={{ __html: markdownToInlineHtml(reportTextNoConfidence || reportContent) }} />
          </div>
        </div>
      )}
    </div>
  );
};

/* ──────────────────── Small UI components ──────────────────── */

function ActionBtn({ onClick, disabled, children }: { onClick: () => void; disabled?: boolean; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="px-3 py-1.5 text-[11px] text-gray-300 hover:text-white hover:bg-zinc-800 rounded-md transition-colors disabled:opacity-40"
    >
      {children}
    </button>
  );
}

function DropdownItem({ onClick, disabled, children }: { onClick: () => void; disabled?: boolean; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="w-full text-left px-4 py-2 text-xs text-gray-200 hover:bg-zinc-700 disabled:opacity-50"
    >
      {children}
    </button>
  );
}

function CaptureCard({ capture, index, onRemove }: { capture: CapturedScreen; index: number; onRemove: () => void }) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="relative group rounded-lg overflow-hidden border border-gray-700 bg-zinc-800"
    >
      <img src={capture.image} alt={capture.description} className="w-full h-24 object-cover" />
      <div className="px-1.5 py-1">
        <span className="text-[9px] px-1.5 py-0.5 rounded-full bg-blue-600/20 text-blue-300">
          {DATA_TYPES.find((d) => d.id === capture.dataType)?.label || capture.dataType}
        </span>
        <p className="text-[10px] text-gray-400 truncate mt-0.5">#{index + 1} {capture.description}</p>
      </div>
      <button
        onClick={onRemove}
        className="absolute top-1 right-1 bg-black/60 text-white rounded-full w-5 h-5 flex items-center justify-center text-[10px] opacity-0 group-hover:opacity-100 transition-opacity"
      >
        X
      </button>
    </motion.div>
  );
}

/* ──────────────────── Custom Section Editor ──────────────────── */

function CustomSectionEditor({ sections, setSections }: { sections: string[]; setSections: (s: string[]) => void }) {
  const [input, setInput] = useState("");
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [dragOverIdx, setDragOverIdx] = useState<number | null>(null);

  const addSection = () => {
    const trimmed = input.trim();
    if (!trimmed || sections.includes(trimmed)) return;
    setSections([...sections, trimmed]);
    setInput("");
  };

  const removeSection = (idx: number) => setSections(sections.filter((_, i) => i !== idx));

  const handleDrop = (idx: number) => {
    if (dragIdx === null || dragIdx === idx) { setDragIdx(null); setDragOverIdx(null); return; }
    const next = [...sections];
    const [moved] = next.splice(dragIdx, 1);
    next.splice(idx, 0, moved);
    setSections(next);
    setDragIdx(null);
    setDragOverIdx(null);
  };

  const unusedPresets = ALL_SECTIONS.filter((s) => !sections.includes(s.id));

  return (
    <div className="space-y-2">
      {/* Draggable list */}
      {sections.length > 0 && (
        <div className="flex flex-col gap-0.5 max-h-[180px] overflow-y-auto pr-1">
          {sections.map((s, i) => {
            const preset = ALL_SECTIONS.find((a) => a.id === s);
            const label = preset ? preset.ko : s;
            return (
              <div
                key={s + i}
                draggable
                onDragStart={() => setDragIdx(i)}
                onDragOver={(e) => { e.preventDefault(); setDragOverIdx(i); }}
                onDrop={() => handleDrop(i)}
                onDragEnd={() => { setDragIdx(null); setDragOverIdx(null); }}
                className={`flex items-center gap-1.5 px-2 py-1 text-[11px] rounded-md border cursor-grab active:cursor-grabbing transition-all ${
                  dragIdx === i ? "opacity-30 border-blue-500" : dragOverIdx === i ? "border-blue-400 bg-blue-600/5" : "border-gray-700 bg-zinc-800"
                }`}
              >
                <span className="text-gray-500 select-none text-[10px]">&#x2807;</span>
                <span className="text-gray-300 flex-1 truncate">{label}</span>
                <button onClick={() => removeSection(i)} className="text-gray-500 hover:text-red-400 text-sm leading-none">&times;</button>
              </div>
            );
          })}
        </div>
      )}

      {/* Input row */}
      <div className="flex gap-1.5">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addSection(); } }}
          placeholder="Type section name..."
          className="flex-1 px-2.5 py-1.5 text-[11px] rounded-md bg-zinc-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
        />
        <button onClick={addSection} className="px-2.5 py-1.5 text-[11px] rounded-md bg-blue-600 text-white hover:bg-blue-500">Add</button>
      </div>

      {/* Quick add */}
      {unusedPresets.length > 0 && (
        <div className="flex flex-wrap gap-1">
          {unusedPresets.map((s) => (
            <button
              key={s.id}
              onClick={() => setSections([...sections, s.id])}
              className="px-1.5 py-0.5 text-[9px] rounded bg-zinc-800 text-gray-400 hover:text-gray-200 border border-gray-700 transition-colors"
            >
              + {s.ko}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
