"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MultimodalInput } from "./multimodal-input";

export type GeoLensMode = "guide" | "report";

export const GoalInput = () => {
  const [input, setInput] = useState("");
  const [mode, setMode] = useState<GeoLensMode>("guide");
  const router = useRouter();

  const handleSubmit = (
    event?: { preventDefault?: () => void },
    suggestedInput?: string
  ) => {
    event?.preventDefault?.();
    const goalText = suggestedInput || input;
    if (!goalText.trim()) return;

    if (mode === "guide") {
      sessionStorage.setItem("geolens-goal", goalText.trim());
      router.push("/task");
    } else {
      sessionStorage.setItem("geolens-report-topic", goalText.trim());
      router.push("/report");
    }
  };

  return (
    <div>
      {/* Mode toggle */}
      <div className="flex justify-center mb-4">
        <div className="inline-flex rounded-full border border-gray-700 bg-zinc-900 p-1">
          <button
            onClick={() => setMode("guide")}
            className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === "guide"
                ? "bg-white text-black"
                : "text-gray-400 hover:text-white"
            }`}
          >
            Guide Mode
          </button>
          <button
            onClick={() => setMode("report")}
            className={`px-5 py-2 rounded-full text-sm font-medium transition-colors ${
              mode === "report"
                ? "bg-white text-black"
                : "text-gray-400 hover:text-white"
            }`}
          >
            Report Mode
          </button>
        </div>
      </div>

      <MultimodalInput
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        isLoading={false}
        messages={[]}
        placeholderText={
          mode === "guide"
            ? "What do you need help with?"
            : "What data do you want to interpret?"
        }
        showSuggestions
        customSuggestions={
          mode === "report"
            ? [
                { text: "Viking Graben seismic interpretation", icon: "monitor" },
                { text: "Well log reservoir evaluation", icon: "monitor" },
                { text: "Gravity anomaly map analysis", icon: "globe" },
              ]
            : undefined
        }
        onSuggestedActionClicked={(action) => {
          setInput(action);
        }}
      />
    </div>
  );
};
