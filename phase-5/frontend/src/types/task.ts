/**
 * Task type definitions.
 * Matches the backend API TaskRead schema.
 */

export type Priority = "low" | "medium" | "high";
export type Recurrence = "none" | "daily" | "weekly" | "monthly";
export type SortField = "created_at" | "updated_at" | "due_date" | "priority" | "title";
export type SortOrder = "asc" | "desc";

export interface Task {
  id: string;
  user_id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
  // Phase 5 additions
  priority: Priority;
  due_date?: string;
  remind_at?: string;
  reminder_sent: boolean;
  recurrence: Recurrence;
  tags: string[];
  parent_task_id?: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: Priority;
  due_date?: string;
  remind_at?: string;
  recurrence?: Recurrence;
  tags?: string[];
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  is_completed?: boolean;
  priority?: Priority;
  due_date?: string;
  remind_at?: string;
  recurrence?: Recurrence;
}

export interface TaskFilters {
  priority?: Priority;
  tag?: string;
  is_completed?: boolean;
  overdue?: boolean;
  sort_by?: SortField;
  sort_order?: SortOrder;
}
