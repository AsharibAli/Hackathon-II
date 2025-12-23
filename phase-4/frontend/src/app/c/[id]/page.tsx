/**
 * Dynamic conversation page.
 * Shows a specific conversation by its ID with URL-based routing.
 */
"use client";

import { useEffect, useState, use } from "react";
import { useRouter } from "next/navigation";
import { ChatLayout } from "@/components/chat/ChatLayout";
import { authApi, UserProfile } from "@/lib/api";
import { AppHeader, AppMode } from "@/components/navigation";
import { TasksView } from "@/components/tasks";
import { toast } from "sonner";

interface ConversationPageProps {
  params: Promise<{ id: string }>;
}

export default function ConversationPage({ params }: ConversationPageProps) {
  const { id } = use(params);
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeMode, setActiveMode] = useState<AppMode>("chat");
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (!token) {
      router.replace("/login");
      return;
    }
    setIsAuthenticated(true);
    loadUserProfile();
    setIsLoading(false);
  }, [router]);

  const loadUserProfile = async () => {
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch (error) {
      console.error("Failed to load user profile:", error);
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      toast.success("Logged out successfully");
      router.replace("/login");
    } catch (error) {
      localStorage.removeItem("auth_token");
      router.replace("/login");
    }
  };

  const handleModeChange = (mode: AppMode) => {
    setActiveMode(mode);
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

  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </main>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <AppHeader
        activeMode={activeMode}
        onModeChange={handleModeChange}
        user={user}
        onLogout={handleLogout}
        onUpdateProfile={handleUpdateProfile}
      />
      <div className="flex-1 overflow-hidden">
        {activeMode === "chat" ? (
          <ChatLayout initialConversationId={id} />
        ) : (
          <TasksView />
        )}
      </div>
    </div>
  );
}
