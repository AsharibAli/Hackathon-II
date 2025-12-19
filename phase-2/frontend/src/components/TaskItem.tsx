/**
 * TaskItem component.
 * Displays a single task with title, description, completion status, and actions.
 */
"use client";

import { useState } from "react";
import { Task } from "@/types/task";
import { Checkbox } from "@/components/ui/checkbox";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
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
      <Card className={cn(
        "transition-opacity",
        task.is_completed && "opacity-60"
      )}>
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <Checkbox
              checked={task.is_completed}
              onCheckedChange={handleToggle}
              className="mt-1"
            />
            <div className="flex-1 space-y-1">
              <h3
                className={cn(
                  "font-medium",
                  task.is_completed && "line-through text-muted-foreground"
                )}
              >
                {task.title}
              </h3>
              {task.description && (
                <p
                  className={cn(
                    "text-sm text-muted-foreground",
                    task.is_completed && "line-through"
                  )}
                >
                  {task.description}
                </p>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsEditDialogOpen(true)}
                title="Edit task"
              >
                <Pencil className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsDeleteDialogOpen(true)}
                title="Delete task"
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

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
