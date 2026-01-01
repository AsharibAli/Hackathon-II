/**
 * TaskFilters component.
 * Neo-Editorial styled filtering and sorting controls.
 */
"use client";

import { useState } from "react";
import {
  Priority,
  SortField,
  TaskFilters as TFilters,
} from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import {
  Filter,
  SortAsc,
  SortDesc,
  X,
  ChevronUp,
  ChevronDown,
  Minus,
  Tag,
  AlertTriangle,
  CheckCircle2,
  Circle,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface TaskFiltersProps {
  filters: TFilters;
  onFiltersChange: (filters: TFilters) => void;
  className?: string;
}

export function TaskFilters({
  filters,
  onFiltersChange,
  className,
}: TaskFiltersProps) {
  const [tagInput, setTagInput] = useState("");

  const updateFilter = <K extends keyof TFilters>(
    key: K,
    value: TFilters[K] | undefined
  ) => {
    const newFilters = { ...filters };
    if (value === undefined) {
      delete newFilters[key];
    } else {
      newFilters[key] = value;
    }
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    onFiltersChange({});
  };

  const handleTagSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (tagInput.trim()) {
      updateFilter("tag", tagInput.trim().toLowerCase());
      setTagInput("");
    }
  };

  const activeFilterCount = Object.keys(filters).filter(
    (k) => k !== "sort_by" && k !== "sort_order"
  ).length;

  return (
    <div
      className={cn(
        "rounded-xl border border-border/60 bg-card/50 p-4 space-y-4",
        className
      )}
    >
      {/* Filter row */}
      <div className="flex flex-wrap items-center gap-3">
        <span className="text-sm font-medium text-muted-foreground flex items-center gap-2">
          <Filter className="h-4 w-4" />
          Filters
        </span>

        {/* Priority filter */}
        <Select
          value={filters.priority || "all"}
          onValueChange={(v) =>
            updateFilter("priority", v === "all" ? undefined : (v as Priority))
          }
        >
          <SelectTrigger className="w-[140px] h-9 rounded-lg border-border/60 bg-background/80">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent className="rounded-lg">
            <SelectItem value="all">All priorities</SelectItem>
            <SelectItem value="high">
              <span className="flex items-center gap-2 text-red-600 dark:text-red-400">
                <ChevronUp className="h-3.5 w-3.5" /> High
              </span>
            </SelectItem>
            <SelectItem value="medium">
              <span className="flex items-center gap-2 text-amber-600 dark:text-amber-400">
                <Minus className="h-3.5 w-3.5" /> Medium
              </span>
            </SelectItem>
            <SelectItem value="low">
              <span className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                <ChevronDown className="h-3.5 w-3.5" /> Low
              </span>
            </SelectItem>
          </SelectContent>
        </Select>

        {/* Status filter */}
        <Select
          value={
            filters.is_completed === true
              ? "completed"
              : filters.is_completed === false
              ? "pending"
              : "all"
          }
          onValueChange={(v) =>
            updateFilter(
              "is_completed",
              v === "completed" ? true : v === "pending" ? false : undefined
            )
          }
        >
          <SelectTrigger className="w-[130px] h-9 rounded-lg border-border/60 bg-background/80">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent className="rounded-lg">
            <SelectItem value="all">All tasks</SelectItem>
            <SelectItem value="pending">
              <span className="flex items-center gap-2">
                <Circle className="h-3.5 w-3.5" /> Pending
              </span>
            </SelectItem>
            <SelectItem value="completed">
              <span className="flex items-center gap-2">
                <CheckCircle2 className="h-3.5 w-3.5" /> Completed
              </span>
            </SelectItem>
          </SelectContent>
        </Select>

        {/* Overdue toggle */}
        <Button
          variant={filters.overdue ? "default" : "outline"}
          size="sm"
          onClick={() =>
            updateFilter("overdue", filters.overdue ? undefined : true)
          }
          className={cn(
            "h-9 gap-2 rounded-lg transition-all",
            filters.overdue
              ? "bg-destructive hover:bg-destructive/90 text-destructive-foreground"
              : "border-border/60 bg-background/80 hover:bg-muted"
          )}
        >
          <AlertTriangle className="h-3.5 w-3.5" />
          Overdue
        </Button>

        {/* Tag filter input */}
        <form onSubmit={handleTagSubmit} className="flex items-center gap-2">
          <div className="relative">
            <Tag className="absolute left-3 top-1/2 -translate-y-1/2 h-3.5 w-3.5 text-muted-foreground" />
            <Input
              placeholder="Filter by tag..."
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              className="h-9 w-[150px] pl-9 text-sm rounded-lg border-border/60 bg-background/80"
            />
          </div>
        </form>

        {/* Sort controls */}
        <div className="flex items-center gap-2 ml-auto">
          <Select
            value={filters.sort_by || "created_at"}
            onValueChange={(v) => updateFilter("sort_by", v as SortField)}
          >
            <SelectTrigger className="w-[140px] h-9 rounded-lg border-border/60 bg-background/80">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent className="rounded-lg">
              <SelectItem value="created_at">Created date</SelectItem>
              <SelectItem value="updated_at">Updated date</SelectItem>
              <SelectItem value="due_date">Due date</SelectItem>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="title">Title</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="icon"
            className="h-9 w-9 rounded-lg border-border/60 bg-background/80 hover:bg-muted"
            onClick={() =>
              updateFilter(
                "sort_order",
                filters.sort_order === "asc" ? "desc" : "asc"
              )
            }
            title={filters.sort_order === "asc" ? "Ascending" : "Descending"}
          >
            {filters.sort_order === "asc" ? (
              <SortAsc className="h-4 w-4" />
            ) : (
              <SortDesc className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Active filters row */}
      {activeFilterCount > 0 && (
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-border/30">
          <span className="text-xs font-medium text-muted-foreground">
            Active filters:
          </span>

          {filters.priority && (
            <span
              className={cn(
                "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium border",
                filters.priority === "high" &&
                  "bg-red-500/10 text-red-600 dark:text-red-400 border-red-500/20",
                filters.priority === "medium" &&
                  "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
                filters.priority === "low" &&
                  "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20"
              )}
            >
              {filters.priority === "high" && (
                <ChevronUp className="h-3 w-3" />
              )}
              {filters.priority === "medium" && <Minus className="h-3 w-3" />}
              {filters.priority === "low" && (
                <ChevronDown className="h-3 w-3" />
              )}
              {filters.priority.charAt(0).toUpperCase() +
                filters.priority.slice(1)}
              <button
                onClick={() => updateFilter("priority", undefined)}
                className="ml-0.5 hover:bg-black/10 dark:hover:bg-white/10 rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}

          {filters.is_completed !== undefined && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-muted/80 text-foreground border border-border/50">
              {filters.is_completed ? (
                <CheckCircle2 className="h-3 w-3 text-emerald-500" />
              ) : (
                <Circle className="h-3 w-3" />
              )}
              {filters.is_completed ? "Completed" : "Pending"}
              <button
                onClick={() => updateFilter("is_completed", undefined)}
                className="ml-0.5 hover:bg-black/10 dark:hover:bg-white/10 rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}

          {filters.overdue && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-destructive/10 text-destructive border border-destructive/20">
              <AlertTriangle className="h-3 w-3" />
              Overdue only
              <button
                onClick={() => updateFilter("overdue", undefined)}
                className="ml-0.5 hover:bg-destructive/20 rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}

          {filters.tag && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-primary/10 text-primary border border-primary/20">
              <Tag className="h-3 w-3" />#{filters.tag}
              <button
                onClick={() => updateFilter("tag", undefined)}
                className="ml-0.5 hover:bg-primary/20 rounded-full p-0.5 transition-colors"
              >
                <X className="h-3 w-3" />
              </button>
            </span>
          )}

          <Button
            variant="ghost"
            size="sm"
            onClick={clearAllFilters}
            className="h-7 px-2 text-xs text-muted-foreground hover:text-foreground rounded-lg"
          >
            <Sparkles className="h-3 w-3 mr-1" />
            Clear all
          </Button>
        </div>
      )}
    </div>
  );
}
