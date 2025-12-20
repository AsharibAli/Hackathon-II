"use client";

import { useEffect, useState, useRef } from "react";
import { ChatMessage } from "./ChatMessage";
import { ChatInput } from "./ChatInput";
import { chatApi } from "../lib/api";
import { Message } from "../types/chat";
import { ScrollArea } from "./ui/scroll-area";
import { toast } from "sonner";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadConversation();
  }, []);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const loadConversation = async () => {
    try {
      setIsLoading(true);
      const data = await chatApi.getConversation();
      setMessages(data.messages);
    } catch (error) {
      console.error("Failed to load conversation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (content: string) => {
    // Optimistic update
    const tempMessage: Message = {
      id: "temp-" + Date.now(),
      role: "user",
      content: content,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(content);
      // Append the assistant's response
      setMessages(prev => [...prev, response.message]);
    } catch (error) {
      toast.error("Failed to send message");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] border rounded-lg overflow-hidden bg-background mt-4">
      <ScrollArea className="flex-1 p-4">
        <div className="flex flex-col gap-4">
          {messages.map((msg) => (
            <ChatMessage key={msg.id} message={msg} />
          ))}
          <div ref={scrollRef} />
        </div>
      </ScrollArea>
      <ChatInput onSend={handleSend} isLoading={isLoading} />
    </div>
  );
}
