import { RefreshCw, Pause, Play } from "@geist-ui/icons";
import { useEffect, useState } from "react";
import { Button } from "../ui/button";
import {
  TaskCardBaseProps,
  TASK_CARD_BASE_CLASS,
  getTaskAnimationClass,
} from "./types";

export const TaskCardBase = ({
  children,
  animationKey = 0,
  taskHistoryLength = 0,
  showRefreshButton = false,
  onRefresh,
  actionButton,
  pauseButton,
  className = "",
  isAnalyzingScreen = false,
  footer,
  decreasePaddingButton,
}: TaskCardBaseProps) => {
  const animationClass = getTaskAnimationClass(taskHistoryLength, animationKey);
  const [showIndicator, setShowIndicator] = useState(false);
  const [isFadingOut, setIsFadingOut] = useState(false);
  const [isDoneDisabled, setIsDoneDisabled] = useState(false);

  useEffect(() => {
    const isDemo = localStorage.getItem("demo");

    setIsDoneDisabled(!!isDemo);
  }, []);

  useEffect(() => {
    if (isAnalyzingScreen) {
      setShowIndicator(true);
      setIsFadingOut(false);
    } else if (showIndicator) {
      setIsFadingOut(true);
      const timer = setTimeout(() => {
        setShowIndicator(false);
        setIsFadingOut(false);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [isAnalyzingScreen]);

  return (
    <div
      key={animationKey}
      className={`${TASK_CARD_BASE_CLASS} ${animationClass} ${className} ${
        decreasePaddingButton && isDoneDisabled ? "pb-0" : ""
      }`}
    >
      <div className="float-right -mt-1 -mr-1 flex gap-1">
        {pauseButton && (
          <Button
            onClick={pauseButton.onToggle}
            icon={pauseButton.isPaused ? <Play /> : <Pause />}
            variant="ghost"
            title={pauseButton.isPaused ? "Resume" : "Pause"}
          />
        )}
        {showRefreshButton && onRefresh && (
          <Button
            onClick={onRefresh}
            icon={<RefreshCw />}
            variant="ghost"
          />
        )}
      </div>
      {children}
      {actionButton && !isDoneDisabled && (
        <div className="mt-4 flex items-center justify-between gap-3">
          <Button
            size="sm"
            onClick={actionButton.onClick}
            leftIcon={actionButton.icon}
            disabled={actionButton.disabled}
          >
            {actionButton.label}
          </Button>
          {pauseButton?.isPaused ? (
            <span className="text-sm text-yellow-500">Paused</span>
          ) : showIndicator ? (
            <span
              className={`text-sm text-foreground/60 ${
                isFadingOut ? "animate-fade-out" : "animate-fade-in-pulse"
              }`}
            >
              Detecting changes...
            </span>
          ) : null}
        </div>
      )}
      {footer}
    </div>
  );
};
