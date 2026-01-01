/**
 * TaskForm component.
 * Neo-Editorial styled task creation form.
 */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { tasksApi, ApiError, Task } from "@/lib/api";
import { toast } from "sonner";
import { Plus, Sparkles } from "lucide-react";

interface TaskFormProps {
  onTaskCreated?: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    general?: string;
  }>({});

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!title.trim()) {
      newErrors.title = "Title is required";
    } else if (title.length > 200) {
      newErrors.title = "Title must be 200 characters or less";
    }

    if (description.length > 2000) {
      newErrors.description = "Description must be 2000 characters or less";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      const task = await tasksApi.create({
        title: title.trim(),
        description: description.trim() || undefined,
      });

      toast.success("Task created successfully!");

      setTitle("");
      setDescription("");

      if (onTaskCreated) {
        onTaskCreated(task);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || "Failed to create task";
        setErrors({ general: detail });
        toast.error(detail);
      } else {
        setErrors({ general: "An unexpected error occurred" });
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="rounded-2xl border border-border/60 bg-card shadow-card overflow-hidden">
      {/* Header */}
      <div className="px-6 py-5 border-b border-border/50 bg-muted/30">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
            <Plus className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h2 className="font-display text-lg font-semibold">
              Create Task
            </h2>
            <p className="text-xs text-muted-foreground">
              Add a new item to your list
            </p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="p-6">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="title" className="text-sm font-medium">
              Title <span className="text-destructive">*</span>
            </Label>
            <Input
              id="title"
              placeholder="What needs to be done?"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isLoading}
              aria-invalid={!!errors.title}
              maxLength={200}
              className="h-11"
            />
            {errors.title && (
              <p className="text-sm text-destructive">{errors.title}</p>
            )}
            <p className="text-xs text-muted-foreground">
              {title.length}/200 characters
            </p>
          </div>

          {/* Description */}
          <div className="space-y-2">
            <Label htmlFor="description" className="text-sm font-medium">
              Description
            </Label>
            <textarea
              id="description"
              placeholder="Add details... (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
              aria-invalid={!!errors.description}
              maxLength={2000}
              rows={4}
              className="flex w-full rounded-lg border border-input bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary transition-all disabled:cursor-not-allowed disabled:opacity-50 resize-none"
            />
            {errors.description && (
              <p className="text-sm text-destructive">{errors.description}</p>
            )}
          </div>

          {/* Error message */}
          {errors.general && (
            <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-lg border border-destructive/20">
              {errors.general}
            </div>
          )}

          {/* Submit button */}
          <Button
            type="submit"
            className="w-full h-11 gap-2 shadow-soft hover:shadow-elevated transition-shadow"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                Creating...
              </>
            ) : (
              <>
                <Sparkles className="h-4 w-4" />
                Create Task
              </>
            )}
          </Button>
        </form>
      </div>

      {/* Tip */}
      <div className="px-6 py-4 bg-muted/20 border-t border-border/30">
        <p className="text-xs text-muted-foreground text-center">
          <span className="font-medium">Tip:</span> Use the chat mode for
          natural language task creation
        </p>
      </div>
    </div>
  );
}
