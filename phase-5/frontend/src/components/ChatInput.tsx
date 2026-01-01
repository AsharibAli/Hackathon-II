/**
 * ChatInput component.
 * Neo-Editorial styled chat input with auto-resize.
 */
"use client";

import { useState, FormEvent, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { ArrowUp } from "lucide-react";

interface ChatInputProps {
  onSend: (message: string) => void;
  isLoading?: boolean;
}

export function ChatInput({ onSend, isLoading }: ChatInputProps) {
  const [input, setInput] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        200
      )}px`;
    }
  }, [input]);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSend(input.trim());
      setInput("");
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="relative flex items-end gap-2 bg-muted/40 border border-border/60 rounded-2xl shadow-soft focus-within:border-primary/40 focus-within:shadow-elevated transition-all duration-200">
        {/* Textarea */}
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message..."
          disabled={isLoading}
          rows={1}
          className="flex-1 resize-none bg-transparent py-4 pl-4 pr-2 text-sm placeholder:text-muted-foreground/60 focus:outline-none disabled:cursor-not-allowed disabled:opacity-50 max-h-[200px] scrollbar-thin"
        />

        {/* Send button */}
        <div className="flex items-center pr-3 pb-3">
          <Button
            type="submit"
            size="icon"
            disabled={isLoading || !input.trim()}
            className="h-9 w-9 rounded-xl bg-primary hover:bg-primary/90 disabled:opacity-40 shadow-soft hover:shadow-elevated transition-all duration-200"
          >
            {isLoading ? (
              <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>

      {/* Footer text */}
      <p className="mt-3 text-xs text-center text-muted-foreground/60">
        Press <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-mono text-[10px]">Enter</kbd> to send,{" "}
        <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-mono text-[10px]">Shift+Enter</kbd> for new line
      </p>
    </form>
  );
}
