/**
 * TaskForm component.
 * Neo-Editorial styled task creation form with Phase 5 enhancements.
 */
"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { tasksApi, ApiError, Task, Priority, Recurrence } from "@/lib/api";
import { TagChip } from "./TagChip";
import { toast } from "sonner";
import {
  Plus,
  Sparkles,
  ChevronUp,
  ChevronDown,
  Minus,
  Calendar,
  Bell,
  Repeat,
  Tag,
  AlertCircle,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";

interface TaskFormProps {
  onTaskCreated?: (task: Task) => void;
}

export function TaskForm({ onTaskCreated }: TaskFormProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("medium");
  const [dueDate, setDueDate] = useState("");
  const [reminderTime, setReminderTime] = useState("");
  const [recurrence, setRecurrence] = useState<Recurrence>("none");
  const [tags, setTags] = useState<string[]>([]);
  const [newTag, setNewTag] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    reminder?: string;
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

    // Validate reminder is in the future
    if (reminderTime) {
      const reminderDate = new Date(reminderTime);
      if (reminderDate <= new Date()) {
        newErrors.reminder = "Reminder must be set in the future";
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleAddTag = () => {
    const tag = newTag.trim().toLowerCase();
    if (tag && !tags.includes(tag) && tags.length < 10) {
      setTags([...tags, tag]);
      setNewTag("");
    }
  };

  const handleRemoveTag = (tagToRemove: string) => {
    setTags(tags.filter((t) => t !== tagToRemove));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      // Create the task with basic fields
      let task = await tasksApi.create({
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined,
        tags: tags.length > 0 ? tags : undefined,
      });

      // Set reminder if specified
      if (reminderTime) {
        task = await tasksApi.setReminder(task.id, reminderTime);
      }

      // Update with recurrence if not "none"
      if (recurrence !== "none") {
        task = await tasksApi.update(task.id, { recurrence });
      }

      toast.success("Task created successfully!");

      // Reset form
      setTitle("");
      setDescription("");
      setPriority("medium");
      setDueDate("");
      setReminderTime("");
      setRecurrence("none");
      setTags([]);
      setNewTag("");
      setShowAdvanced(false);

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
            <h2 className="font-display text-lg font-semibold">Create Task</h2>
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
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {errors.title}
              </p>
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
              rows={3}
              className="flex w-full rounded-lg border border-input bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary transition-all disabled:cursor-not-allowed disabled:opacity-50 resize-none"
            />
            {errors.description && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {errors.description}
              </p>
            )}
          </div>

          {/* Priority */}
          <div className="space-y-2">
            <Label className="text-sm font-medium">Priority</Label>
            <Select
              value={priority}
              onValueChange={(v) => setPriority(v as Priority)}
              disabled={isLoading}
            >
              <SelectTrigger className="h-11 rounded-lg">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="rounded-lg">
                <SelectItem value="high">
                  <span className="flex items-center gap-2 text-red-600 dark:text-red-400">
                    <ChevronUp className="h-4 w-4" /> High Priority
                  </span>
                </SelectItem>
                <SelectItem value="medium">
                  <span className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                    <Minus className="h-4 w-4" /> Medium Priority
                  </span>
                </SelectItem>
                <SelectItem value="low">
                  <span className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                    <ChevronDown className="h-4 w-4" /> Low Priority
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Due Date */}
          <div className="space-y-2">
            <Label
              htmlFor="due-date"
              className="text-sm font-medium flex items-center gap-1.5"
            >
              <Calendar className="h-3.5 w-3.5 text-muted-foreground" />
              Due Date
            </Label>
            <Input
              id="due-date"
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              disabled={isLoading}
              className="h-11 rounded-lg"
              min={new Date().toISOString().split("T")[0]}
            />
          </div>

          {/* Tags */}
          <div className="space-y-3">
            <Label className="text-sm font-medium flex items-center gap-1.5">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" />
              Tags
            </Label>
            <div className="flex gap-2">
              <Input
                placeholder="Add a tag..."
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddTag();
                  }
                }}
                disabled={isLoading || tags.length >= 10}
                className="flex-1 h-10 rounded-lg"
                maxLength={30}
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleAddTag}
                disabled={isLoading || !newTag.trim() || tags.length >= 10}
                className="h-10 w-10 rounded-lg"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
            {tags.length > 0 && (
              <div className="flex flex-wrap gap-2 p-3 rounded-lg bg-muted/30 border border-border/50">
                {tags.map((tag) => (
                  <TagChip
                    key={tag}
                    name={tag}
                    size="md"
                    onRemove={() => handleRemoveTag(tag)}
                  />
                ))}
              </div>
            )}
            <p className="text-xs text-muted-foreground">
              {tags.length}/10 tags
            </p>
          </div>

          {/* Advanced Options Toggle */}
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors w-full"
          >
            {showAdvanced ? (
              <ChevronLeft className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            <span>{showAdvanced ? "Hide" : "Show"} advanced options</span>
          </button>

          {/* Advanced Options */}
          {showAdvanced && (
            <div className="space-y-5 pt-2 border-t border-border/30">
              {/* Reminder */}
              <div className="space-y-2">
                <Label
                  htmlFor="reminder"
                  className="text-sm font-medium flex items-center gap-1.5"
                >
                  <Bell className="h-3.5 w-3.5 text-muted-foreground" />
                  Reminder
                </Label>
                <Input
                  id="reminder"
                  type="datetime-local"
                  value={reminderTime}
                  onChange={(e) => setReminderTime(e.target.value)}
                  disabled={isLoading}
                  className="h-11 rounded-lg"
                  min={new Date().toISOString().slice(0, 16)}
                />
                {errors.reminder && (
                  <p className="text-sm text-destructive flex items-center gap-1">
                    <AlertCircle className="h-3 w-3" />
                    {errors.reminder}
                  </p>
                )}
                <p className="text-xs text-muted-foreground">
                  Get notified at this time
                </p>
              </div>

              {/* Recurrence */}
              <div className="space-y-2">
                <Label className="text-sm font-medium flex items-center gap-1.5">
                  <Repeat className="h-3.5 w-3.5 text-muted-foreground" />
                  Repeat
                </Label>
                <Select
                  value={recurrence}
                  onValueChange={(v) => setRecurrence(v as Recurrence)}
                  disabled={isLoading}
                >
                  <SelectTrigger className="h-11 rounded-lg">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="rounded-lg">
                    <SelectItem value="none">Does not repeat</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="monthly">Monthly</SelectItem>
                  </SelectContent>
                </Select>
                <p className="text-xs text-muted-foreground">
                  Create a new task when completed
                </p>
              </div>
            </div>
          )}

          {/* Error message */}
          {errors.general && (
            <div className="flex items-start gap-3 p-4 text-sm text-destructive bg-destructive/10 rounded-lg border border-destructive/20">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
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
