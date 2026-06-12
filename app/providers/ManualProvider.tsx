"use client";

import {
  createContext,
  ReactNode,
  useContext,
  useState,
  useEffect,
  useCallback,
  useRef,
} from "react";

const apiUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export interface Manual {
  id: string;
  type: "pdf" | "url" | "github";
  name: string;
  status: "processing" | "ready" | "error";
  created_at?: string;
  error?: string;
}

export interface ManualContextType {
  manuals: Manual[];
  isUploading: boolean;
  uploadPdf: (file: File) => Promise<void>;
  addUrl: (url: string) => Promise<void>;
  addGithub: (url: string) => Promise<void>;
  deleteManual: (id: string) => Promise<void>;
  refreshManuals: () => Promise<void>;
  activeManualIds: string[];
  activeGuideManualIds: string[];
}

const ManualContext = createContext<ManualContextType | undefined>(undefined);

export function ManualProvider({ children }: { children: ReactNode }) {
  const [manuals, setManuals] = useState<Manual[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  const activeManualIds = manuals
    .filter((m) => m.status === "ready")
    .map((m) => m.id);

  const activeGuideManualIds = activeManualIds;

  const refreshManuals = useCallback(async () => {
    try {
      const response = await fetch(`${apiUrl}/manual/list`);
      if (response.ok) {
        const data = await response.json();
        setManuals(data.manuals || []);
      }
    } catch (e) {
      console.error("Error fetching manuals:", e);
    }
  }, []);

  useEffect(() => {
    refreshManuals();
  }, [refreshManuals]);

  useEffect(() => {
    const hasProcessing = manuals.some((m) => m.status === "processing");

    if (hasProcessing) {
      if (!pollingRef.current) {
        pollingRef.current = setInterval(() => {
          refreshManuals();
        }, 3000);
      }
    } else {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    };
  }, [manuals, refreshManuals]);

  const uploadPdf = async (file: File) => {
    setIsUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${apiUrl}/manual/upload`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.status}`);
      }

      await refreshManuals();
    } catch (e) {
      console.error("Error uploading PDF:", e);
      throw e;
    } finally {
      setIsUploading(false);
    }
  };

  const addUrl = async (url: string) => {
    setIsUploading(true);
    try {
      const response = await fetch(`${apiUrl}/manual/url`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Add URL failed: ${response.status}`);
      }

      await refreshManuals();
    } catch (e) {
      console.error("Error adding URL:", e);
      throw e;
    } finally {
      setIsUploading(false);
    }
  };

  const addGithub = async (url: string) => {
    setIsUploading(true);
    try {
      const response = await fetch(`${apiUrl}/manual/github`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        throw new Error(`Add GitHub failed: ${response.status}`);
      }

      await refreshManuals();
    } catch (e) {
      console.error("Error adding GitHub URL:", e);
      throw e;
    } finally {
      setIsUploading(false);
    }
  };

  const deleteManual = async (id: string) => {
    try {
      const response = await fetch(`${apiUrl}/manual/${id}`, {
        method: "DELETE",
      });

      if (!response.ok) {
        throw new Error(`Delete failed: ${response.status}`);
      }

      setManuals((prev) => prev.filter((m) => m.id !== id));
    } catch (e) {
      console.error("Error deleting manual:", e);
      throw e;
    }
  };

  return (
    <ManualContext.Provider
      value={{
        manuals,
        isUploading,
        uploadPdf,
        addUrl,
        addGithub,
        deleteManual,
        refreshManuals,
        activeManualIds,
        activeGuideManualIds,
      }}
    >
      {children}
    </ManualContext.Provider>
  );
}

export function useManuals() {
  const context = useContext(ManualContext);
  if (context === undefined) {
    throw new Error("useManuals must be used within a ManualProvider");
  }
  return context;
}
