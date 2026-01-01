/**
 * EditTaskDialog component.
 * Neo-Editorial styled modal dialog for editing tasks.
 */
"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Task, tasksApi, ApiError, Priority, Recurrence } from "@/lib/api";
import { TagChip } from "./TagChip";
import { toast } from "sonner";
import {
  Plus,
  ChevronUp,
  ChevronDown,
  Minus,
  Calendar,
  Bell,
  Repeat,
  Pencil,
  Tag,
  AlertCircle,
  Save,
} from "lucide-react";

interface EditTaskDialogProps {
  task: Task;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onTaskUpdated: (task: Task) => void;
}

export function EditTaskDialog({
  task,
  open,
  onOpenChange,
  onTaskUpdated,
}: EditTaskDialogProps) {
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || "");
  const [priority, setPriority] = useState<Priority>(task.priority || "medium");
  const [dueDate, setDueDate] = useState(task.due_date?.split("T")[0] || "");
  const [reminderTime, setReminderTime] = useState(
    task.remind_at?.slice(0, 16) || ""
  );
  const [recurrence, setRecurrence] = useState<Recurrence>(
    task.recurrence || "none"
  );
  const [tags, setTags] = useState<string[]>(task.tags || []);
  const [newTag, setNewTag] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [errors, setErrors] = useState<{
    title?: string;
    description?: string;
    reminder?: string;
    general?: string;
  }>({});

  // Reset form when task changes or dialog opens
  useEffect(() => {
    if (open) {
      setTitle(task.title);
      setDescription(task.description || "");
      setPriority(task.priority || "medium");
      setDueDate(task.due_date?.split("T")[0] || "");
      setReminderTime(task.remind_at?.slice(0, 16) || "");
      setRecurrence(task.recurrence || "none");
      setTags(task.tags || []);
      setNewTag("");
      setErrors({});
    }
  }, [task, open]);

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

  const handleAddTag = () => {
    const tag = newTag.trim().toLowerCase();
    if (tag && !tags.includes(tag)) {
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
      let updatedTask = await tasksApi.update(task.id, {
        title: title.trim(),
        description: description.trim() || undefined,
        priority,
        due_date: dueDate || undefined,
        remind_at: reminderTime || undefined,
        recurrence,
      });

      // Handle tag changes
      const originalTags = new Set(task.tags || []);
      const newTags = new Set(tags);

      // Remove tags that were removed
      for (const tag of originalTags) {
        if (!newTags.has(tag)) {
          updatedTask = await tasksApi.removeTag(task.id, tag);
        }
      }

      // Add tags that were added
      for (const tag of newTags) {
        if (!originalTags.has(tag)) {
          updatedTask = await tasksApi.addTag(task.id, tag);
        }
      }

      toast.success("Task updated successfully!");
      onTaskUpdated(updatedTask);
      onOpenChange(false);
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || "Failed to update task";
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

  const handleCancel = () => {
    setTitle(task.title);
    setDescription(task.description || "");
    setPriority(task.priority || "medium");
    setDueDate(task.due_date?.split("T")[0] || "");
    setReminderTime(task.remind_at?.slice(0, 16) || "");
    setRecurrence(task.recurrence || "none");
    setTags(task.tags || []);
    setErrors({});
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg max-h-[90vh] overflow-y-auto rounded-2xl border-border/60 p-0">
        {/* Header */}
        <DialogHeader className="px-6 pt-6 pb-4 border-b border-border/50 bg-muted/30">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center">
              <Pencil className="h-5 w-5 text-primary" />
            </div>
            <div>
              <DialogTitle className="font-display text-lg font-semibold">
                Edit Task
              </DialogTitle>
              <DialogDescription className="text-sm">
                Update details, priority, and schedule
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="p-6 space-y-5">
          {/* Title */}
          <div className="space-y-2">
            <Label htmlFor="edit-title" className="text-sm font-medium">
              Title <span className="text-destructive">*</span>
            </Label>
            <Input
              id="edit-title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={isLoading}
              aria-invalid={!!errors.title}
              maxLength={200}
              className="h-11 rounded-lg"
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
            <Label htmlFor="edit-description" className="text-sm font-medium">
              Description
            </Label>
            <textarea
              id="edit-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
              aria-invalid={!!errors.description}
              maxLength={2000}
              rows={3}
              placeholder="Add details about this task..."
              className="flex w-full rounded-lg border border-input bg-background px-4 py-3 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary transition-all disabled:cursor-not-allowed disabled:opacity-50 resize-none"
            />
            {errors.description && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {errors.description}
              </p>
            )}
          </div>

          {/* Priority and Due Date row */}
          <div className="grid grid-cols-2 gap-4">
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
                      <ChevronUp className="h-4 w-4" /> High
                    </span>
                  </SelectItem>
                  <SelectItem value="medium">
                    <span className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                      <Minus className="h-4 w-4" /> Medium
                    </span>
                  </SelectItem>
                  <SelectItem value="low">
                    <span className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                      <ChevronDown className="h-4 w-4" /> Low
                    </span>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Due Date */}
            <div className="space-y-2">
              <Label
                htmlFor="edit-due-date"
                className="text-sm font-medium flex items-center gap-1.5"
              >
                <Calendar className="h-3.5 w-3.5 text-muted-foreground" /> Due
                Date
              </Label>
              <Input
                id="edit-due-date"
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
                disabled={isLoading}
                className="h-11 rounded-lg"
              />
            </div>
          </div>

          {/* Reminder */}
          <div className="space-y-2">
            <Label
              htmlFor="edit-reminder"
              className="text-sm font-medium flex items-center gap-1.5"
            >
              <Bell className="h-3.5 w-3.5 text-muted-foreground" /> Reminder
            </Label>
            <Input
              id="edit-reminder"
              type="datetime-local"
              value={reminderTime}
              onChange={(e) => setReminderTime(e.target.value)}
              disabled={isLoading}
              className="h-11 rounded-lg"
            />
            {errors.reminder && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {errors.reminder}
              </p>
            )}
            <p className="text-xs text-muted-foreground">
              Set a date and time to be reminded
            </p>
          </div>

          {/* Recurrence */}
          <div className="space-y-2">
            <Label className="text-sm font-medium flex items-center gap-1.5">
              <Repeat className="h-3.5 w-3.5 text-muted-foreground" />{" "}
              Recurrence
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
          </div>

          {/* Tags */}
          <div className="space-y-3">
            <Label className="text-sm font-medium flex items-center gap-1.5">
              <Tag className="h-3.5 w-3.5 text-muted-foreground" /> Tags
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
                disabled={isLoading}
                className="flex-1 h-10 rounded-lg"
              />
              <Button
                type="button"
                variant="outline"
                size="icon"
                onClick={handleAddTag}
                disabled={isLoading || !newTag.trim()}
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
          </div>

          {/* Error message */}
          {errors.general && (
            <div className="flex items-start gap-3 p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
              <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
              {errors.general}
            </div>
          )}

          {/* Footer */}
          <DialogFooter className="pt-4 border-t border-border/50 gap-2">
            <Button
              type="button"
              variant="outline"
              onClick={handleCancel}
              disabled={isLoading}
              className="rounded-lg"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="rounded-lg gap-2"
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
