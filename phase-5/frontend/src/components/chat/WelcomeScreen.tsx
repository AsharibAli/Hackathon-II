/**
 * WelcomeScreen component.
 * Neo-Editorial styled welcome screen with starter prompts.
 */
"use client";

import { Sparkles, ListTodo, CalendarCheck, Tag, Search } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WelcomeScreenProps {
  onStarterPrompt: (prompt: string) => void;
}

const starterPrompts = [
  {
    icon: ListTodo,
    title: "Create a task",
    description: "Add a new item to your list",
    prompt: "Create a new task: Review project documentation",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    icon: CalendarCheck,
    title: "Show my tasks",
    description: "View all pending items",
    prompt: "Show me all my pending tasks",
    color: "text-blue-500",
    bgColor: "bg-blue-500/10",
  },
  {
    icon: Tag,
    title: "Filter by tag",
    description: "Find tasks by category",
    prompt: "Show me all tasks tagged with work",
    color: "text-emerald-500",
    bgColor: "bg-emerald-500/10",
  },
  {
    icon: Search,
    title: "Search tasks",
    description: "Find specific items",
    prompt: "Search for tasks containing 'report'",
    color: "text-amber-500",
    bgColor: "bg-amber-500/10",
  },
];

export function WelcomeScreen({ onStarterPrompt }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4 py-12">
      {/* Hero Section */}
      <div className="text-center mb-12 animate-fade-up">
        {/* Logo */}
        <div className="relative inline-flex mb-6">
          <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary/20 via-primary/10 to-accent/10 flex items-center justify-center shadow-soft">
            <Sparkles className="h-10 w-10 text-primary" />
          </div>
          <div className="absolute -top-1 -right-1 h-6 w-6 rounded-full bg-accent/20 flex items-center justify-center animate-pulse-glow">
            <div className="h-3 w-3 rounded-full bg-accent" />
          </div>
        </div>

        {/* Title */}
        <h1 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mb-3">
          How can I help you today?
        </h1>

        {/* Subtitle */}
        <p className="text-muted-foreground max-w-md mx-auto leading-relaxed">
          I can help you manage tasks, set priorities, add reminders, and keep
          your workflow organized. Just tell me what you need.
        </p>
      </div>

      {/* Starter Prompts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full max-w-2xl">
        {starterPrompts.map((item, index) => {
          const Icon = item.icon;
          return (
            <Button
              key={index}
              variant="outline"
              className="h-auto p-5 justify-start text-left flex items-start gap-4 border-border/60 hover:border-primary/30 hover:bg-muted/50 transition-all duration-300 group animate-fade-up rounded-xl"
              style={{ animationDelay: `${100 + index * 75}ms` }}
              onClick={() => onStarterPrompt(item.prompt)}
            >
              <div
                className={`flex-shrink-0 h-10 w-10 rounded-lg ${item.bgColor} flex items-center justify-center group-hover:scale-110 transition-transform duration-200`}
              >
                <Icon className={`h-5 w-5 ${item.color}`} />
              </div>
              <div className="flex-1 min-w-0">
                <span className="block font-medium text-foreground mb-1">
                  {item.title}
                </span>
                <span className="block text-sm text-muted-foreground">
                  {item.description}
                </span>
              </div>
            </Button>
          );
        })}
      </div>

      {/* Tips */}
      <div className="mt-12 text-center animate-fade-up delay-500">
        <p className="text-xs text-muted-foreground/70">
          <span className="font-medium">Tip:</span> Try natural language like
          &quot;Add a high priority task due next Monday&quot; or &quot;Show overdue tasks&quot;
        </p>
      </div>
    </div>
  );
}
