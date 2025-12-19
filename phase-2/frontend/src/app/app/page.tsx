/**
 * Main todo list page.
 * Displays the user's tasks in a protected route with task creation.
 */
"use client";

import { useState } from "react";
import { TaskList } from "@/components/TaskList";
import { TaskForm } from "@/components/TaskForm";

export default function AppPage() {
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleTaskCreated = () => {
    // Trigger TaskList refresh
    setRefreshTrigger((prev) => prev + 1);
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold mb-2">My Tasks</h2>
        <p className="text-muted-foreground">
          Manage your personal todo list
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        <div className="md:col-span-2 order-2 md:order-1">
          <TaskList key={refreshTrigger} />
        </div>
        <div className="md:col-span-1 order-1 md:order-2">
          <TaskForm onTaskCreated={handleTaskCreated} />
        </div>
      </div>
    </div>
  );
}
