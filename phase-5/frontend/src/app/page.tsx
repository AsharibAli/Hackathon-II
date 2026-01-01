/**
 * Main App page - Entry point for authenticated users.
 * Redirects unauthenticated users to /home landing page.
 *
 * Dual Mode:
 * - Chat (CUI): Natural language AI task management
 * - Tasks (GUI): Traditional visual interface
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { ChatLayout } from "@/components/chat/ChatLayout";
import { TasksView } from "@/components/tasks";
import { AppHeader, AppMode } from "@/components/navigation";
import { authApi, UserProfile } from "@/lib/api";
import { toast } from "sonner";

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeMode, setActiveMode] = useState<AppMode>("chat");
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      setIsAuthenticated(true);
      loadUserProfile();
    } else {
      // Redirect unauthenticated users to landing page
      router.replace("/home");
    }
    setIsLoading(false);
  }, [router]);

  const loadUserProfile = async () => {
    try {
      const profile = await authApi.getProfile();
      setUser(profile);
    } catch (error) {
      console.error("Failed to load user profile:", error);
      // Token might be invalid, redirect to home
      localStorage.removeItem("auth_token");
      router.replace("/home");
    }
  };

  const handleLogout = async () => {
    try {
      await authApi.logout();
      toast.success("Logged out successfully");
      setIsAuthenticated(false);
      setUser(null);
      router.replace("/home");
    } catch (error) {
      localStorage.removeItem("auth_token");
      setIsAuthenticated(false);
      setUser(null);
      router.replace("/home");
    }
  };

  const handleModeChange = (mode: AppMode) => {
    setActiveMode(mode);
  };

  const handleUpdateProfile = async (data: {
    full_name?: string;
    profile_picture?: string;
  }) => {
    try {
      const updatedProfile = await authApi.updateProfile(data);
      setUser(updatedProfile);
      toast.success("Profile updated");
    } catch (error) {
      toast.error("Failed to update profile");
    }
  };

  // Loading state with refined spinner
  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-6 animate-fade-in">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-2 border-primary/20" />
            <div className="absolute inset-0 h-12 w-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
          <p className="text-sm text-muted-foreground font-medium tracking-wide">
            Loading your workspace...
          </p>
        </div>
      </main>
    );
  }

  // Not authenticated - show nothing while redirecting
  if (!isAuthenticated) {
    return (
      <main className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-6 animate-fade-in">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-2 border-primary/20" />
            <div className="absolute inset-0 h-12 w-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
          <p className="text-sm text-muted-foreground font-medium tracking-wide">
            Redirecting...
          </p>
        </div>
      </main>
    );
  }

  // Authenticated - Show Dual-Mode Application
  return (
    <div className="h-screen flex flex-col overflow-hidden bg-background">
      <AppHeader
        activeMode={activeMode}
        onModeChange={handleModeChange}
        user={user}
        onLogout={handleLogout}
        onUpdateProfile={handleUpdateProfile}
      />
      <div className="flex-1 overflow-hidden">
        {activeMode === "chat" ? <ChatLayout /> : <TasksView />}
      </div>
    </div>
  );
}
