/**
 * TaskItem component.
 * Displays a single task with title, description, completion status, and actions.
 */
"use client";

import { useState } from "react";
import { Task } from "@/types/task";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { EditTaskDialog } from "@/components/EditTaskDialog";
import { DeleteTaskDialog } from "@/components/DeleteTaskDialog";
import { Pencil, Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface TaskItemProps {
  task: Task;
  onToggleComplete?: (taskId: string) => void;
  onTaskUpdated?: (task: Task) => void;
  onTaskDeleted?: (taskId: string) => void;
}

export function TaskItem({
  task,
  onToggleComplete,
  onTaskUpdated,
  onTaskDeleted,
}: TaskItemProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);

  const handleToggle = () => {
    if (onToggleComplete) {
      onToggleComplete(task.id);
    }
  };

  return (
    <>
      <div
        className={cn(
          "group relative flex items-start gap-4 p-4 rounded-xl border bg-card transition-all duration-200 hover:shadow-md hover:border-primary/20",
          task.is_completed && "opacity-60 bg-muted/30"
        )}
      >
        <Checkbox
          checked={task.is_completed}
          onCheckedChange={handleToggle}
          className="mt-0.5 h-5 w-5"
        />
        <div className="flex-1 min-w-0 space-y-1">
          <h3
            className={cn(
              "font-medium text-foreground leading-tight",
              task.is_completed && "line-through text-muted-foreground"
            )}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={cn(
                "text-sm text-muted-foreground leading-relaxed",
                task.is_completed && "line-through"
              )}
            >
              {task.description}
            </p>
          )}
        </div>
        <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsEditDialogOpen(true)}
            title="Edit task"
            className="h-8 w-8 text-muted-foreground hover:text-foreground"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setIsDeleteDialogOpen(true)}
            title="Delete task"
            className="h-8 w-8 text-muted-foreground hover:text-destructive"
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
