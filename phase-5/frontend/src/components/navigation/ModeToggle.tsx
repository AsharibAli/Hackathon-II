/**
 * ModeToggle component.
 * Neo-Editorial styled toggle for switching between Chat and Tasks modes.
 */
"use client";

import { useRef, useEffect, useState } from "react";
import { MessageSquare, ListTodo } from "lucide-react";
import { cn } from "@/lib/utils";

export type AppMode = "chat" | "tasks";

interface ModeToggleProps {
  activeMode: AppMode;
  onModeChange: (mode: AppMode) => void;
  className?: string;
}

export function ModeToggle({
  activeMode,
  onModeChange,
  className,
}: ModeToggleProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chatRef = useRef<HTMLButtonElement>(null);
  const tasksRef = useRef<HTMLButtonElement>(null);
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0 });

  // Calculate indicator position based on active mode
  useEffect(() => {
    const activeRef = activeMode === "chat" ? chatRef : tasksRef;
    if (activeRef.current && containerRef.current) {
      const containerRect = containerRef.current.getBoundingClientRect();
      const activeRect = activeRef.current.getBoundingClientRect();
      setIndicatorStyle({
        left: activeRect.left - containerRect.left,
        width: activeRect.width,
      });
    }
  }, [activeMode]);

  return (
    <div
      ref={containerRef}
      className={cn(
        "relative flex items-center p-1 bg-muted/60 rounded-full border border-border/50",
        className
      )}
    >
      {/* Animated indicator */}
      <div
        className="absolute h-[calc(100%-8px)] bg-background rounded-full shadow-soft transition-all duration-300 ease-out-expo"
        style={{
          left: indicatorStyle.left,
          width: indicatorStyle.width,
        }}
      />

      {/* Chat button */}
      <button
        ref={chatRef}
        onClick={() => onModeChange("chat")}
        className={cn(
          "relative z-10 flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200",
          activeMode === "chat"
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground"
        )}
        aria-pressed={activeMode === "chat"}
      >
        <MessageSquare
          className={cn(
            "h-4 w-4 transition-transform duration-200",
            activeMode === "chat" && "scale-110"
          )}
        />
        <span className="hidden sm:inline">Chat</span>
      </button>

      {/* Tasks button */}
      <button
        ref={tasksRef}
        onClick={() => onModeChange("tasks")}
        className={cn(
          "relative z-10 flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-colors duration-200",
          activeMode === "tasks"
            ? "text-foreground"
            : "text-muted-foreground hover:text-foreground"
        )}
        aria-pressed={activeMode === "tasks"}
      >
        <ListTodo
          className={cn(
            "h-4 w-4 transition-transform duration-200",
            activeMode === "tasks" && "scale-110"
          )}
        />
        <span className="hidden sm:inline">Tasks</span>
      </button>
    </div>
  );
}
