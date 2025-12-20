"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Sidebar, SidebarToggle } from "./Sidebar";
import { ChatInterface } from "../ChatInterface";
import { conversationsApi, chatApi, authApi, UserProfile } from "@/lib/api";
import { ConversationSummary, Message } from "@/types/chat";
import { toast } from "sonner";

export function ChatLayout() {
  const router = useRouter();
  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [user, setUser] = useState<UserProfile | null>(null);

  // Load user profile and conversations on mount
  useEffect(() => {
    loadUserProfile();
    loadConversations();
  }, []);

  // Load messages when active conversation changes
  useEffect(() => {
    if (activeConversationId) {
      loadMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId]);

  const loadUserProfile = async () => {
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch (error) {
      console.error("Failed to load user profile:", error);
    }
  };

  const loadConversations = async () => {
    try {
      const data = await conversationsApi.list();
      setConversations(data);
      // Do NOT auto-select conversation - show welcome screen by default
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
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleSelectConversation = (id: string) => {
    setActiveConversationId(id);
  };

  const handleRenameConversation = async (id: string, title: string) => {
    try {
      await conversationsApi.rename(id, title);
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === id ? { ...conv, title } : conv
        )
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
      
      // If we deleted the active conversation, clear it
      if (id === activeConversationId) {
        setActiveConversationId(null);
        setMessages([]);
      }
      toast.success("Conversation deleted");
    } catch (error) {
      toast.error("Failed to delete conversation");
    }
  };

  const handleSendMessage = async (content: string) => {
    // Optimistic update - add user message
    const tempUserMessage: Message = {
      id: "temp-user-" + Date.now(),
      role: "user",
      content: content,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMessage]);
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage(content, activeConversationId || undefined);
      
      // If this was a new conversation, update the active ID
      if (!activeConversationId) {
        setActiveConversationId(response.conversation_id);
      }
      
      // Replace temp user message with the one from response (which has real ID)
      // and add assistant's response
      setMessages((prev) => {
        // Remove temp message and add the assistant response
        const filteredMessages = prev.filter((m) => m.id !== tempUserMessage.id);
        return [...filteredMessages, tempUserMessage, response.message];
      });
      
      // Refresh conversation list to show new/updated conversation
      await loadConversations();
      
    } catch (error) {
      toast.error("Failed to send message");
      // Remove the optimistic message on error
      setMessages((prev) => prev.filter((m) => m.id !== tempUserMessage.id));
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      toast.success("Logged out successfully");
      router.push("/");
      router.refresh();
    } catch (error) {
      // Logout locally even if API fails
      authApi.logout();
      router.push("/");
      router.refresh();
    }
  };

  const handleUpdateProfile = async (data: { full_name?: string; profile_picture?: string }) => {
    try {
      const updatedProfile = await authApi.updateProfile(data);
      setUser(updatedProfile);
      toast.success("Profile updated");
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  if (isInitializing) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background overflow-hidden">
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
        user={user}
        onLogout={handleLogout}
        onUpdateProfile={handleUpdateProfile}
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
