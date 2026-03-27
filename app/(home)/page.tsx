"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useScreenShare } from "@/hooks/screenshare";
import { ManualUpload } from "@/components/manual/manual-upload";
import { ManualList } from "@/components/manual/manual-list";
import { ManualStatus } from "@/components/manual/manual-status";
import { GoalInput } from "@/components/goal-input";
import { ProjectList } from "@/components/project-list";

interface Checkpoint {
  id: string;
  mode: "guide" | "report";
  goal: string;
  title?: string;
  // Guide fields
  plan?: string[];
  completedSteps?: string[];
  // Report fields
  captureCount?: number;
  hasReport?: boolean;
  timestamp: number;
}

interface WorkflowItem {
  goal: string;
  timestamp: number;
  stepCount: number;
}

export default function HomePage() {
  const router = useRouter();
  const { isSharing, stopSharing } = useScreenShare();
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);

  useEffect(() => {
    if (isSharing) stopSharing();

    // Load checkpoints (guide + report)
    const allCheckpoints: Checkpoint[] = [];
    try {
      const guideRaw = localStorage.getItem("geolens-guide-checkpoints");
      if (guideRaw) {
        const guideAll = JSON.parse(guideRaw).map((c: any) => ({ ...c, mode: "guide" as const, goal: c.goal }));
        allCheckpoints.push(...guideAll);
      }
    } catch { /* ignore */ }
    try {
      const reportRaw = localStorage.getItem("geolens-report-checkpoints");
      if (reportRaw) {
        const reportAll = JSON.parse(reportRaw).map((c: any) => ({ ...c, mode: "report" as const, goal: c.topic }));
        allCheckpoints.push(...reportAll);
      }
    } catch { /* ignore */ }

    // Filter out older than 7 days, sort by timestamp
    const valid = allCheckpoints
      .filter((cp) => Date.now() - cp.timestamp < 7 * 24 * 60 * 60 * 1000)
      .sort((a, b) => b.timestamp - a.timestamp);
    console.log("[Home] Loaded checkpoints:", valid.length, valid.map(c => ({ id: c.id, goal: c.goal?.slice(0, 30), mode: c.mode })));
    setCheckpoints(valid);

    // Load workflow history
    try {
      const raw = localStorage.getItem("geolens-workflow-history");
      if (raw) setWorkflows(JSON.parse(raw));
    } catch { /* ignore */ }
  }, []);

  const handleResumeCheckpoint = (cp: Checkpoint) => {
    if (cp.mode === "guide") {
      sessionStorage.setItem("geolens-goal", cp.goal);
      sessionStorage.setItem("geolens-resume-data", JSON.stringify({
        plan: cp.plan || [],
        completedSteps: cp.completedSteps || [],
      }));
      router.push("/task");
    } else {
      sessionStorage.setItem("geolens-report-checkpoint-id", cp.id);
      sessionStorage.setItem("geolens-report-topic", cp.goal);
      router.push("/report");
    }
  };

  const formatTime = (ts: number) => {
    const d = new Date(ts);
    const now = new Date();
    const diffMs = now.getTime() - d.getTime();
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return "just now";
    if (diffMin < 60) return `${diffMin}m ago`;
    const diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    const diffDay = Math.floor(diffHr / 24);
    return `${diffDay}d ago`;
  };

  const handleRenameCheckpoint = (id: string, mode: string) => {
    const cp = checkpoints.find((c) => c.id === id);
    const current = cp?.title || cp?.goal || "";
    const newTitle = prompt("Set a title for this session:", current);
    if (newTitle === null) return;

    const updated = checkpoints.map((c) =>
      c.id === id ? { ...c, title: newTitle || undefined } : c
    );
    setCheckpoints(updated);

    // Persist
    const storageKey = mode === "guide" ? "geolens-guide-checkpoints" : "geolens-report-checkpoints";
    try {
      const raw = localStorage.getItem(storageKey);
      if (raw) {
        const all = JSON.parse(raw).map((c: any) =>
          c.id === id ? { ...c, title: newTitle || undefined } : c
        );
        localStorage.setItem(storageKey, JSON.stringify(all));
      }
    } catch { /* ignore */ }
  };

  const handleDismissCheckpoint = (id: string) => {
    const next = checkpoints.filter((cp) => cp.id !== id);
    setCheckpoints(next);
    // Remove from the correct storage
    const dismissed = checkpoints.find((cp) => cp.id === id);
    if (dismissed?.mode === "guide") {
      const guideOnly = next.filter((c) => c.mode === "guide");
      localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(guideOnly));
    } else {
      const reportOnly = next.filter((c) => c.mode === "report");
      localStorage.setItem("geolens-report-checkpoints", JSON.stringify(reportOnly));
    }
  };

  const handleRunWorkflow = (goal: string) => {
    sessionStorage.setItem("geolens-goal", goal);
    router.push("/task");
  };

  const handleRemoveWorkflow = (index: number) => {
    const next = workflows.filter((_, i) => i !== index);
    setWorkflows(next);
    localStorage.setItem("geolens-workflow-history", JSON.stringify(next));
  };

  return (
    <div className="flex items-center justify-center min-h-[100dvh] bg-grid-pattern">
      <div className="max-w-[600px] w-full mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">GeoLens</h1>
          <p className="text-gray-500">
            Share your screen with AI. Get guided or generate interpretation reports.
          </p>
        </div>

        {/* Resume checkpoint banners */}
        {checkpoints.length > 0 && (
          <div className="mb-4 space-y-2">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Resume Sessions</h3>
            {checkpoints.map((cp) => (
              <div key={cp.id} className="rounded-xl border-2 border-orange-400 bg-orange-950 p-3">
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${
                      cp.mode === "guide"
                        ? "bg-orange-400/20 text-orange-300"
                        : "bg-purple-400/20 text-purple-300"
                    }`}>
                      {cp.mode === "guide" ? "Guide Mode" : "Report Mode"}
                    </span>
                    <span className="text-xs text-orange-200">
                      {cp.mode === "guide"
                        ? `${cp.completedSteps?.length || 0} steps`
                        : `${cp.captureCount || 0} captures${cp.hasReport ? " · report generated" : ""}`}
                    </span>
                    <span className="text-[10px] text-orange-400/70">{formatTime(cp.timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRenameCheckpoint(cp.id, cp.mode)}
                      className="text-xs text-orange-300 hover:text-white"
                      title="Rename"
                    >
                      Rename
                    </button>
                    <button
                      onClick={() => handleDismissCheckpoint(cp.id)}
                      className="text-xs text-orange-300 hover:text-white"
                    >
                      Dismiss
                    </button>
                  </div>
                </div>
                <p className="text-sm text-white font-medium truncate">
                  {cp.title || cp.goal}
                </p>
                {cp.title && (
                  <p className="text-[11px] text-orange-300/60 truncate">{cp.goal}</p>
                )}
                <button
                  onClick={() => handleResumeCheckpoint(cp)}
                  className="w-full mt-2 py-2 text-sm font-bold text-white bg-orange-500 hover:bg-orange-400 rounded-lg transition-colors"
                >
                  Continue
                </button>
              </div>
            ))}
          </div>
        )}

        <div className="mb-6 space-y-4">
          <ManualUpload />
          <ManualList />
          <ManualStatus />
        </div>

        <GoalInput />

        <div className="mt-4">
          <ProjectList />
        </div>
      </div>
    </div>
  );
}
