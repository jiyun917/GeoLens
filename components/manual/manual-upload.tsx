"use client";

import { useState, useRef, useCallback } from "react";
import { useManuals } from "@/app/providers/ManualProvider";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

type Tab = "pdf" | "url" | "github";

export const ManualUpload = ({ mode = "guide" }: { mode?: "guide" | "report" }) => {
  const { uploadPdf, addUrl, addGithub, isUploading } = useManuals();
  const [activeTab, setActiveTab] = useState<Tab>("pdf");
  const [urlInput, setUrlInput] = useState("");
  const [githubInput, setGithubInput] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = useCallback(
    async (file: File) => {
      if (!file.name.endsWith(".pdf")) {
        toast.error("Please select a PDF file");
        return;
      }

      try {
        await uploadPdf(file, mode);
        toast.success("PDF uploaded successfully");
      } catch {
        toast.error("Failed to upload PDF");
      }
    },
    [uploadPdf]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      const file = e.dataTransfer.files[0];
      if (file) {
        handleFileSelect(file);
      }
    },
    [handleFileSelect]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleUrlSubmit = async () => {
    if (!urlInput.trim()) return;

    try {
      await addUrl(urlInput.trim(), mode);
      setUrlInput("");
      toast.success("URL added successfully");
    } catch {
      toast.error("Failed to add URL");
    }
  };

  const handleGithubSubmit = async () => {
    if (!githubInput.trim()) return;

    try {
      await addGithub(githubInput.trim(), mode);
      setGithubInput("");
      toast.success("GitHub repository added successfully");
    } catch {
      toast.error("Failed to add GitHub repository");
    }
  };

  const tabs: { key: Tab; label: string }[] = [
    { key: "pdf", label: "PDF" },
    { key: "url", label: "URL" },
    { key: "github", label: "GitHub" },
  ];

  return (
    <div className="w-full">
      <div className="flex border-b border-gray-200 mb-4">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            onClick={() => setActiveTab(tab.key)}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === tab.key
                ? "text-black border-b-2 border-black"
                : "text-gray-500 hover:text-gray-700"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "pdf" && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging
              ? "border-black bg-gray-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFileSelect(file);
              e.target.value = "";
            }}
          />
          <p className="text-gray-600 mb-1">
            {isUploading ? "Uploading..." : "Drop a PDF here or click to browse"}
          </p>
          <p className="text-xs text-gray-400">PDF files only</p>
        </div>
      )}

      {activeTab === "url" && (
        <div className="flex gap-2">
          <input
            type="url"
            value={urlInput}
            onChange={(e) => setUrlInput(e.target.value)}
            placeholder="https://docs.example.com/guide"
            className="flex-1 px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-black"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleUrlSubmit();
            }}
          />
          <Button
            size="sm"
            onClick={handleUrlSubmit}
            disabled={isUploading || !urlInput.trim()}
          >
            {isUploading ? "Adding..." : "Add"}
          </Button>
        </div>
      )}

      {activeTab === "github" && (
        <div className="flex gap-2">
          <input
            type="url"
            value={githubInput}
            onChange={(e) => setGithubInput(e.target.value)}
            placeholder="https://github.com/user/repo"
            className="flex-1 px-3 py-2 border border-gray-200 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-black"
            onKeyDown={(e) => {
              if (e.key === "Enter") handleGithubSubmit();
            }}
          />
          <Button
            size="sm"
            onClick={handleGithubSubmit}
            disabled={isUploading || !githubInput.trim()}
          >
            {isUploading ? "Adding..." : "Add"}
          </Button>
        </div>
      )}
    </div>
  );
};
