"use client";

import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { useReport } from "@/app/providers/ReportProvider";
import { useScreenShare } from "@/hooks/screenshare";
import { ScreenshareModal } from "@/components/screenshare-modal";
import { ReportScreen } from "@/components/report-screen";

export default function ReportPage() {
  const router = useRouter();
  const report = useReport();
  const { topic, setTopic, reset: resetReport } = report;

  const { isSharing, requestScreenShare, stopSharing } = useScreenShare();

  const [showModal, setShowModal] = useState(false);
  const [isStarting, setIsStarting] = useState(false);
  const hasStartedRef = useRef(false);

  useEffect(() => {
    // Check if resuming from a report checkpoint
    const checkpointId = sessionStorage.getItem("geolens-report-checkpoint-id");
    if (checkpointId) {
      sessionStorage.removeItem("geolens-report-checkpoint-id");
      report.loadFromCheckpoint(checkpointId);
      setShowModal(true);
      return;
    }

    // Check if loading an existing project
    const projectId = sessionStorage.getItem("geolens-project-id");
    if (projectId) {
      sessionStorage.removeItem("geolens-project-id");
      report.loadProject(projectId).then(() => {
        setShowModal(true);
      });
      return;
    }

    const storedTopic = sessionStorage.getItem("geolens-report-topic");
    if (!storedTopic) {
      router.push("/");
      return;
    }

    setTopic(storedTopic);

    // Check if coming from guide mode with a screenshot
    const guideScreenshot = sessionStorage.getItem("geolens-guide-screenshot");
    if (guideScreenshot) {
      sessionStorage.removeItem("geolens-guide-screenshot");
      report.addCapture(guideScreenshot, "Guide mode final screen", "other");
    }

    setShowModal(true);
  }, []);

  const handleConfirm = async () => {
    setIsStarting(true);
    const success = await requestScreenShare();

    if (success) {
      setShowModal(false);
      hasStartedRef.current = true;
    }

    setIsStarting(false);
  };

  const handleClose = () => {
    setShowModal(false);
    router.push("/");
  };

  const handleStartOver = () => {
    stopSharing();
    resetReport();
    sessionStorage.removeItem("geolens-report-topic");
    router.push("/");
  };

  return (
    <>
      <ScreenshareModal
        isOpen={showModal}
        onConfirm={handleConfirm}
        onClose={handleClose}
        isLoading={isStarting}
      />

      {isSharing && (
        <ReportScreen
          {...report}
          onStartOver={handleStartOver}
        />
      )}
    </>
  );
}
