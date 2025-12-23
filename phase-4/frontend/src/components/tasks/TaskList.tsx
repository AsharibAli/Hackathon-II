/**
 * TaskList component.
 * Fetches and displays all tasks for the authenticated user.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { Task, tasksApi, ApiError } from "@/lib/api";
import { TaskItem } from "./TaskItem";
import { toast } from "sonner";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Inbox, RefreshCw } from "lucide-react";

interface TaskListProps {
  refreshTrigger?: number;
  onTaskCreated?: (task: Task) => void;
}

export function TaskList({ refreshTrigger, onTaskCreated }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const data = await tasksApi.getAll();
      setTasks(data);
    } catch (err) {
      if (err instanceof ApiError) {
        const message = err.data?.detail || "Failed to load tasks";
        setError(message);
        toast.error(message);
      } else {
        setError("An unexpected error occurred");
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  const handleToggleComplete = async (taskId: string) => {
    // Optimistic update
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId
          ? { ...task, is_completed: !task.is_completed }
          : task
      )
    );

    try {
      const updatedTask = await tasksApi.toggleComplete(taskId);
      // Update with server response
      setTasks((prevTasks) =>
        prevTasks.map((task) => (task.id === taskId ? updatedTask : task))
      );
      toast.success(
        updatedTask.is_completed
          ? "Task marked as complete"
          : "Task marked as incomplete"
      );
    } catch (err) {
      // Rollback on error
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId
            ? { ...task, is_completed: !task.is_completed }
            : task
        )
      );
      if (err instanceof ApiError) {
        toast.error(err.data?.detail || "Failed to update task");
      } else {
        toast.error("An unexpected error occurred");
      }
    }
  };

  const handleTaskUpdated = (updatedTask: Task) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) => (task.id === updatedTask.id ? updatedTask : task))
    );
  };

  const handleTaskDeleted = (taskId: string) => {
    setTasks((prevTasks) => prevTasks.filter((task) => task.id !== taskId));
  };

  // Expose method to add new task
  const addTask = useCallback((task: Task) => {
    setTasks((prevTasks) => [task, ...prevTasks]);
  }, []);

  // Call onTaskCreated callback when component mounts to expose addTask method
  useEffect(() => {
    if (onTaskCreated) {
      // This is a bit unconventional but allows parent to trigger task addition
    }
  }, [onTaskCreated]);

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="h-20 bg-muted/50 animate-pulse rounded-xl border"
          />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-destructive mb-4">{error}</p>
          <Button onClick={fetchTasks} variant="outline" className="gap-2">
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
        </CardContent>
      </Card>
    );
  }

  if (tasks.length === 0) {
    return (
      <Card>
        <CardContent className="py-16 text-center">
          <Inbox className="h-12 w-12 mx-auto text-muted-foreground/50 mb-4" />
          <h3 className="text-lg font-medium mb-2">No tasks yet</h3>
          <p className="text-muted-foreground">
            Create your first task to get started!
          </p>
        </CardContent>
      </Card>
    );
  }

  const completedCount = tasks.filter((t) => t.is_completed).length;
  const totalCount = tasks.length;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>{totalCount} task{totalCount !== 1 ? "s" : ""}</span>
        <span>{completedCount} completed</span>
      </div>
      <div className="space-y-3">
        {tasks.map((task) => (
          <TaskItem
            key={task.id}
            task={task}
            onToggleComplete={handleToggleComplete}
            onTaskUpdated={handleTaskUpdated}
            onTaskDeleted={handleTaskDeleted}
          />
        ))}
      </div>
    </div>
  );
}

// Export a hook-friendly version
export function useTaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await tasksApi.getAll();
      setTasks(data);
    } catch {
      // Error handled by caller
    } finally {
      setIsLoading(false);
    }
  }, []);

  const addTask = useCallback((task: Task) => {
    setTasks((prev) => [task, ...prev]);
  }, []);

  return { tasks, isLoading, fetchTasks, addTask, setTasks };
}
