"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useTasks } from "@/app/providers/TaskProvider";
import { useScreenShare } from "@/hooks/screenshare";
import { useTaskPip } from "@/hooks/pip";
import { TaskScreen } from "@/components/task-screen";
import { MinimalTaskScreen } from "@/components/task-screen";
import { ScreenshareModal } from "@/components/screenshare-modal";

export default function TaskPage() {
  const router = useRouter();
  const taskContext = useTasks();
  const {
    tasks,
    goal,
    setGoal,
    triggerFirstTask,
    resumeFromCheckpoint,
    isLoading,
    reset: resetTasks,
  } = taskContext;

  const { isSharing, requestScreenShare, stopSharing } = useScreenShare();
  const { isPipActive, openPipWindow } = useTaskPip();

  const [showModal, setShowModal] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    const storedGoal = sessionStorage.getItem("geolens-goal");
    if (!storedGoal) {
      router.push("/");
      return;
    }

    setGoal(storedGoal);
    const lang = sessionStorage.getItem("geolens-guide-language") || "en";
    taskContext.setGuideLanguage(lang);
    setShowModal(true);
  }, []);

  const handleConfirm = async () => {
    setIsStarting(true);
    const success = await requestScreenShare();

    if (success) {
      setShowModal(false);

      if (!hasStartedRef.current) {
        hasStartedRef.current = true;
        if (sessionStorage.getItem("geolens-resume-data")) {
          resumeFromCheckpoint();
        } else {
          triggerFirstTask();
        }
        openPipWindow();
      }
    }

    setIsStarting(false);
  };

  const handleClose = () => {
    setShowModal(false);
    router.push("/");
  };

  const handleStartOver = () => {
    stopSharing();
    resetTasks();
    sessionStorage.removeItem("geolens-goal");
    router.push("/");
  };

  if (isPipActive) {
    return <MinimalTaskScreen goal={goal} />;
  }

  return (
    <>
      <ScreenshareModal
        isOpen={showModal}
        onConfirm={handleConfirm}
        onClose={handleClose}
        isLoading={isStarting}
      />

      {isSharing && (
        <TaskScreen
          {...taskContext}
          tasks={tasks}
          goal={goal}
          isLoading={isLoading}
          onStartOver={handleStartOver}
          onTaskRefreshed={() => {}}
          onAllTasksCompleted={() => {}}
          isGuidePaused={taskContext.isGuidePaused}
          onToggleGuidePause={taskContext.toggleGuidePause}
        />
      )}
    </>
  );
}
