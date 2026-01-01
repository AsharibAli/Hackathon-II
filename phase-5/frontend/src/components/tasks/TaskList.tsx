/**
 * TaskList component.
 * Neo-Editorial styled task list with filtering, sorting, and search.
 */
"use client";

import { useEffect, useState, useCallback } from "react";
import { Task, tasksApi, ApiError, TaskFilters as TFilters } from "@/lib/api";
import { TaskItem } from "./TaskItem";
import { TaskFilters } from "./TaskFilters";
import { SearchBar } from "./SearchBar";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import {
  Inbox,
  RefreshCw,
  Search,
  CheckCircle2,
  AlertCircle,
  ListTodo,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TaskListProps {
  refreshTrigger?: number;
}

export function TaskList({ refreshTrigger }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<TFilters>({});
  const [searchQuery, setSearchQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);

  const fetchTasks = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      let data: Task[];
      if (searchQuery.trim()) {
        setIsSearching(true);
        data = await tasksApi.search(searchQuery);
      } else {
        data = await tasksApi.getAll(filters);
      }
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
      setIsSearching(false);
    }
  }, [filters, searchQuery]);

  useEffect(() => {
    fetchTasks();
  }, [fetchTasks, refreshTrigger]);

  const handleToggleComplete = async (taskId: string) => {
    setTasks((prevTasks) =>
      prevTasks.map((task) =>
        task.id === taskId
          ? { ...task, is_completed: !task.is_completed }
          : task
      )
    );

    try {
      const updatedTask = await tasksApi.toggleComplete(taskId);
      setTasks((prevTasks) =>
        prevTasks.map((task) => (task.id === taskId ? updatedTask : task))
      );
      toast.success(
        updatedTask.is_completed
          ? "Task marked as complete"
          : "Task marked as incomplete"
      );
    } catch (err) {
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

  const handleSearch = useCallback((query: string) => {
    setSearchQuery(query);
  }, []);

  const handleFiltersChange = useCallback(
    (newFilters: TFilters) => {
      setFilters(newFilters);
      if (searchQuery) {
        setSearchQuery("");
      }
    },
    [searchQuery]
  );

  // Calculate stats
  const completedCount = tasks.filter((t) => t.is_completed).length;
  const totalCount = tasks.length;
  const overdueCount = tasks.filter(
    (t) => t.due_date && new Date(t.due_date) < new Date() && !t.is_completed
  ).length;

  // Loading state
  if (isLoading && tasks.length === 0) {
    return (
      <div className="space-y-6">
        <SearchBar onSearch={handleSearch} placeholder="Search tasks..." />
        <TaskFilters filters={filters} onFiltersChange={handleFiltersChange} />
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="h-28 bg-muted/30 animate-pulse rounded-xl border border-border/50"
              style={{ animationDelay: `${i * 100}ms` }}
            />
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="space-y-6">
        <SearchBar onSearch={handleSearch} placeholder="Search tasks..." />
        <TaskFilters filters={filters} onFiltersChange={handleFiltersChange} />
        <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-12 text-center">
          <div className="mx-auto h-14 w-14 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
            <AlertCircle className="h-7 w-7 text-destructive" />
          </div>
          <h3 className="font-display text-lg font-semibold text-foreground mb-2">
            Unable to Load Tasks
          </h3>
          <p className="text-muted-foreground mb-6 max-w-sm mx-auto">{error}</p>
          <Button
            onClick={fetchTasks}
            variant="outline"
            className="gap-2 rounded-xl"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Search */}
      <SearchBar
        onSearch={handleSearch}
        isSearching={isSearching}
        placeholder="Search tasks by title or description..."
      />

      {/* Filters */}
      <TaskFilters filters={filters} onFiltersChange={handleFiltersChange} />

      {/* Stats bar */}
      <div className="flex flex-wrap items-center gap-6 py-3 px-1">
        {searchQuery ? (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Search className="h-4 w-4" />
            <span>
              <span className="font-medium text-foreground">{totalCount}</span>{" "}
              result{totalCount !== 1 ? "s" : ""} for &ldquo;
              <span className="text-primary">{searchQuery}</span>&rdquo;
            </span>
          </div>
        ) : (
          <>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-primary/10 flex items-center justify-center">
                <ListTodo className="h-4 w-4 text-primary" />
              </div>
              <div className="text-sm">
                <span className="font-semibold text-foreground">
                  {totalCount}
                </span>
                <span className="text-muted-foreground ml-1">
                  task{totalCount !== 1 ? "s" : ""}
                </span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
              </div>
              <div className="text-sm">
                <span className="font-semibold text-foreground">
                  {completedCount}
                </span>
                <span className="text-muted-foreground ml-1">completed</span>
              </div>
            </div>

            {overdueCount > 0 && (
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-destructive/10 flex items-center justify-center">
                  <AlertCircle className="h-4 w-4 text-destructive" />
                </div>
                <div className="text-sm">
                  <span className="font-semibold text-destructive">
                    {overdueCount}
                  </span>
                  <span className="text-muted-foreground ml-1">overdue</span>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Empty state */}
      {tasks.length === 0 && (
        <div className="rounded-2xl border border-border/60 bg-card p-16 text-center">
          <div className="mx-auto h-16 w-16 rounded-2xl bg-muted/50 flex items-center justify-center mb-6">
            <Inbox className="h-8 w-8 text-muted-foreground/50" />
          </div>
          {searchQuery ? (
            <>
              <h3 className="font-display text-xl font-semibold mb-2">
                No Matching Tasks
              </h3>
              <p className="text-muted-foreground max-w-sm mx-auto">
                No tasks found for &ldquo;{searchQuery}&rdquo;. Try a different
                search term or clear the search.
              </p>
            </>
          ) : Object.keys(filters).length > 0 ? (
            <>
              <h3 className="font-display text-xl font-semibold mb-2">
                No Tasks Match Filters
              </h3>
              <p className="text-muted-foreground max-w-sm mx-auto">
                Try adjusting your filters or create a new task that matches
                your criteria.
              </p>
            </>
          ) : (
            <>
              <h3 className="font-display text-xl font-semibold mb-2">
                No Tasks Yet
              </h3>
              <p className="text-muted-foreground max-w-sm mx-auto">
                Create your first task using the form on the left, or try the
                chat mode for natural language task creation.
              </p>
            </>
          )}
        </div>
      )}

      {/* Task list */}
      {tasks.length > 0 && (
        <div className="space-y-4">
          {tasks.map((task, index) => (
            <div
              key={task.id}
              className={cn(
                "animate-fade-up",
                isLoading && "opacity-50 pointer-events-none"
              )}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              <TaskItem
                task={task}
                onToggleComplete={handleToggleComplete}
                onTaskUpdated={handleTaskUpdated}
                onTaskDeleted={handleTaskDeleted}
                searchQuery={searchQuery || undefined}
              />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Export a hook-friendly version
export function useTaskList() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchTasks = useCallback(async (filters?: TFilters) => {
    setIsLoading(true);
    try {
      const data = await tasksApi.getAll(filters);
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
