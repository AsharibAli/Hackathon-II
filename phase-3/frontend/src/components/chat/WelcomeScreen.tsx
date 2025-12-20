"use client";

import { Bot, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";

interface WelcomeScreenProps {
  onStarterPrompt: (prompt: string) => void;
}

const starterPrompts = [
  {
    title: "Create a task",
    description: "Add a new task to my todo list",
    prompt: "Create a new task for me: Review project documentation",
  },
  {
    title: "List my tasks",
    description: "Show all my pending tasks",
    prompt: "Show me all my pending tasks",
  },
  {
    title: "Help me organize",
    description: "Get productivity tips",
    prompt: "Give me some tips to organize my day better",
  },
  {
    title: "Complete a task",
    description: "Mark a task as done",
    prompt: "What tasks do I have? I'd like to mark one as complete.",
  },
];

export function WelcomeScreen({ onStarterPrompt }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col items-center justify-center h-full px-4">
      {/* Logo/Icon */}
      <div className="mb-8">
        <div className="relative">
          <div className="h-20 w-20 rounded-full bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center">
            <Bot className="h-10 w-10 text-primary" />
          </div>
          <div className="absolute -top-1 -right-1">
            <Sparkles className="h-6 w-6 text-primary/60" />
          </div>
        </div>
      </div>

      {/* Welcome Text */}
      <h1 className="text-2xl font-semibold mb-2 text-foreground">
        AI Todo Assistant
      </h1>
      <p className="text-muted-foreground text-center mb-8 max-w-md">
        I can help you manage your tasks, organize your day, and boost your productivity.
        What would you like to do?
      </p>

      {/* Starter Prompts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-2xl">
        {starterPrompts.map((item, index) => (
          <Button
            key={index}
            variant="outline"
            className="h-auto p-4 justify-start text-left flex flex-col items-start gap-1 hover:bg-accent/50 hover:border-primary/30 transition-all"
            onClick={() => onStarterPrompt(item.prompt)}
          >
            <span className="font-medium text-foreground">{item.title}</span>
            <span className="text-xs text-muted-foreground">{item.description}</span>
          </Button>
        ))}
      </div>
    </div>
  );
}
