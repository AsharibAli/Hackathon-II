/**
 * ModeToggle component.
 * Provides tabs/buttons to switch between CUI (Chat) and GUI (Tasks) modes.
 */
"use client";

import { MessageSquare, ListTodo } from "lucide-react";
import { cn } from "@/lib/utils";

export type AppMode = "chat" | "tasks";

interface ModeToggleProps {
  activeMode: AppMode;
  onModeChange: (mode: AppMode) => void;
  className?: string;
}

export function ModeToggle({ activeMode, onModeChange, className }: ModeToggleProps) {
  return (
    <div className={cn("flex items-center gap-1 p-1 bg-muted rounded-lg", className)}>
      <button
        onClick={() => onModeChange("chat")}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
          activeMode === "chat"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground hover:bg-background/50"
        )}
      >
        <MessageSquare className="h-4 w-4" />
        <span>Chat</span>
      </button>
      <button
        onClick={() => onModeChange("tasks")}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200",
          activeMode === "tasks"
            ? "bg-background text-foreground shadow-sm"
            : "text-muted-foreground hover:text-foreground hover:bg-background/50"
        )}
      >
        <ListTodo className="h-4 w-4" />
        <span>Tasks</span>
      </button>
    </div>
  );
}
