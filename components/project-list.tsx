"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

interface ProjectSummary {
  id: string;
  topic: string;
  capture_count: number;
  data_types: string[];
  has_report: boolean;
  created_at: string;
  updated_at: string;
}

const DATA_TYPE_SHORT: Record<string, string> = {
  seismic: "탄성파",
  well_log: "검층",
  gravity: "중력",
  magnetic: "자력",
  gpr: "GPR",
  resistivity: "전기비저항",
  geological_map: "지질도",
  other: "기타",
};

export function ProjectList() {
  const [projects, setProjects] = useState<ProjectSummary[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  const apiUrl =
    process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

  const fetchProjects = async () => {
    try {
      const res = await fetch(`${apiUrl}/project/list`);
      if (!res.ok) return;
      const data = await res.json();
      setProjects(data.projects || []);
    } catch {
      // ignore
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleOpen = (id: string) => {
    sessionStorage.setItem("geolens-project-id", id);
    router.push("/report");
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await fetch(`${apiUrl}/project/${id}`, { method: "DELETE" });
      setProjects((prev) => prev.filter((p) => p.id !== id));
    } catch {
      // ignore
    }
  };

  if (projects.length === 0) return null;

  const formatDate = (iso: string) => {
    try {
      const d = new Date(iso);
      return d.toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      });
    } catch {
      return "";
    }
  };

  return (
    <div className="border border-gray-700 rounded-xl overflow-hidden">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-3 hover:bg-zinc-800/50 transition-colors"
      >
        <span className="text-sm font-medium text-gray-300">
          Previous Projects ({projects.length})
        </span>
        <span className="text-xs text-gray-500">
          {isOpen ? "Close" : "Open"}
        </span>
      </button>

      {isOpen && (
        <div className="px-3 pb-3 space-y-2">
          {projects.map((p) => (
            <button
              key={p.id}
              onClick={() => handleOpen(p.id)}
              className="w-full text-left px-3 py-2.5 rounded-lg bg-zinc-800/50 hover:bg-zinc-800 border border-gray-700/50 transition-colors group"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0 flex-1">
                  <p className="text-sm text-white truncate">{p.topic}</p>
                  <div className="flex items-center gap-2 mt-1 text-[11px] text-gray-500">
                    <span>{formatDate(p.updated_at)}</span>
                    <span>&middot;</span>
                    <span>{p.capture_count} captures</span>
                    {p.has_report && (
                      <>
                        <span>&middot;</span>
                        <span className="text-green-500">report</span>
                      </>
                    )}
                  </div>
                  {p.data_types.length > 0 && (
                    <div className="flex gap-1 mt-1 flex-wrap">
                      {p.data_types.map((dt) => (
                        <span
                          key={dt}
                          className="text-[10px] px-1.5 py-0.5 rounded bg-blue-600/10 text-blue-400/70"
                        >
                          {DATA_TYPE_SHORT[dt] || dt}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={(e) => handleDelete(p.id, e)}
                  className="text-gray-600 hover:text-red-400 text-xs opacity-0 group-hover:opacity-100 transition-opacity mt-1"
                >
                  Delete
                </button>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
