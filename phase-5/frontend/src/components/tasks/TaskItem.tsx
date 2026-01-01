/**
 * TaskItem component.
 * Neo-Editorial styled task card with priority, tags, due dates, reminders, recurrence.
 */
"use client";

import { useState } from "react";
import { Task, Priority } from "@/lib/api";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { EditTaskDialog } from "./EditTaskDialog";
import { DeleteTaskDialog } from "./DeleteTaskDialog";
import { TagChip } from "./TagChip";
import {
  Pencil,
  Trash2,
  Calendar,
  Bell,
  Repeat,
  AlertTriangle,
  ChevronUp,
  ChevronDown,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { format, isPast, parseISO } from "date-fns";

interface TaskItemProps {
  task: Task;
  onToggleComplete?: (taskId: string) => void;
  onTaskUpdated?: (task: Task) => void;
  onTaskDeleted?: (taskId: string) => void;
  searchQuery?: string;
}

const priorityConfig: Record<
  Priority,
  { color: string; bgColor: string; icon: React.ReactNode; label: string }
> = {
  high: {
    color: "text-red-600 dark:text-red-400",
    bgColor: "bg-red-500/10 border-red-500/20",
    icon: <ChevronUp className="h-3 w-3" />,
    label: "High",
  },
  medium: {
    color: "text-amber-600 dark:text-amber-400",
    bgColor: "bg-amber-500/10 border-amber-500/20",
    icon: <Minus className="h-3 w-3" />,
    label: "Medium",
  },
  low: {
    color: "text-emerald-600 dark:text-emerald-400",
    bgColor: "bg-emerald-500/10 border-emerald-500/20",
    icon: <ChevronDown className="h-3 w-3" />,
    label: "Low",
  },
};

const recurrenceLabels: Record<string, string> = {
  daily: "Daily",
  weekly: "Weekly",
  monthly: "Monthly",
};

function highlightText(text: string, query?: string): React.ReactNode {
  if (!query || !text) return text;

  const regex = new RegExp(
    `(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
    "gi"
  );
  const parts = text.split(regex);

  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="bg-accent/40 text-foreground rounded px-0.5">
        {part}
      </mark>
    ) : (
      part
    )
  );
}

export function TaskItem({
  task,
  onToggleComplete,
  onTaskUpdated,
  onTaskDeleted,
  searchQuery,
}: TaskItemProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const handleToggle = () => {
    if (onToggleComplete) {
      onToggleComplete(task.id);
    }
  };

  const isOverdue =
    task.due_date && isPast(parseISO(task.due_date)) && !task.is_completed;

  const formattedDueDate = task.due_date
    ? format(parseISO(task.due_date), "MMM d, yyyy")
    : null;

  const formattedReminder = task.remind_at
    ? format(parseISO(task.remind_at), "MMM d 'at' h:mm a")
    : null;

  const priorityInfo = priorityConfig[task.priority || "medium"];

  return (
    <>
      <div
        className={cn(
          "group relative flex items-start gap-4 p-5 rounded-xl border bg-card transition-all duration-300",
          "hover:shadow-elevated hover:-translate-y-0.5",
          task.is_completed && "opacity-50 bg-muted/20",
          isOverdue && !task.is_completed && "border-l-4 border-l-destructive"
        )}
      >
        {/* Checkbox */}
        <div className="pt-0.5">
          <Checkbox
            checked={task.is_completed}
            onCheckedChange={handleToggle}
            className="h-5 w-5 rounded-md border-2 data-[state=checked]:bg-primary data-[state=checked]:border-primary"
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0 space-y-3">
          {/* Title row */}
          <div className="flex items-start gap-2 flex-wrap">
            <h3
              className={cn(
                "font-medium text-foreground leading-snug",
                task.is_completed && "line-through text-muted-foreground"
              )}
            >
              {highlightText(task.title, searchQuery)}
            </h3>

            {/* Priority Badge */}
            {task.priority && task.priority !== "medium" && (
              <span
                className={cn(
                  "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium border",
                  priorityInfo.bgColor,
                  priorityInfo.color
                )}
              >
                {priorityInfo.icon}
                {priorityInfo.label}
              </span>
            )}

            {/* Overdue indicator */}
            {isOverdue && (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-destructive/10 text-destructive border border-destructive/20">
                <AlertTriangle className="h-3 w-3" />
                Overdue
              </span>
            )}
          </div>

          {/* Description */}
          {task.description && (
            <p
              className={cn(
                "text-sm text-muted-foreground leading-relaxed",
                task.is_completed && "line-through"
              )}
            >
              {highlightText(task.description, searchQuery)}
            </p>
          )}

          {/* Tags */}
          {task.tags && task.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {task.tags.map((tag) => (
                <TagChip key={tag} name={tag} size="sm" />
              ))}
            </div>
          )}

          {/* Metadata row */}
          <div className="flex flex-wrap items-center gap-4 text-xs text-muted-foreground">
            {/* Due Date */}
            {formattedDueDate && (
              <span
                className={cn(
                  "inline-flex items-center gap-1.5",
                  isOverdue && "text-destructive font-medium"
                )}
              >
                <Calendar className="h-3.5 w-3.5" />
                {formattedDueDate}
              </span>
            )}

            {/* Reminder */}
            {formattedReminder && !task.reminder_sent && (
              <span className="inline-flex items-center gap-1.5 text-info">
                <Bell className="h-3.5 w-3.5" />
                {formattedReminder}
              </span>
            )}

            {/* Recurrence */}
            {task.recurrence && task.recurrence !== "none" && (
              <span className="inline-flex items-center gap-1.5 text-purple-600 dark:text-purple-400">
                <Repeat className="h-3.5 w-3.5" />
                {recurrenceLabels[task.recurrence]}
              </span>
            )}
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsEditDialogOpen(true)}
            title="Edit task"
            className="h-8 w-8 rounded-lg text-muted-foreground hover:text-foreground hover:bg-muted"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsDeleteDialogOpen(true)}
            title="Delete task"
            className="h-8 w-8 rounded-lg text-muted-foreground hover:text-destructive hover:bg-destructive/10"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      <EditTaskDialog
        task={task}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onTaskUpdated={(updatedTask) => {
          if (onTaskUpdated) {
            onTaskUpdated(updatedTask);
          }
        }}
      />

      <DeleteTaskDialog
        task={task}
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onTaskDeleted={(taskId) => {
          if (onTaskDeleted) {
            onTaskDeleted(taskId);
          }
        }}
      />
    </>
  );
}
