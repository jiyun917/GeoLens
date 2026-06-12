"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useScreenShare } from "@/hooks/screenshare";
import { ManualUpload } from "@/components/manual/manual-upload";
import { ManualList } from "@/components/manual/manual-list";
import { ManualStatus } from "@/components/manual/manual-status";
import { GoalInput } from "@/components/goal-input";

interface Checkpoint {
  id: string;
  goal: string;
  title?: string;
  plan?: string[];
  completedSteps?: string[];
  timestamp: number;
}

export default function HomePage() {
  const router = useRouter();
  const { isSharing, stopSharing } = useScreenShare();
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([]);

  useEffect(() => {
    if (isSharing) stopSharing();

    const allCheckpoints: Checkpoint[] = [];
    try {
      const guideRaw = localStorage.getItem("geolens-guide-checkpoints");
      if (guideRaw) {
        allCheckpoints.push(...JSON.parse(guideRaw));
      }
    } catch { /* ignore */ }

    const valid = allCheckpoints
      .filter((cp) => Date.now() - cp.timestamp < 7 * 24 * 60 * 60 * 1000)
      .sort((a, b) => b.timestamp - a.timestamp);
    setCheckpoints(valid);
  }, []);

  const handleResumeCheckpoint = (cp: Checkpoint) => {
    sessionStorage.setItem("geolens-goal", cp.goal);
    sessionStorage.setItem("geolens-resume-data", JSON.stringify({
      plan: cp.plan || [],
      completedSteps: cp.completedSteps || [],
    }));
    router.push("/task");
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

  const handleRenameCheckpoint = (id: string) => {
    const cp = checkpoints.find((c) => c.id === id);
    const current = cp?.title || cp?.goal || "";
    const newTitle = prompt("Set a title for this session:", current);
    if (newTitle === null) return;

    const updated = checkpoints.map((c) =>
      c.id === id ? { ...c, title: newTitle || undefined } : c
    );
    setCheckpoints(updated);

    try {
      const raw = localStorage.getItem("geolens-guide-checkpoints");
      if (raw) {
        const all = JSON.parse(raw).map((c: any) =>
          c.id === id ? { ...c, title: newTitle || undefined } : c
        );
        localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(all));
      }
    } catch { /* ignore */ }
  };

  const handleDismissCheckpoint = (id: string) => {
    const next = checkpoints.filter((cp) => cp.id !== id);
    setCheckpoints(next);
    localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(next));
  };

  return (
    <div className="flex items-center justify-center min-h-[100dvh] bg-grid-pattern">
      <div className="max-w-[600px] w-full mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2">GeoLens</h1>
          <p className="text-gray-500">
            Share your screen with AI. Get guided step-by-step.
          </p>
        </div>

        {checkpoints.length > 0 && (
          <div className="mb-4 space-y-2">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Resume Sessions</h3>
            {checkpoints.map((cp) => (
              <div key={cp.id} className="rounded-xl border-2 border-orange-400 bg-orange-950 p-3">
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-orange-200">
                      {cp.completedSteps?.length || 0} steps
                    </span>
                    <span className="text-[10px] text-orange-400/70">{formatTime(cp.timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleRenameCheckpoint(cp.id)}
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
      </div>
    </div>
  );
}
