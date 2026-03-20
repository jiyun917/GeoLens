"use client";

import { useScreenShare } from "@/hooks/screenshare";
import {
  generateAction,
  generateHelpResponse,
  generateCoordinate,
  parseCoordinates,
  createCoordinateSnapshot,
  FollowUpContext,
  checkStepCompletion,
  generateSummary,
  generatePlan,
} from "@/lib/ai";
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
import { getSystemInfo } from "@/lib/utils";
import { TaskHistoryItem, FollowUpItem } from "@/components/task-screen/types";

const MAX_STEPS = 150;

export interface TaskContextType {
  tasks: TaskHistoryItem[];
  totalTaskCount: number;
  hasExceededMaxSteps: boolean;

  goal: string;
  setGoal: (goal: string) => void;

  onNextTask: () => void;
  onRefreshTask: () => void;
  triggerFirstTask: () => void;
  resumeFromCheckpoint: () => void;
  returnToTask: (taskIndex: number) => void;

  isGuidePaused: boolean;
  toggleGuidePause: () => void;

  sendFollowUpMessage: (question?: string) => void;

  isLoading: boolean;
  isLoadingFollowUp: boolean;
  isAnalyzingScreen: boolean;

  isLoadingPreviewImage: boolean;

  autoCompleteTriggered: number;

  plan: string[];
  isPlanLoading: boolean;

  summaryReport: string;
  isGeneratingSummary: boolean;

  lastScreenshot: string;

  reset: () => void;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

export function TaskProvider({ children }: { children: ReactNode }) {
  const [goal, setGoal] = useState("");

  const { settings, isUsingLocalProvider } = useSettings();
  const { activeManualIds } = useManuals();

  const {
    captureImageFromStream,
    startChangeDetection,
    stopChangeDetection,
    pauseChangeDetection,
    resumeChangeDetection,
    pauseChangeDetectionTemporarily,
    setIsAnalyzingScreenChange,
    isAnalyzingScreenChange,
  } = useScreenShare();

  const [tasks, setTasks] = useState<TaskHistoryItem[]>([]);
  const tasksRef = useRef<TaskHistoryItem[]>([]);
  const [totalTaskCount, setTotalTaskCount] = useState(0);
  const [totalTaskGeneration, setTotalTaskGeneration] = useState(0);

  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingFollowUp, setIsLoadingFollowUp] = useState(false);
  const [isLoadingPreviewImage, setIsLoadingPreviewImage] = useState(false);
  const [autoCompleteTriggered, setAutoCompleteTriggered] = useState(0);

  const [plan, setPlan] = useState<string[]>([]);
  const [isPlanLoading, setIsPlanLoading] = useState(false);
  const [isGuidePaused, setIsGuidePaused] = useState(false);

  const [summaryReport, setSummaryReport] = useState("");
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const summaryGeneratedRef = useRef(false);

  const lastScreenshotRef = useRef<string>("");
  const pendingFollowUpRef = useRef<string>("");

  const isTriggeringRef = useRef(false);
  const changeDetectionStartedRef = useRef(false);
  const isCheckingStepRef = useRef(false);
  const pendingCheckImageRef = useRef<string | null>(null);
  const cancelPendingChecksRef = useRef(false);
  const checkVersionRef = useRef(0);

  // === Checkpoint ID for this session ===
  const checkpointIdRef = useRef<string>("");

  // === Auto-save checkpoint (array-based, multiple sessions) ===
  useEffect(() => {
    if (!goal || tasks.length === 0) return;

    // Generate a stable ID for this session
    if (!checkpointIdRef.current) {
      checkpointIdRef.current = `cp_${Date.now().toString(36)}`;
    }

    try {
      const raw = localStorage.getItem("geolens-guide-checkpoints");
      const all: Array<any> = raw ? JSON.parse(raw) : [];

      const entry = {
        id: checkpointIdRef.current,
        goal,
        plan,
        completedSteps: tasks.map((t) => t.text),
        timestamp: Date.now(),
      };

      // Update existing or add new
      const idx = all.findIndex((c: any) => c.id === entry.id);
      if (idx >= 0) {
        all[idx] = entry;
      } else {
        all.unshift(entry);
      }

      // Keep max 10
      localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(all.slice(0, 10)));
    } catch {
      // localStorage full or unavailable
    }
  }, [goal, tasks, plan]);

  // === Save completed workflow + remove checkpoint on completion ===
  useEffect(() => {
    if (tasks.length === 0) return;
    const lastTask = tasks[tasks.length - 1];
    const isDone = lastTask.text.toLowerCase().replace(".", "") === "done";
    if (!isDone || !goal) return;

    try {
      // Save to workflow history
      const raw = localStorage.getItem("geolens-workflow-history");
      const history: Array<{ goal: string; timestamp: number; stepCount: number }> = raw ? JSON.parse(raw) : [];
      if (!history.some((h) => h.goal === goal)) {
        history.unshift({ goal, timestamp: Date.now(), stepCount: tasks.length - 1 });
        localStorage.setItem("geolens-workflow-history", JSON.stringify(history.slice(0, 20)));
      }

      // Remove this session's checkpoint
      if (checkpointIdRef.current) {
        const cpRaw = localStorage.getItem("geolens-guide-checkpoints");
        if (cpRaw) {
          const all = JSON.parse(cpRaw).filter((c: any) => c.id !== checkpointIdRef.current);
          localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(all));
        }
      }
    } catch {
      // ignore
    }
  }, [tasks, goal]);

  const cancelPendingChecks = () => {
    checkVersionRef.current++;
    cancelPendingChecksRef.current = true;
    pendingCheckImageRef.current = null;
    isCheckingStepRef.current = false;
    setIsAnalyzingScreenChange(false);
  };

  const hasExceededMaxSteps = totalTaskGeneration >= MAX_STEPS;

  const triggerGenerateTaskDescription = async () => {
    if (hasExceededMaxSteps || isTriggeringRef.current) {
      return;
    }

    isTriggeringRef.current = true;
    setIsLoading(true);

    try {
      const captured = await captureImageFromStream({
        isLocalLlm: isUsingLocalProvider,
      });

      const imageDataUrl = captured.scaledImageDataUrl;
      const nonScaledImage = captured.nonScaledImageDataUrl;

      const osName = getSystemInfo().os.osName;

      let followUpContext: FollowUpContext | undefined;
      const currentTask = tasksRef.current[tasksRef.current.length - 1];
      if (
        pendingFollowUpRef.current &&
        lastScreenshotRef.current &&
        currentTask
      ) {
        followUpContext = {
          previousImage: lastScreenshotRef.current,
          previousInstruction: currentTask.text,
          followUpMessage: pendingFollowUpRef.current,
        };
        pendingFollowUpRef.current = "";

        tasksRef.current = tasksRef.current.slice(0, -1);
        setTasks(tasksRef.current);
        setTotalTaskCount((prev) => Math.max(0, prev - 1));
      }

      const action = await generateAction(
        goal,
        imageDataUrl,
        settings,
        tasksRef.current.map((item) => item.text),
        osName,
        followUpContext,
        activeManualIds.length > 0 ? activeManualIds : undefined,
        plan.length > 0 ? plan : undefined
      );

      lastScreenshotRef.current = imageDataUrl;

      setTotalTaskGeneration((prev) => prev + 1);

      const text = action.trim();

      setTotalTaskCount((prev) => prev + 1);

      const newTaskItem: TaskHistoryItem = { text };
      const newTasks = [...tasksRef.current, newTaskItem].filter(
        (item) => item.text
      );

      console.log(newTasks);
      tasksRef.current = newTasks;
      setTasks(newTasks);

      setIsLoading(false);

      const isLink = text.startsWith("https://");
      const textLower = text.toLowerCase();
      const isStandardizedInstruction =
        textLower === "done" ||
        textLower === "done." ||
        textLower === "wait" ||
        textLower === "wait." ||
        textLower.startsWith("scroll down") ||
        textLower.startsWith("scroll up");

      // Start change detection IMMEDIATELY (don't wait for coordinates)
      if (
        !changeDetectionStartedRef.current &&
        text &&
        textLower !== "done" &&
        textLower !== "done."
      ) {
        changeDetectionStartedRef.current = true;
        startChangeDetection(handleScreenChange);
      }

      // Release the triggering lock so "Done" button and checks can work
      isTriggeringRef.current = false;

      // Auto-generate summary report when task is complete
      if (
        (textLower === "done" || textLower === "done.") &&
        !summaryGeneratedRef.current
      ) {
        summaryGeneratedRef.current = true;
        setIsGeneratingSummary(true);
        generateSummary(
          goal,
          imageDataUrl,
          settings,
          tasksRef.current.map((item) => item.text).filter((t) => t.toLowerCase() !== "done" && t.toLowerCase() !== "done."),
          (streamed) => setSummaryReport(streamed),
          activeManualIds.length > 0 ? activeManualIds : undefined
        )
          .catch((e) => console.error("Summary generation error:", e))
          .finally(() => setIsGeneratingSummary(false));
      }

      // Generate coordinates in the background (non-blocking)
      if (!isLink && !isStandardizedInstruction && text) {
        setIsLoadingPreviewImage(true);
        generateCoordinate(text, nonScaledImage, settings)
          .then(async (coordinates) => {
            const coordinatePattern = /^-?\d+,\s*-?\d+$/;
            if (coordinates && coordinatePattern.test(coordinates.trim())) {
              const parsedCoordinates = parseCoordinates(coordinates);
              const generatedPreviewImage = await createCoordinateSnapshot(
                nonScaledImage,
                parsedCoordinates
              );

              if (generatedPreviewImage) {
                const lastIndex = tasksRef.current.length - 1;
                if (lastIndex >= 0) {
                  tasksRef.current[lastIndex] = {
                    ...tasksRef.current[lastIndex],
                    previewImage: generatedPreviewImage,
                  };
                  setTasks([...tasksRef.current]);
                }
              }
            }
          })
          .catch((e) => console.error("Coordinate generation error:", e))
          .finally(() => setIsLoadingPreviewImage(false));
      }
    } catch (e) {
      console.error(e);
    } finally {
      isTriggeringRef.current = false;
      setIsLoading(false);
    }
  };

  const handleScreenChange = async (scaledImage: string) => {
    if (isCheckingStepRef.current) {
      pendingCheckImageRef.current = scaledImage;
      return;
    }

    await processScreenChange(scaledImage);
  };

  const processScreenChange = async (scaledImage: string) => {
    const currentVersion = ++checkVersionRef.current;
    cancelPendingChecksRef.current = false;

    const currentTaskText = tasksRef.current[tasksRef.current.length - 1]?.text;
    if (!currentTaskText || isTriggeringRef.current) {
      setIsAnalyzingScreenChange(false);
      return;
    }

    const taskLower = currentTaskText.toLowerCase();
    if (taskLower === "done" || taskLower === "done.") {
      setIsAnalyzingScreenChange(false);
      return;
    }

    const isLink = currentTaskText.startsWith("https://");
    const isWait = taskLower === "wait";

    const taskDescription = isLink
      ? `Navigate to ${currentTaskText}`
      : isWait
      ? "Wait for the window to finish loading"
      : currentTaskText;

    isCheckingStepRef.current = true;

    try {
      if (!lastScreenshotRef.current) {
        isCheckingStepRef.current = false;
        setIsAnalyzingScreenChange(false);
        return;
      }

      const isCompleted = await checkStepCompletion(
        taskDescription,
        lastScreenshotRef.current,
        scaledImage,
        settings
      );

      if (currentVersion !== checkVersionRef.current) {
        return;
      }

      isCheckingStepRef.current = false;

      const pendingImage = pendingCheckImageRef.current;
      pendingCheckImageRef.current = null;

      if (isCompleted) {
        setIsAnalyzingScreenChange(false);
        if (!cancelPendingChecksRef.current) {
          setAutoCompleteTriggered((prev) => prev + 1);
        }
      } else if (pendingImage) {
        await processScreenChange(pendingImage);
      } else {
        setIsAnalyzingScreenChange(false);
      }
    } catch (e) {
      if (currentVersion !== checkVersionRef.current) {
        return;
      }
      console.error("Error in processScreenChange:", e);
      isCheckingStepRef.current = false;
      setIsAnalyzingScreenChange(false);
    }
  };

  const onNextTask = () => {
    if (hasExceededMaxSteps) return;
    cancelPendingChecks();
    triggerGenerateTaskDescription();
  };

  const onRefreshTask = () => {
    if (hasExceededMaxSteps) return;
    if (tasksRef.current.length > 0) {
      tasksRef.current = tasksRef.current.slice(0, -1);
      setTasks(tasksRef.current);
      setTotalTaskCount((prev) => Math.max(0, prev - 1));
    }
    triggerGenerateTaskDescription();
  };

  const triggerFirstTask = async () => {
    if (hasExceededMaxSteps) return;

    // Generate plan first, then start first task
    setIsPlanLoading(true);
    try {
      const captured = await captureImageFromStream({ isLocalLlm: isUsingLocalProvider });
      const steps = await generatePlan(
        goal,
        captured.scaledImageDataUrl,
        settings,
        activeManualIds.length > 0 ? activeManualIds : undefined
      );
      if (steps.length > 0) setPlan(steps);
    } catch (e) {
      console.error("Plan generation failed:", e);
    } finally {
      setIsPlanLoading(false);
    }

    triggerGenerateTaskDescription();
  };

  const resumeFromCheckpoint = () => {
    try {
      const raw = sessionStorage.getItem("geolens-resume-data");
      if (!raw) {
        triggerFirstTask();
        return;
      }
      sessionStorage.removeItem("geolens-resume-data");
      const data = JSON.parse(raw);
      if (data.plan?.length) setPlan(data.plan);
      if (data.completedSteps?.length) {
        const restored: TaskHistoryItem[] = data.completedSteps.map((text: string) => ({ text }));
        tasksRef.current = restored;
        setTasks(restored);
        setTotalTaskCount(restored.length);
        setTotalTaskGeneration(restored.length);
      }
      triggerGenerateTaskDescription();
    } catch (e) {
      console.error("Resume failed:", e);
      triggerFirstTask();
    }
  };

  const toggleGuidePause = () => {
    if (isGuidePaused) {
      resumeChangeDetection();
      setIsGuidePaused(false);
    } else {
      pauseChangeDetection();
      cancelPendingChecks();
      setIsGuidePaused(true);
    }
  };

  const returnToTask = (taskIndex: number) => {
    if (hasExceededMaxSteps) return;
    if (taskIndex < 0 || taskIndex >= tasksRef.current.length) return;

    isTriggeringRef.current = false;
    isCheckingStepRef.current = false;
    pendingCheckImageRef.current = null;
    setIsLoading(false);
    setIsLoadingPreviewImage(false);
    setIsAnalyzingScreenChange(false);

    pauseChangeDetectionTemporarily(2000);

    const newTasks = tasksRef.current.slice(0, taskIndex + 1);
    tasksRef.current = newTasks;
    setTasks(newTasks);
    setTotalTaskCount(newTasks.length);
  };

  const addFollowUpToCurrentTask = (followUp: FollowUpItem) => {
    const lastIndex = tasksRef.current.length - 1;
    if (lastIndex >= 0) {
      const currentTask = tasksRef.current[lastIndex];
      tasksRef.current[lastIndex] = {
        ...currentTask,
        followUps: [...(currentTask.followUps ?? []), followUp],
      };
      setTasks([...tasksRef.current]);
    }
  };

  const updateCurrentFollowUpAnswer = (answer: string) => {
    const lastTaskIndex = tasksRef.current.length - 1;
    if (lastTaskIndex >= 0) {
      const currentTask = tasksRef.current[lastTaskIndex];
      const followUps = currentTask.followUps ?? [];
      if (followUps.length > 0) {
        const lastFollowUpIndex = followUps.length - 1;
        followUps[lastFollowUpIndex] = {
          ...followUps[lastFollowUpIndex],
          answer,
        };
        tasksRef.current[lastTaskIndex] = {
          ...currentTask,
          followUps: [...followUps],
        };
        setTasks([...tasksRef.current]);
      }
    }
  };

  const removeLastFollowUpFromCurrentTask = () => {
    const lastTaskIndex = tasksRef.current.length - 1;
    if (lastTaskIndex >= 0) {
      const currentTask = tasksRef.current[lastTaskIndex];
      const followUps = currentTask.followUps ?? [];
      if (followUps.length > 0) {
        tasksRef.current[lastTaskIndex] = {
          ...currentTask,
          followUps: followUps.slice(0, -1),
        };
        setTasks([...tasksRef.current]);
      }
    }
  };

  const sendFollowUpMessage = async (question?: string) => {
    if (!question) return;

    setIsLoadingFollowUp(true);
    addFollowUpToCurrentTask({ question, answer: "" });

    try {
      const { scaledImageDataUrl: imageDataUrl } = await captureImageFromStream(
        { isLocalLlm: isUsingLocalProvider }
      );

      const currentTaskText =
        tasksRef.current[tasksRef.current.length - 1]?.text ?? "";

      await generateHelpResponse(
        goal,
        imageDataUrl,
        question,
        currentTaskText,
        settings,
        (streamedMessage) => {
          updateCurrentFollowUpAnswer(streamedMessage);
        }
      );
    } catch (e) {
      console.error(e);
      removeLastFollowUpFromCurrentTask();
    }

    setIsLoadingFollowUp(false);
  };

  const reset = () => {
    stopChangeDetection();
    changeDetectionStartedRef.current = false;
    isCheckingStepRef.current = false;
    pendingCheckImageRef.current = null;
    isTriggeringRef.current = false;
    summaryGeneratedRef.current = false;
    tasksRef.current = [];
    setTasks([]);
    setTotalTaskCount(0);
    setTotalTaskGeneration(0);
    setIsLoading(false);
    setIsLoadingFollowUp(false);
    setIsLoadingPreviewImage(false);
    setPlan([]);
    setIsPlanLoading(false);
    // Remove this session's checkpoint
    if (checkpointIdRef.current) {
      try {
        const raw = localStorage.getItem("geolens-guide-checkpoints");
        if (raw) {
          const all = JSON.parse(raw).filter((c: any) => c.id !== checkpointIdRef.current);
          localStorage.setItem("geolens-guide-checkpoints", JSON.stringify(all));
        }
      } catch { /* ignore */ }
      checkpointIdRef.current = "";
    }
    setSummaryReport("");
    setIsGeneratingSummary(false);
    lastScreenshotRef.current = "";
    pendingFollowUpRef.current = "";
    setGoal("");
  };

  const taskContext: TaskContextType = {
    tasks,
    totalTaskCount,
    hasExceededMaxSteps,
    goal,
    setGoal,
    onNextTask,
    onRefreshTask,
    triggerFirstTask,
    resumeFromCheckpoint,
    returnToTask,
    sendFollowUpMessage,

    isGuidePaused,
    toggleGuidePause,

    isLoading,
    isLoadingFollowUp,
    isAnalyzingScreen: isAnalyzingScreenChange,
    isLoadingPreviewImage,

    autoCompleteTriggered,

    plan,
    isPlanLoading,

    summaryReport,
    isGeneratingSummary,

    lastScreenshot: lastScreenshotRef.current,

    reset,
  };

  return (
    <TaskContext.Provider value={taskContext}>{children}</TaskContext.Provider>
  );
}

export function useTasks() {
  const context = useContext(TaskContext);
  if (context === undefined) {
    throw new Error("useTasks must be used within a TaskProvider");
  }
  return context;
}
