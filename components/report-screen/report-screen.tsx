"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import { motion } from "framer-motion";
import { Button } from "../ui/button";
import { Textarea } from "../ui/textarea";
import { CropModal } from "./crop-modal";
import { ReportMarkdown } from "./report-markdown";
import { ManualUpload } from "../manual/manual-upload";
import { ManualList } from "../manual/manual-list";
import { ManualStatus } from "../manual/manual-status";
import { exportReportAsDocx } from "@/lib/export-docx";
import { DATA_TYPES, type DataType } from "@/app/providers/ReportProvider";
import type { ReportContextType, CapturedScreen } from "@/app/providers/ReportProvider";
import type { ReportTemplate } from "@/lib/prompts/report";
import { ALL_SECTIONS } from "@/lib/prompts/report";

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
  const exportRef = useRef<HTMLDivElement>(null);
  const printRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

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
      await html2pdf().set({
        margin: [15, 15, 15, 15],
        filename: `GeoLens_Report_${new Date().toISOString().slice(0, 10)}.pdf`,
        image: { type: "jpeg", quality: 0.95 },
        html2canvas: { scale: 2, useCORS: true, logging: false, width: 680 },
        jsPDF: { unit: "mm", format: "a4", orientation: "portrait" },
        pagebreak: { mode: ["avoid-all", "css", "legacy"] },
      }).from(printRef.current).save();
    } catch (e) { console.error("PDF export failed:", e); }
    finally { setIsExporting(false); }
  };

  const handleExportDocx = async () => {
    if (isExportingDocx) return;
    setIsExportingDocx(true);
    try { await exportReportAsDocx(topic, captures, reportContent); }
    catch (e) { console.error("Word export failed:", e); }
    finally { setIsExportingDocx(false); }
  };

  // Split by ## headers - try multiple patterns for robustness
  const reportSections = (() => {
    if (!reportContent) return [];
    // Try splitting by ## at line start
    let sections = reportContent.split(/(?=\n##\s)/).filter((s) => s.trim());
    if (sections.length <= 1) {
      // Try with ## anywhere (some models don't put newline before first ##)
      sections = reportContent.split(/(?=##\s)/).filter((s) => s.trim());
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
                  <ManualUpload />
                </div>
                <ManualList />
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
                    <ActionBtn onClick={() => generateInterpretationReport()}>Regenerate</ActionBtn>
                  </div>
                </div>
              )}

              {/* Capture strip */}
              {captures.length > 0 && (
                <div className="flex gap-2 overflow-x-auto pb-1">
                  {captures.map((c, i) => (
                    <div key={c.timestamp} className="shrink-0 w-36 rounded-lg overflow-hidden border border-gray-700">
                      <img src={c.image} alt={c.description} className="w-full h-20 object-cover" />
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

      {/* ── Hidden printable div ── */}
      {reportContent && (
        <div className="fixed left-[-9999px] top-0">
          <div ref={printRef} className="w-[210mm] bg-white text-black p-8 font-sans text-sm break-words [word-break:break-word] overflow-hidden [&_*]:max-w-full [&_pre]:whitespace-pre-wrap [&_code]:break-all [&_table]:table-fixed [&_td]:break-words [&_img]:max-w-full [&_img]:h-auto">
            <h1 className="text-xl font-bold mb-1">{topic}</h1>
            <p className="text-xs text-gray-500 mb-4">GeoLens Interpretation Report &middot; {new Date().toLocaleDateString("ko-KR")}</p>
            {captures.length > 0 && (
              <div className="grid grid-cols-2 gap-3 mb-4">
                {captures.map((c, i) => (
                  <div key={c.timestamp}>
                    <img src={c.image} alt={c.description} className="w-full rounded border border-gray-300" />
                    <p className="text-[10px] text-gray-500 mt-0.5">Capture {i + 1}: {c.description}</p>
                  </div>
                ))}
              </div>
            )}
            <div className="[&_h2]:text-base [&_h2]:font-bold [&_h2]:mt-3 [&_h2]:mb-1 [&_h3]:text-sm [&_h3]:font-bold [&_h3]:mt-2 [&_li]:py-0.5 [&_li]:text-sm [&_p]:text-sm [&_p]:mb-1 [&_ul]:list-disc [&_ul]:ml-4 [&_ol]:list-decimal [&_ol]:ml-4">
              <ReportMarkdown showConfidence={false}>{reportContent}</ReportMarkdown>
            </div>
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
