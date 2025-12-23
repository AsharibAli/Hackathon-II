/**
 * TasksView component.
 * Container for the GUI mode - displays TaskForm and TaskList.
 */
"use client";

import { useState, useCallback } from "react";
import { TaskForm } from "./TaskForm";
import { TaskList } from "./TaskList";
import { Task } from "@/lib/api";

export function TasksView() {
  // Use a refresh trigger to force TaskList to refetch after task creation
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTaskCreated = useCallback((task: Task) => {
    // Increment refresh trigger to cause TaskList to refetch
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  return (
    <div className="flex-1 flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="container mx-auto max-w-4xl px-4 py-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Task Form - Sidebar on larger screens */}
            <div className="lg:col-span-1 order-2 lg:order-1">
              <TaskForm onTaskCreated={handleTaskCreated} />
            </div>

            {/* Task List - Main content */}
            <div className="lg:col-span-2 order-1 lg:order-2">
              <TaskList refreshTrigger={refreshTrigger} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
