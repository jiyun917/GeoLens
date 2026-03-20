"use client";

import { useScreenShare } from "@/hooks/screenshare";
import { generateReport, regenerateSection } from "@/lib/ai";
import type { ReportLanguage, ReportTemplate } from "@/lib/prompts/report";
import { PRESET_SECTIONS } from "@/lib/prompts/report";
import {
  createContext,
  ReactNode,
  useContext,
  useEffect,
  useRef,
  useState,
} from "react";
import { useSettings } from "./SettingsProvider";
import { useManuals } from "./ManualProvider";

export const DATA_TYPES = [
  { id: "seismic", label: "탄성파 (Seismic)" },
  { id: "well_log", label: "검층 (Well Log)" },
  { id: "gravity", label: "중력 (Gravity)" },
  { id: "magnetic", label: "자력 (Magnetic)" },
  { id: "gpr", label: "GPR" },
  { id: "resistivity", label: "전기비저항 (Resistivity)" },
  { id: "geological_map", label: "지질도 (Geological Map)" },
  { id: "other", label: "기타 (Other)" },
] as const;

export type DataType = (typeof DATA_TYPES)[number]["id"];

export interface CapturedScreen {
  image: string;
  description: string;
  dataType: DataType;
  timestamp: number;
}

export interface ReportContextType {
  topic: string;
  setTopic: (topic: string) => void;

  captures: CapturedScreen[];
  captureFullScreen: () => Promise<string | null>;
  addCapture: (image: string, description: string, dataType: DataType) => void;
  removeCapture: (index: number) => void;

  reportContent: string;
  isGenerating: boolean;
  generateInterpretationReport: () => Promise<void>;
  regenerateReportSection: (sectionTitle: string) => Promise<void>;
  regeneratingSection: string;

  reportLanguage: ReportLanguage;
  setReportLanguage: (lang: ReportLanguage) => void;

  reportTemplate: ReportTemplate;
  setReportTemplate: (t: ReportTemplate) => void;
  customSections: string[];
  setCustomSections: (s: string[]) => void;

  projectId: string;
  isSaving: boolean;
  saveProject: () => Promise<void>;
  loadProject: (id: string) => Promise<void>;
  loadFromCheckpoint: (checkpointId: string) => void;

  reset: () => void;
}

const ReportContext = createContext<ReportContextType | undefined>(undefined);

export function ReportProvider({ children }: { children: ReactNode }) {
  const [topic, setTopic] = useState("");
  const [captures, setCaptures] = useState<CapturedScreen[]>([]);
  const [reportContent, setReportContent] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [regeneratingSection, setRegeneratingSection] = useState("");
  const [projectId, setProjectId] = useState("");
  const [isSaving, setIsSaving] = useState(false);
  const [reportLanguage, setReportLanguage] = useState<ReportLanguage>("ko");
  const [reportTemplate, _setReportTemplate] = useState<ReportTemplate>("detailed");
  const [customSections, setCustomSections] = useState<string[]>(PRESET_SECTIONS.detailed);

  const setReportTemplate = (t: ReportTemplate) => {
    _setReportTemplate(t);
    if (t !== "custom" && PRESET_SECTIONS[t]) {
      setCustomSections([...PRESET_SECTIONS[t]]);
    }
  };

  const { settings } = useSettings();
  const { activeManualIds } = useManuals();
  const { captureImageFromStream } = useScreenShare();

  const captureFullScreen = async (): Promise<string | null> => {
    try {
      const { scaledImageDataUrl } = await captureImageFromStream({
        isLocalLlm: false,
      });
      return scaledImageDataUrl;
    } catch (e) {
      console.error("Failed to capture screen:", e);
      return null;
    }
  };

  const addCapture = (image: string, description: string, dataType: DataType) => {
    const desc = description || `Capture ${captures.length + 1}`;
    const newCapture: CapturedScreen = {
      image,
      description: desc,
      dataType,
      timestamp: Date.now(),
    };
    setCaptures((prev) => [...prev, newCapture]);
  };

  const removeCapture = (index: number) => {
    setCaptures((prev) => prev.filter((_, i) => i !== index));
  };

  // === Auto-save checkpoint for Report Mode (debounced, skip during generation) ===
  const reportCheckpointIdRef = useRef<string>("");
  const saveTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    // Don't save during active generation/regeneration (causes perf issues with streaming)
    if (isGenerating || regeneratingSection) return;
    if (!topic || (captures.length === 0 && !reportContent)) return;

    // Debounce: save 2 seconds after last change
    if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    saveTimerRef.current = setTimeout(() => {
      if (!reportCheckpointIdRef.current) {
        reportCheckpointIdRef.current = `rp_${Date.now().toString(36)}`;
      }

      try {
        const raw = localStorage.getItem("geolens-report-checkpoints");
        const all: Array<any> = raw ? JSON.parse(raw) : [];

        const entry = {
          id: reportCheckpointIdRef.current,
          mode: "report",
          topic,
          captureCount: captures.length,
          hasReport: !!reportContent,
          captures: captures.map((c) => ({
            image: c.image,
            description: c.description,
            dataType: c.dataType,
            timestamp: c.timestamp,
          })),
          reportContent,
          reportLanguage,
          reportTemplate,
          customSections,
          timestamp: Date.now(),
        };

        const idx = all.findIndex((c: any) => c.id === entry.id);
        if (idx >= 0) {
          all[idx] = entry;
        } else {
          all.unshift(entry);
        }

        localStorage.setItem("geolens-report-checkpoints", JSON.stringify(all.slice(0, 10)));
      } catch {
        // localStorage full
      }
    }, 2000);

    return () => {
      if (saveTimerRef.current) clearTimeout(saveTimerRef.current);
    };
  }, [topic, captures, reportContent, reportLanguage, reportTemplate, customSections, isGenerating, regeneratingSection]);

  const generateInterpretationReport = async () => {
    if (captures.length === 0 || isGenerating) return;

    setIsGenerating(true);
    setReportContent("");

    try {
      await generateReport(
        topic,
        captures.map((c) => ({
          image: c.image,
          description: c.description,
          dataType: c.dataType,
        })),
        settings,
        (streamed) => {
          setReportContent(streamed);
        },
        activeManualIds.length > 0 ? activeManualIds : undefined,
        reportLanguage,
        "custom",
        customSections
      );
    } catch (e) {
      console.error("Report generation failed:", e);
    } finally {
      setIsGenerating(false);
    }
  };

  const regenerateReportSection = async (sectionTitle: string) => {
    if (!reportContent || regeneratingSection) return;

    setRegeneratingSection(sectionTitle);

    try {
      let newSectionContent = "";
      await regenerateSection(
        topic,
        captures.map((c) => ({
          image: "",  // no image needed for section regen
          description: c.description,
          dataType: c.dataType,
        })),
        reportContent,
        sectionTitle,
        settings,
        (streamed) => {
          newSectionContent = streamed;
        },
        undefined,
        reportLanguage
      );

      if (newSectionContent) {
        // Replace the section in the full report using functional update to avoid stale closure
        setReportContent((prev) => {
          const escaped = sectionTitle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
          const sectionRegex = new RegExp(`## ${escaped}\\n[\\s\\S]*?(?=\\n## |$)`);
          if (sectionRegex.test(prev)) {
            return prev.replace(sectionRegex, newSectionContent.trim());
          }
          return prev + "\n\n" + newSectionContent.trim();
        });
      }
    } catch (e) {
      console.error("Section regeneration failed:", e);
    } finally {
      setRegeneratingSection("");
    }
  };

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

  const saveProject = async () => {
    if (isSaving) return;
    setIsSaving(true);
    try {
      const res = await fetch(`${apiUrl}/project/save`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id: projectId,
          topic,
          captures: captures.map((c) => ({
            image: c.image,
            description: c.description,
            dataType: c.dataType,
            timestamp: c.timestamp,
          })),
          report_content: reportContent,
          manual_ids: activeManualIds,
        }),
      });
      const data = await res.json();
      if (data.id) setProjectId(data.id);
    } catch (e) {
      console.error("Failed to save project:", e);
    } finally {
      setIsSaving(false);
    }
  };

  const loadFromCheckpoint = (checkpointId: string) => {
    try {
      const raw = localStorage.getItem("geolens-report-checkpoints");
      if (!raw) return;
      const all = JSON.parse(raw);
      const cp = all.find((c: any) => c.id === checkpointId);
      if (!cp) return;

      reportCheckpointIdRef.current = cp.id;
      setTopic(cp.topic || "");
      setCaptures(
        (cp.captures || []).map((c: any) => ({
          image: c.image || "",
          description: c.description || "",
          dataType: c.dataType || "other",
          timestamp: c.timestamp || Date.now(),
        }))
      );
      setReportContent(cp.reportContent || "");
      setReportLanguage(cp.reportLanguage || "ko");
      _setReportTemplate(cp.reportTemplate || "detailed");
      setCustomSections(cp.customSections || PRESET_SECTIONS.detailed);
    } catch (e) {
      console.error("Failed to load checkpoint:", e);
    }
  };

  const loadProject = async (id: string) => {
    try {
      const res = await fetch(`${apiUrl}/project/${id}`);
      if (!res.ok) return;
      const data = await res.json();
      setProjectId(data.id || "");
      setTopic(data.topic || "");
      setCaptures(
        (data.captures || []).map((c: any) => ({
          image: c.image || "",
          description: c.description || "",
          dataType: c.dataType || "other",
          timestamp: c.timestamp || Date.now(),
        }))
      );
      setReportContent(data.report_content || "");
    } catch (e) {
      console.error("Failed to load project:", e);
    }
  };

  const reset = () => {
    // Remove this session's report checkpoint
    if (reportCheckpointIdRef.current) {
      try {
        const raw = localStorage.getItem("geolens-report-checkpoints");
        if (raw) {
          const all = JSON.parse(raw).filter((c: any) => c.id !== reportCheckpointIdRef.current);
          localStorage.setItem("geolens-report-checkpoints", JSON.stringify(all));
        }
      } catch { /* ignore */ }
      reportCheckpointIdRef.current = "";
    }
    setTopic("");
    setCaptures([]);
    setReportContent("");
    setIsGenerating(false);
    setRegeneratingSection("");
    setProjectId("");
  };

  const ctx: ReportContextType = {
    topic,
    setTopic,
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
    loadProject,
    loadFromCheckpoint,
    reset,
  };

  return (
    <ReportContext.Provider value={ctx}>{children}</ReportContext.Provider>
  );
}

export function useReport() {
  const context = useContext(ReportContext);
  if (context === undefined) {
    throw new Error("useReport must be used within a ReportProvider");
  }
  return context;
}
