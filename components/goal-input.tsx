"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { MultimodalInput } from "./multimodal-input";

export type GuideLanguage = "ko" | "en";

export const GoalInput = () => {
  const [input, setInput] = useState("");
  const [guideLang, setGuideLang] = useState<GuideLanguage>("ko");
  const router = useRouter();

  const handleSubmit = (
    event?: { preventDefault?: () => void },
    suggestedInput?: string
  ) => {
    event?.preventDefault?.();
    const goalText = suggestedInput || input;
    if (!goalText.trim()) return;

    sessionStorage.setItem("geolens-goal", goalText.trim());
    sessionStorage.setItem("geolens-guide-language", guideLang);
    router.push("/task");
  };

  return (
    <div>
      <div className="flex justify-center mb-4">
        <div className="inline-flex rounded-full border border-gray-700 bg-zinc-900 p-0.5">
          {([["ko", "한국어"], ["en", "English"]] as const).map(([id, label]) => (
            <button
              key={id}
              onClick={() => setGuideLang(id)}
              className={`px-4 py-1.5 rounded-full text-xs font-medium transition-colors ${
                guideLang === id
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
      </div>

      <MultimodalInput
        input={input}
        setInput={setInput}
        handleSubmit={handleSubmit}
        isLoading={false}
        messages={[]}
        placeholderText="What do you need help with?"
        showSuggestions
        onSuggestedActionClicked={(action) => {
          setInput(action);
        }}
      />
    </div>
  );
};
