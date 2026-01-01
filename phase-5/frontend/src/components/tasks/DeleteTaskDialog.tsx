/**
 * DeleteTaskDialog component.
 * Neo-Editorial styled confirmation dialog for deleting tasks.
 */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Task, tasksApi, ApiError } from "@/lib/api";
import { toast } from "sonner";
import { Trash2, AlertTriangle, Calendar, Tag } from "lucide-react";
import { cn } from "@/lib/utils";
import { format, parseISO } from "date-fns";

interface DeleteTaskDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskDeleted: (taskId: string) => void;
}

export function DeleteTaskDialog({
  task,
  open,
  onOpenChange,
  onTaskDeleted,
}: DeleteTaskDialogProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleDelete = async () => {
    setIsLoading(true);

    try {
      await tasksApi.delete(task.id);
      toast.success("Task deleted successfully!");
      onTaskDeleted(task.id);
      onOpenChange(false);
    } catch (error) {
      if (error instanceof ApiError) {
        toast.error(error.data?.detail || "Failed to delete task");
      } else {
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const formattedDueDate = task.due_date
    ? format(parseISO(task.due_date), "MMM d, yyyy")
    : null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md rounded-2xl border-border/60 p-0 overflow-hidden">
        {/* Header with warning color */}
        <DialogHeader className="px-6 pt-6 pb-4 bg-destructive/5 border-b border-destructive/10">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-xl bg-destructive/10 flex items-center justify-center">
              <Trash2 className="h-6 w-6 text-destructive" />
            </div>
            <div>
              <DialogTitle className="font-display text-lg font-semibold text-destructive">
                Delete Task
              </DialogTitle>
              <DialogDescription className="text-sm">
                This action cannot be undone
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <div className="p-6 space-y-4">
          {/* Warning message */}
          <div className="flex items-start gap-3 p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-amber-700 dark:text-amber-300">
              Are you sure you want to delete this task? All associated data
              including tags, reminders, and history will be permanently
              removed.
            </p>
          </div>

          {/* Task preview */}
          <div className="rounded-xl border border-border/60 bg-muted/30 p-4 space-y-3">
            <h4 className="font-medium text-foreground leading-snug">
              {task.title}
            </h4>

            {task.description && (
              <p className="text-sm text-muted-foreground line-clamp-2">
                {task.description}
              </p>
            )}

            <div className="flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              {formattedDueDate && (
                <span className="inline-flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5" />
                  {formattedDueDate}
                </span>
              )}

              {task.tags && task.tags.length > 0 && (
                <span className="inline-flex items-center gap-1.5">
                  <Tag className="h-3.5 w-3.5" />
                  {task.tags.length} tag{task.tags.length !== 1 ? "s" : ""}
                </span>
              )}

              <span
                className={cn(
                  "inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium",
                  task.priority === "high" &&
                    "bg-red-500/10 text-red-600 dark:text-red-400",
                  task.priority === "medium" &&
                    "bg-amber-500/10 text-amber-600 dark:text-amber-400",
                  task.priority === "low" &&
                    "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                )}
              >
                {task.priority
                  ? task.priority.charAt(0).toUpperCase() +
                    task.priority.slice(1)
                  : "Medium"}{" "}
                priority
              </span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <DialogFooter className="px-6 py-4 bg-muted/30 border-t border-border/50 gap-2">
          <Button
            type="button"
            variant="outline"
            onClick={() => onOpenChange(false)}
            disabled={isLoading}
            className="rounded-lg"
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleDelete}
            disabled={isLoading}
            className="rounded-lg gap-2"
          >
            {isLoading ? (
              <>
                <div className="h-4 w-4 rounded-full border-2 border-destructive-foreground border-t-transparent animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="h-4 w-4" />
                Delete Task
              </>
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
