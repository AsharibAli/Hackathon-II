/**
 * ChatInterface component.
 * Neo-Editorial styled chat interface with messages and input.
 */
"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { WelcomeScreen } from "./chat/WelcomeScreen";
import { Message } from "../types/chat";
import { ScrollArea } from "./ui/scroll-area";
import { Sparkles } from "lucide-react";

interface ChatInterfaceProps {
  messages: Message[];
  isLoading: boolean;
  onSendMessage: (content: string) => void;
  conversationId: string | null;
}

export function ChatInterface({
  messages,
  isLoading,
  onSendMessage,
}: ChatInterfaceProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const handleStarterPrompt = (prompt: string) => {
    onSendMessage(prompt);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-hidden">
        {messages.length === 0 ? (
          <WelcomeScreen onStarterPrompt={handleStarterPrompt} />
        ) : (
          <ScrollArea className="h-full">
            <div className="max-w-3xl mx-auto px-4 py-8">
              {messages.map((msg, index) => (
                <div
                  key={msg.id}
                  className="animate-fade-up"
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <ChatMessage message={msg} />
                </div>
              ))}

              {/* Loading indicator */}
              {isLoading && (
                <div className="flex items-start gap-4 py-6 animate-fade-up">
                  <div className="flex-shrink-0 h-10 w-10 rounded-xl bg-gradient-to-br from-primary/20 to-accent/20 flex items-center justify-center">
                    <Sparkles className="h-5 w-5 text-primary animate-pulse" />
                  </div>
                  <div className="flex-1 pt-2">
                    <div className="flex items-center gap-2">
                      <div className="flex items-center gap-1.5">
                        <span
                          className="h-2.5 w-2.5 bg-primary/60 rounded-full animate-bounce"
                          style={{ animationDelay: "0ms" }}
                        />
                        <span
                          className="h-2.5 w-2.5 bg-primary/60 rounded-full animate-bounce"
                          style={{ animationDelay: "150ms" }}
                        />
                        <span
                          className="h-2.5 w-2.5 bg-primary/60 rounded-full animate-bounce"
                          style={{ animationDelay: "300ms" }}
                        />
                      </div>
                      <span className="text-sm text-muted-foreground ml-2">
                        Thinking...
                      </span>
                    </div>
                  </div>
                </div>
              )}

              <div ref={scrollRef} />
            </div>
          </ScrollArea>
        )}
      </div>

      {/* Input Area */}
      <div className="border-t border-border/50 bg-background/80 backdrop-blur-md flex-shrink-0">
        <div className="max-w-3xl mx-auto px-4 py-4">
          <ChatInput onSend={onSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
