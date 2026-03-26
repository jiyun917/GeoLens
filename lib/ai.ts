import { ApiSettings, PROVIDER_URLS } from "@/app/providers/SettingsProvider";
import {
  buildActionPrompt,
  buildHelpPrompt,
  buildCheckPrompt,
  buildCoordinatePrompt,
  buildReportPrompt,
  buildSummaryPrompt,
} from "./prompts";
import type { ReportLanguage, ReportTemplate } from "./prompts/report";

export const aiApiUrl =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

export const chatId = crypto.randomUUID?.()
  ?? crypto.getRandomValues(new Uint8Array(16))
       .reduce((s, b) => s + b.toString(16).padStart(2, '0'), '');

export async function readStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onStream?: (message: string) => void
): Promise<string> {
  const decoder = new TextDecoder();
  let result = "";
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine === "data: [DONE]") continue;

        if (trimmedLine.startsWith("data: ")) {
          const dataContent = trimmedLine.slice(6);
          try {
            const parsed = JSON.parse(dataContent);
            if (parsed.type === "text-delta") {
              result += parsed.delta;
              onStream?.(result);
            }
          } catch (e) {
            console.error("Error parsing JSON:", e);
          }
        }
      }
    }

    if (buffer.trim()) {
      const trimmedLine = buffer.trim();
      if (trimmedLine.startsWith("data: ") && trimmedLine !== "data: [DONE]") {
        const dataContent = trimmedLine.slice(6);
        try {
          const parsed = JSON.parse(dataContent);
          if (parsed.type === "text-delta") {
            result += parsed.delta;
          }
        } catch (e) {
          console.error("Error parsing JSON from buffer:", e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return result;
}

async function readOpenAIStream(
  reader: ReadableStreamDefaultReader<Uint8Array>,
  onStream?: (message: string) => void
): Promise<string> {
  const decoder = new TextDecoder();
  let result = "";
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || "";

      for (const line of lines) {
        const trimmedLine = line.trim();
        if (!trimmedLine || trimmedLine === "data: [DONE]") continue;

        if (trimmedLine.startsWith("data: ")) {
          const dataContent = trimmedLine.slice(6);
          try {
            const parsed = JSON.parse(dataContent);
            const content = parsed.choices?.[0]?.delta?.content;
            if (content) {
              result += content;
              onStream?.(result);
            }
          } catch (e) {
            console.error("Error parsing OpenAI JSON:", e);
          }
        }
      }
    }

    if (buffer.trim()) {
      const trimmedLine = buffer.trim();
      if (trimmedLine.startsWith("data: ") && trimmedLine !== "data: [DONE]") {
        const dataContent = trimmedLine.slice(6);
        try {
          const parsed = JSON.parse(dataContent);
          const content = parsed.choices?.[0]?.delta?.content;
          if (content) {
            result += content;
          }
        } catch (e) {
          console.error("Error parsing OpenAI JSON from buffer:", e);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  return result;
}

export interface FollowUpContext {
  previousImage: string;
  previousInstruction: string;
  followUpMessage: string;
}

type MessageContent =
  | string
  | Array<{ type: string; text?: string; image_url?: { url: string } }>;
type Message = { role: string; content: MessageContent };

async function sendToBackend(
  endpoint: string,
  messages: Message[],
  onStream?: (message: string) => void,
  body?: Record<string, unknown>
): Promise<string> {
  const response = await fetch(`${aiApiUrl}/${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ messages, ...body }),
  });

  if (!response.ok) {
    throw new Error(`Backend request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) return "";

  return readStream(reader, onStream);
}

async function sendDirectToApi(
  messages: Message[],
  settings: ApiSettings,
  onStream?: (message: string) => void
): Promise<string> {
  if (!settings.provider) {
    throw new Error("No provider configured");
  }

  const baseUrl = PROVIDER_URLS[settings.provider];
  const response = await fetch(`${baseUrl}/v1/chat/completions`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      messages,
      model: settings.model,
      stream: true,
    }),
  });

  if (!response.ok) {
    throw new Error(`Direct API request failed: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) return "";

  return readOpenAIStream(reader, onStream);
}

const shouldUseDirectApi = (settings: ApiSettings): boolean => {
  return Boolean(settings.provider && settings.model);
};

export async function generatePlan(
  goal: string,
  base64Image: string,
  settings: ApiSettings,
  manualIds?: string[]
): Promise<string[]> {
  const systemPrompt = `You are a task planning assistant. Create a step-by-step plan based on the user's goal, the current screen, and any reference manual context.

# Goal
${goal}

# Rules
- Look at the SCREENSHOT carefully. Identify which software is open and what state it is in.
- SIMPLEST SOLUTION FIRST: Before creating a complex plan, consider if the goal can be achieved by simply restarting the program, creating a new project, or using a reset/clear function. If so, the plan should be 2-3 steps, not 10.
- ANALYZE THE GOAL: Break complex goals into concrete sub-tasks.
  - If the goal involves doing something to MULTIPLE items (e.g., "delete all scenes", "close all tabs"), list each deletion/action as a separate step OR write "Repeat: delete each item one by one" as a step.
  - If the goal has a PRECONDITION (e.g., "delete old ones so the next one starts at 1"), identify both the cleanup steps AND the verification step.
  - If the goal has CAUSE and EFFECT (e.g., "delete X so that Y happens"), plan steps for X and add a final step to verify Y.
- Plan ONLY steps that are relevant to this specific software and its current state.
- Use terminology visible in the screenshot or described in the manual context. Do NOT guess menu names.
- List 3-10 steps in logical order.
- Each step: short phrase (under 12 words).
- Output ONLY the numbered list, nothing else.`;

  const userContent: Array<Record<string, unknown>> = [
    { type: "text", text: "Create a step plan for this goal." },
  ];
  if (base64Image) {
    userContent.push({ type: "image_url", image_url: { url: base64Image } });
  }

  const messages: Message[] = [
    { role: "system", content: systemPrompt },
    { role: "user", content: userContent },
  ];

  try {
    let result: string;
    if (shouldUseDirectApi(settings)) {
      result = (await sendDirectToApi(messages, settings)) || "";
    } else {
      result = (await sendToBackend("step", messages, undefined, { manual_ids: manualIds })) || "";
    }

    // Parse numbered list
    const steps = result
      .split("\n")
      .map((line) => line.replace(/^\d+[\.\)]\s*/, "").trim())
      .filter((line) => line.length > 0 && line.length < 100);

    return steps.length > 0 ? steps : [];
  } catch (e) {
    console.error("Plan generation failed:", e);
    return [];
  }
}

export async function generateAction(
  goal: string,
  base64Image: string,
  settings: ApiSettings,
  completedSteps?: string[],
  osName?: string,
  followUpContext?: FollowUpContext,
  manualIds?: string[],
  plan?: string[],
  language?: string
) {
  const maxRetries = 3;
  let lastError: unknown;

  const systemPrompt = buildActionPrompt(goal, osName, completedSteps, undefined, plan, language);

  let messages: Message[];

  if (followUpContext) {
    messages = [
      { role: "system", content: systemPrompt },
      {
        role: "user",
        content: [{ type: "text", text: "[Previous Screenshot]" }],
      },
      {
        role: "assistant",
        content: followUpContext.previousInstruction,
      },
      {
        role: "user",
        content: [
          { type: "text", text: followUpContext.followUpMessage },
          { type: "image_url", image_url: { url: base64Image } },
        ],
      },
    ];
  } else {
    messages = [{ role: "system", content: systemPrompt }];

    if (completedSteps && completedSteps.length > 0) {
      // Only include the last 3 steps as conversation turns to keep context focused
      const recentSteps = completedSteps.slice(-3);
      for (const step of recentSteps) {
        messages.push({ role: "user", content: "[Screenshot]" });
        messages.push({ role: "assistant", content: step });
      }
    }

    // Current screenshot — include a brief state summary to ground the AI
    const stepCount = completedSteps?.length || 0;
    const stateHint = stepCount > 0
      ? `This is step ${stepCount + 1}. Look at the screenshot and give the next instruction.`
      : "This is the first step. Look at the screenshot and give the first instruction.";

    messages.push({
      role: "user",
      content: [
        { type: "text", text: stateHint },
        { type: "image_url", image_url: { url: base64Image } },
      ],
    });
  }

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      if (shouldUseDirectApi(settings)) {
        return await sendDirectToApi(messages, settings);
      } else {
        return await sendToBackend("step", messages, undefined, {
          manual_ids: manualIds,
        });
      }
    } catch (e) {
      lastError = e;
      console.error(
        `Error generating action (attempt ${attempt + 1}/${maxRetries + 1}):`,
        e
      );
      if (attempt < maxRetries) {
        await new Promise((resolve) =>
          setTimeout(resolve, 1000 * (attempt + 1))
        );
      }
    }
  }

  console.error("All retry attempts failed for generateAction:", lastError);
  return "";
}

export async function generateHelpResponse(
  goal: string,
  base64Image: string,
  userQuestion: string,
  previousMessage: string,
  settings: ApiSettings,
  onStream?: (message: string) => void
) {
  try {
    const systemPrompt = buildHelpPrompt(goal, previousMessage || undefined);

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      {
        role: "user",
        content: [
          { type: "text", text: userQuestion },
          { type: "image_url", image_url: { url: base64Image } },
        ],
      },
    ];

    if (shouldUseDirectApi(settings)) {
      return await sendDirectToApi(messages, settings, onStream);
    } else {
      return await sendToBackend("help", messages, onStream);
    }
  } catch (e) {
    console.error("Error generating help response:", e);
    return "";
  }
}

export async function checkStepCompletion(
  currentInstruction: string,
  lastBase64Image: string,
  currentBase64Image: string,
  settings: ApiSettings
): Promise<boolean> {
  try {
    const systemPrompt = buildCheckPrompt(currentInstruction);

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      {
        role: "user",
        content: [
          { type: "text", text: "Before:" },
          { type: "image_url", image_url: { url: lastBase64Image } },
          { type: "text", text: "After:" },
          { type: "image_url", image_url: { url: currentBase64Image } },
        ],
      },
    ];

    let text: string;
    if (shouldUseDirectApi(settings)) {
      text = await sendDirectToApi(messages, settings);
    } else {
      text = await sendToBackend("check", messages);
    }

    const cleanText = text.replace(/```json\n|\n```/g, "").trim();

    console.log(cleanText);

    return cleanText.toLowerCase().includes("yes");
  } catch (e) {
    console.error("Error checking step completion:", e);
    return false;
  }
}

export async function generateCoordinate(
  instruction: string,
  base64Image: string,
  settings: ApiSettings
) {
  try {
    const systemPrompt = buildCoordinatePrompt(instruction);

    const messages: Message[] = [
      { role: "system", content: systemPrompt },
      {
        role: "user",
        content: [{ type: "image_url", image_url: { url: base64Image } }],
      },
    ];

    let text: string;
    if (shouldUseDirectApi(settings)) {
      text = await sendDirectToApi(messages, settings);
    } else {
      text = await sendToBackend("coordinates", messages);
    }

    return text.trim();
  } catch (e) {
    console.error("Error generating coordinates:", e);
    return "None";
  }
}

interface Coordinates {
  x: number;
  y: number;
}

export const parseCoordinates = (output: string): Coordinates => {
  const [xStr, yStr] = output.split(",");
  return {
    x: parseInt(xStr, 10),
    y: parseInt(yStr, 10),
  };
};

export async function generateSummary(
  goal: string,
  base64Image: string,
  settings: ApiSettings,
  completedSteps?: string[],
  onStream?: (message: string) => void,
  manualIds?: string[]
) {
  const systemPrompt = buildSummaryPrompt(goal, completedSteps);

  const messages: Message[] = [
    { role: "system", content: systemPrompt },
    {
      role: "user",
      content: [
        { type: "text", text: "Please analyze the final result shown on screen." },
        { type: "image_url", image_url: { url: base64Image } },
      ],
    },
  ];

  try {
    if (shouldUseDirectApi(settings)) {
      return await sendDirectToApi(messages, settings, onStream);
    } else {
      return await sendToBackend("report", messages, onStream, {
        manual_ids: manualIds,
      });
    }
  } catch (e) {
    console.error("Error generating summary:", e);
    return "";
  }
}

export interface GeoAnnotation {
  id: string;
  feature_type: string;
  label: string;
  confidence: "high" | "medium" | "low";
  geometry: {
    type: "bbox" | "point" | "line";
    x?: number;
    y?: number;
    width?: number;
    height?: number;
    points?: Array<{ x: number; y: number }>;
  };
  description?: string;
}

export async function requestAnnotations(
  image: string,
  dataType: string,
  description: string,
  topic: string
): Promise<GeoAnnotation[]> {
  try {
    const response = await fetch(`${aiApiUrl}/annotate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image, data_type: dataType, description, topic }),
    });

    if (!response.ok) return [];

    const data = await response.json();
    return data.annotations || [];
  } catch (e) {
    console.error("Annotation request failed:", e);
    return [];
  }
}

export async function generateReport(
  topic: string,
  capturedImages: { image: string; description: string; dataType?: string }[],
  settings: ApiSettings,
  onStream?: (message: string) => void,
  manualIds?: string[],
  language: ReportLanguage = "ko",
  template: ReportTemplate = "detailed",
  customSections?: string[]
) {
  const systemPrompt = buildReportPrompt(
    topic,
    capturedImages.map((c) => ({
      description: c.description,
      dataType: c.dataType || "other",
    })),
    language,
    template,
    customSections
  );

  const imageContent: Array<{
    type: string;
    text?: string;
    image_url?: { url: string };
  }> = [];

  capturedImages.forEach((capture, i) => {
    const typeLabel = capture.dataType || "other";
    imageContent.push({
      type: "text",
      text: `[Capture ${i + 1} (${typeLabel}): ${capture.description}]`,
    });
    imageContent.push({
      type: "image_url",
      image_url: { url: capture.image },
    });
  });

  const messages: Message[] = [
    { role: "system", content: systemPrompt },
    { role: "user", content: imageContent },
  ];

  try {
    if (shouldUseDirectApi(settings)) {
      return await sendDirectToApi(messages, settings, onStream);
    } else {
      return await sendToBackend("report", messages, onStream, {
        manual_ids: manualIds,
      });
    }
  } catch (e) {
    console.error("Error generating report:", e);
    return "";
  }
}

export async function regenerateSection(
  topic: string,
  capturedImages: { image: string; description: string; dataType?: string }[],
  fullReport: string,
  sectionTitle: string,
  settings: ApiSettings,
  onStream?: (message: string) => void,
  _manualIds?: string[],
  language: ReportLanguage = "ko"
) {
  // Extract only the target section
  const sectionRegex = new RegExp(
    `## ${sectionTitle.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")}\\n[\\s\\S]*?(?=\\n## |$)`
  );
  const currentSection = fullReport.match(sectionRegex)?.[0] || "";

  const captureDesc = capturedImages
    .map((c, i) => `Capture ${i + 1} (${c.dataType || "other"}): ${c.description}`)
    .join("; ");

  const isEn = language === "en";
  const prompt = isEn
    ? `Rewrite this report section to be more detailed and accurate.

## Format Rules (MUST follow exactly)
- Start with "## ${sectionTitle}"
- Use bullet points only (- prefix)
- Every bullet MUST end with a confidence tag: [Confidence: High], [Confidence: Medium], or [Confidence: Low]
- Keep it concise: 1-2 sentences per bullet
- Example format:
  - Observation or interpretation here [Confidence: High]
  - Another point with reasoning [Confidence: Medium]

Topic: ${topic}
Data: ${captureDesc}

Current section to improve:
${currentSection}`
    : `이 보고서 섹션을 더 상세하고 정확하게 다시 작성하세요.

## 형식 규칙 (반드시 준수)
- "## ${sectionTitle}" 헤더로 시작
- 개조식(bullet point)으로만 작성 (- 접두사)
- 모든 항목 끝에 반드시 신뢰도 태그: [신뢰도: 높음], [신뢰도: 중간], [신뢰도: 낮음]
- 각 항목 1-2문장으로 간결하게
- 형식 예시:
  - 관찰 또는 해석 내용 [신뢰도: 높음]
  - 근거를 포함한 해석 [신뢰도: 중간]

주제: ${topic}
자료: ${captureDesc}

개선할 현재 섹션:
${currentSection}`;

  const messages: Message[] = [
    { role: "user", content: prompt },
  ];

  try {
    if (shouldUseDirectApi(settings)) {
      return await sendDirectToApi(messages, settings, onStream);
    } else {
      // Use /api/help (lightweight, no RAG) instead of /api/report
      return await sendToBackend("help", messages, onStream);
    }
  } catch (e) {
    console.error("Error regenerating section:", e);
    return "";
  }
}

export const createCoordinateSnapshot = async (
  imageDataUrl: string,
  { x, y }: Coordinates,
  sizePercentY = 15,
  xToYRatio = 2.5
): Promise<string | null> => {
  if (x < 0 || y < 0) return null;

  const img = new Image();
  img.src = imageDataUrl;
  await new Promise<void>((resolve) => {
    img.onload = () => resolve();
  });

  const sizePercentX = sizePercentY * xToYRatio;
  const outputWidth = Math.round((sizePercentX / 100) * img.width);
  const outputHeight = Math.round((sizePercentY / 100) * img.height);

  const imageX = (x / 999) * img.width;
  const imageY = (y / 999) * img.height;

  const halfCropX = outputWidth / 2;
  const halfCropY = outputHeight / 2;

  const cropX = Math.max(
    0,
    Math.min(imageX - halfCropX, img.width - outputWidth)
  );
  const cropY = Math.max(
    0,
    Math.min(imageY - halfCropY, img.height - outputHeight)
  );

  const canvas = document.createElement("canvas");
  canvas.width = outputWidth;
  canvas.height = outputHeight;
  const ctx = canvas.getContext("2d");

  if (!ctx) return null;

  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";

  ctx.drawImage(
    img,
    cropX,
    cropY,
    outputWidth,
    outputHeight,
    0,
    0,
    outputWidth,
    outputHeight
  );

  const cursorX = imageX - cropX + 5;
  const cursorY = imageY - cropY - 5;

  // Draw cursor pointer directly (no external image needed)
  const s = 40; // cursor size
  ctx.save();
  ctx.translate(cursorX, cursorY);
  // Pointer arrow shape
  ctx.beginPath();
  ctx.moveTo(0, 0);
  ctx.lineTo(0, s * 0.85);
  ctx.lineTo(s * 0.25, s * 0.65);
  ctx.lineTo(s * 0.45, s);
  ctx.lineTo(s * 0.55, s * 0.9);
  ctx.lineTo(s * 0.35, s * 0.55);
  ctx.lineTo(s * 0.6, s * 0.55);
  ctx.closePath();
  ctx.fillStyle = "#ef4444";
  ctx.fill();
  ctx.strokeStyle = "white";
  ctx.lineWidth = 2;
  ctx.stroke();
  // Red circle highlight
  ctx.beginPath();
  ctx.arc(s * 0.15, s * 0.15, s * 0.5, 0, Math.PI * 2);
  ctx.strokeStyle = "#ef4444";
  ctx.lineWidth = 3;
  ctx.globalAlpha = 0.4;
  ctx.stroke();
  ctx.globalAlpha = 1;
  ctx.restore();

  return canvas.toDataURL("image/png");
};
