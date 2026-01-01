/**
 * ChatLayout component.
 * Neo-Editorial styled layout for chat interface with sidebar.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { Sidebar, SidebarToggle } from "./Sidebar";
import { ChatInterface } from "../ChatInterface";
import { conversationsApi, chatApi } from "@/lib/api";
import { ConversationSummary, Message } from "@/types/chat";
import { toast } from "sonner";

interface ChatLayoutProps {
  initialConversationId?: string;
}

// Generate a UUID v4 client-side
function generateUUID(): string {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export function ChatLayout({ initialConversationId }: ChatLayoutProps) {
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(initialConversationId || null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(true);
  const [isInitializing, setIsInitializing] = useState(true);
  const [pendingConversationId, setPendingConversationId] = useState<
    string | null
  >(null);

  // Update URL without triggering navigation
  const updateURL = useCallback((conversationId: string | null) => {
    const newPath = conversationId ? `/c/${conversationId}` : "/";
    if (window.location.pathname !== newPath) {
      window.history.pushState({}, "", newPath);
    }
  }, []);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Update active conversation when initialConversationId changes
  useEffect(() => {
    if (initialConversationId) {
      setActiveConversationId(initialConversationId);
    }
  }, [initialConversationId]);

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConversationId && activeConversationId !== pendingConversationId) {
      loadMessages(activeConversationId);
    } else if (!activeConversationId) {
      setMessages([]);
    }
  }, [activeConversationId, pendingConversationId]);

  // Handle browser back/forward
  useEffect(() => {
    const handlePopState = () => {
      const path = window.location.pathname;
      if (path.startsWith("/c/")) {
        const id = path.split("/c/")[1] || null;
        setActiveConversationId(id);
        setPendingConversationId(null);
      } else {
        setActiveConversationId(null);
        setPendingConversationId(null);
        setMessages([]);
      }
    };

    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

  const loadConversations = async () => {
    try {
      const data = await conversationsApi.list();
      setConversations(data);
    } catch (error) {
      console.error("Failed to load conversations:", error);
    } finally {
      setIsInitializing(false);
    }
  };

  const loadMessages = async (conversationId: string) => {
    try {
      setIsLoading(true);
      const data = await conversationsApi.get(conversationId);
      setMessages(data.messages);
    } catch (error) {
      console.error("Failed to load messages:", error);
      setMessages([]);
      toast.error("Conversation not found");
      setActiveConversationId(null);
      updateURL(null);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    const newId = generateUUID();
    setPendingConversationId(newId);
    setActiveConversationId(newId);
    setMessages([]);
    updateURL(newId);
  };

  const handleSelectConversation = (id: string) => {
    setPendingConversationId(null);
    setActiveConversationId(id);
    updateURL(id);
  };

  const handleRenameConversation = async (id: string, title: string) => {
    try {
      await conversationsApi.rename(id, title);
      setConversations((prev) =>
        prev.map((conv) => (conv.id === id ? { ...conv, title } : conv))
      );
      toast.success("Conversation renamed");
    } catch (error) {
      toast.error("Failed to rename conversation");
    }
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await conversationsApi.delete(id);
      setConversations((prev) => prev.filter((conv) => conv.id !== id));

      if (id === activeConversationId) {
        setActiveConversationId(null);
        setPendingConversationId(null);
        setMessages([]);
        updateURL(null);
      }
      toast.success("Conversation deleted");
    } catch (error) {
      toast.error("Failed to delete conversation");
    }
  };

  const handleSendMessage = async (content: string) => {
    const tempUserMessage: Message = {
      id: "temp-user-" + Date.now(),
      role: "user",
      content: content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);

    try {
      const conversationIdToSend = pendingConversationId
        ? undefined
        : activeConversationId || undefined;

      const response = await chatApi.sendMessage(content, conversationIdToSend);

      const serverConversationId = response.conversation_id;
      setActiveConversationId(serverConversationId);

      if (pendingConversationId) {
        setPendingConversationId(null);
        const newPath = `/c/${serverConversationId}`;
        window.history.replaceState({}, "", newPath);
      }

      setMessages((prev) => {
        const filteredMessages = prev.filter((m) => m.id !== tempUserMessage.id);
        return [...filteredMessages, tempUserMessage, response.message];
      });

      await loadConversations();
    } catch (error) {
      toast.error("Failed to send message");
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  if (isInitializing) {
    return (
      <div className="flex h-full items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-6 animate-fade-in">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-2 border-primary/20" />
            <div className="absolute inset-0 h-12 w-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
          <p className="text-sm text-muted-foreground font-medium tracking-wide">
            Loading conversations...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full bg-background overflow-hidden relative">
      {/* Sidebar Toggle when collapsed */}
      {isSidebarCollapsed && <SidebarToggle onClick={toggleSidebar} />}

      {/* Sidebar */}
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        onNewChat={handleNewChat}
        onSelectConversation={handleSelectConversation}
        onRenameConversation={handleRenameConversation}
        onDeleteConversation={handleDeleteConversation}
        isCollapsed={isSidebarCollapsed}
        onToggleCollapse={toggleSidebar}
      />

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col min-w-0">
        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
          conversationId={activeConversationId}
        />
      </main>
    </div>
  );
}
