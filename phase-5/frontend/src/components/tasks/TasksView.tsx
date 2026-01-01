/**
 * TasksView component.
 * Neo-Editorial styled container for GUI mode with TaskForm and TaskList.
 */
"use client";

import { useState, useCallback } from "react";
import { TaskForm } from "./TaskForm";
import { TaskList } from "./TaskList";
import { Task } from "@/lib/api";

export function TasksView() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTaskCreated = useCallback((_task: Task) => {
    setRefreshTrigger((prev) => prev + 1);
  }, []);

  return (
    <div className="h-full flex flex-col overflow-hidden bg-background">
      {/* Main content - scrollable */}
      <div className="flex-1 overflow-y-auto">
        <div className="container-wide py-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
            {/* Task Form - Sidebar on larger screens */}
            <div className="lg:col-span-4 xl:col-span-3 order-2 lg:order-1">
              <div className="lg:sticky lg:top-6">
                <TaskForm onTaskCreated={handleTaskCreated} />
              </div>
            </div>

            {/* Task List - Main content */}
            <div className="lg:col-span-8 xl:col-span-9 order-1 lg:order-2 min-h-0">
              <TaskList refreshTrigger={refreshTrigger} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
