/**
 * ChatMessage component.
 * Neo-Editorial styled chat message bubble.
 */
"use client";

import { useState } from "react";
import { Message } from "../types/chat";
import { cn } from "../lib/utils";
import { Sparkles, User, Copy, Check } from "lucide-react";
import { Button } from "./ui/button";

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error("Failed to copy:", error);
    }
  };

  return (
    <div
      className={cn(
        "group relative flex gap-4 py-5",
        isUser ? "flex-row-reverse" : "flex-row"
      )}
    >
      {/* Avatar */}
      <div
        className={cn(
          "flex-shrink-0 h-10 w-10 rounded-xl flex items-center justify-center transition-transform group-hover:scale-105",
          isUser
            ? "bg-primary text-primary-foreground shadow-soft"
            : "bg-gradient-to-br from-primary/20 via-primary/10 to-accent/20"
        )}
      >
        {isUser ? (
          <User className="h-5 w-5" />
        ) : (
          <Sparkles className="h-5 w-5 text-primary" />
        )}
      </div>

      {/* Message Content */}
      <div
        className={cn(
          "flex-1 min-w-0 max-w-[85%] md:max-w-[75%]",
          isUser ? "text-right" : "text-left"
        )}
      >
        {/* Role Label */}
        <div className="mb-2">
          <span className="text-xs font-medium text-muted-foreground tracking-wide uppercase">
            {isUser ? "You" : "AI Assistant"}
          </span>
        </div>

        {/* Message Bubble */}
        <div
          className={cn(
            "inline-block rounded-2xl px-5 py-3.5 text-sm leading-relaxed shadow-sm",
            isUser
              ? "bg-primary text-primary-foreground rounded-tr-md"
              : "bg-muted/60 text-foreground rounded-tl-md border border-border/30"
          )}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>

        {/* Actions (only for assistant messages) */}
        {!isUser && (
          <div className="mt-3 flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            <Button
              variant="ghost"
              size="sm"
              className="h-8 px-3 text-xs text-muted-foreground hover:text-foreground rounded-lg"
              onClick={handleCopy}
            >
              {copied ? (
                <>
                  <Check className="h-3.5 w-3.5 mr-1.5 text-success" />
                  <span className="text-success">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3.5 w-3.5 mr-1.5" />
                  Copy
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
