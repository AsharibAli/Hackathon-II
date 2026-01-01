/**
 * TagChip component.
 * Neo-Editorial styled tag display with optional remove button.
 */
"use client";

import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface TagChipProps {
  name: string;
  onRemove?: () => void;
  className?: string;
  size?: "sm" | "md";
  variant?: "default" | "muted";
}

// Color palette for tags based on name hash
const tagColors = [
  { bg: "bg-blue-500/10", text: "text-blue-600 dark:text-blue-400", border: "border-blue-500/20" },
  { bg: "bg-emerald-500/10", text: "text-emerald-600 dark:text-emerald-400", border: "border-emerald-500/20" },
  { bg: "bg-violet-500/10", text: "text-violet-600 dark:text-violet-400", border: "border-violet-500/20" },
  { bg: "bg-amber-500/10", text: "text-amber-600 dark:text-amber-400", border: "border-amber-500/20" },
  { bg: "bg-rose-500/10", text: "text-rose-600 dark:text-rose-400", border: "border-rose-500/20" },
  { bg: "bg-cyan-500/10", text: "text-cyan-600 dark:text-cyan-400", border: "border-cyan-500/20" },
  { bg: "bg-orange-500/10", text: "text-orange-600 dark:text-orange-400", border: "border-orange-500/20" },
  { bg: "bg-pink-500/10", text: "text-pink-600 dark:text-pink-400", border: "border-pink-500/20" },
];

function getTagColor(name: string) {
  // Simple hash function to get consistent color for same tag name
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = ((hash << 5) - hash + name.charCodeAt(i)) | 0;
  }
  return tagColors[Math.abs(hash) % tagColors.length];
}

export function TagChip({
  name,
  onRemove,
  className,
  size = "sm",
  variant = "default",
}: TagChipProps) {
  const colors = variant === "default" ? getTagColor(name) : {
    bg: "bg-muted/80",
    text: "text-muted-foreground",
    border: "border-border/50",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full font-medium border transition-all duration-200",
        colors.bg,
        colors.text,
        colors.border,
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-3 py-1 text-sm",
        onRemove && "pr-1",
        className
      )}
    >
      <span className="opacity-70">#</span>
      {name}
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove();
          }}
          className={cn(
            "rounded-full transition-colors",
            size === "sm" ? "p-0.5 ml-0.5" : "p-1 ml-1",
            "hover:bg-black/10 dark:hover:bg-white/10"
          )}
          title={`Remove tag ${name}`}
        >
          <X className={size === "sm" ? "h-3 w-3" : "h-3.5 w-3.5"} />
        </button>
      )}
    </span>
  );
}
