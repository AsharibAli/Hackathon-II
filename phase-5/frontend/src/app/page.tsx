/**
 * Home page - Dynamic entry point for the Advanced Todo Application.
 * Shows landing page if not authenticated, dual-mode app if authenticated.
 *
 * Dual Mode:
 * - CUI (Conversational User Interface): ChatGPT-style chat for task management
 * - GUI (Graphical User Interface): Traditional forms and lists for task management
 */
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { ChatLayout } from "@/components/chat/ChatLayout";
import { TasksView } from "@/components/tasks";
import { AppHeader, AppMode } from "@/components/navigation";
import { authApi, UserProfile } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowRight,
  Shield,
  Zap,
  MessageSquare,
  ListTodo,
  RefreshCw
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [activeMode, setActiveMode] = useState<AppMode>("chat");
  const [user, setUser] = useState<UserProfile | null>(null);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("auth_token");

    if (token) {
      setIsAuthenticated(true);
      loadUserProfile();
    }
    setIsLoading(false);
  }, []);

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
      setIsAuthenticated(false);
      setUser(null);
      router.refresh();
    } catch (error) {
      // Logout locally even if API fails
      localStorage.removeItem("auth_token");
      setIsAuthenticated(false);
      setUser(null);
      router.refresh();
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

  // Loading state
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

  // Authenticated - Show Dual-Mode Application
  if (isAuthenticated) {
    return (
      <div className="h-screen flex flex-col overflow-hidden">
        {/* App Header with Mode Toggle */}
        <AppHeader
          activeMode={activeMode}
          onModeChange={handleModeChange}
          user={user}
          onLogout={handleLogout}
          onUpdateProfile={handleUpdateProfile}
        />

        {/* Main Content Area */}
        <div className="flex-1 overflow-hidden">
          {activeMode === "chat" ? (
            <ChatLayout />
          ) : (
            <TasksView />
          )}
        </div>
      </div>
    );
  }

  // Not authenticated - Show Landing Page
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Logo size="lg" />
            <span className="text-xl font-bold">TaskAI</span>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/login">
              <Button variant="ghost">Sign In</Button>
            </Link>
            <Link href="/register">
              <Button>Get Started</Button>
            </Link>
          </div>
        </nav>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-4xl mx-auto text-center">
          <div className="mb-8 flex justify-center">
            <div className="relative">
              <div className="h-24 w-24 rounded-full bg-gradient-to-br from-blue-500/20 to-blue-500/5 flex items-center justify-center">
                <Logo size="lg" className="h-14 w-14" />
              </div>
            </div>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6">
            Manage tasks with{" "}
            <span className="text-primary">AI Chat</span>{" "}
            <span className="text-muted-foreground">or</span>{" "}
            <span className="text-primary">Classic UI</span>
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            The most flexible todo app. Choose how you work - chat naturally with AI
            or use traditional forms and buttons. Switch anytime, your tasks stay in sync.
          </p>
          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2 w-full sm:w-auto">
                Start for Free
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="w-full sm:w-auto">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-20 max-w-4xl mx-auto">
          {/* CUI Feature */}
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <MessageSquare className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Conversational AI</h3>
            <p className="text-muted-foreground text-sm">
              Chat naturally with AI to manage your tasks. Just say what you need -
              no buttons or forms required.
            </p>
          </div>

          {/* GUI Feature */}
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <ListTodo className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Classic Interface</h3>
            <p className="text-muted-foreground text-sm">
              Prefer traditional UI? Use forms, checkboxes, and buttons to manage
              your tasks with familiar controls.
            </p>
          </div>

          {/* Sync Feature */}
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm hover:shadow-md transition-shadow">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <RefreshCw className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Switch Anytime</h3>
            <p className="text-muted-foreground text-sm">
              Both interfaces share the same tasks. Create in chat, edit in UI -
              everything stays perfectly in sync.
            </p>
          </div>
        </div>

        {/* Additional Benefits */}
        <div className="grid sm:grid-cols-2 gap-6 mt-12 max-w-2xl mx-auto">
          <div className="flex items-start gap-4 p-4">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Shield className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h4 className="font-medium mb-1">Secure & Private</h4>
              <p className="text-sm text-muted-foreground">
                Your data is protected with industry-standard security and encryption.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-4 p-4">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
              <Zap className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h4 className="font-medium mb-1">Lightning Fast</h4>
              <p className="text-sm text-muted-foreground">
                Optimized for speed. Add tasks, switch modes, and get things done instantly.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-16 border-t">
        <div className="text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} TaskAI. CUI + GUI powered by AI.</p>
        </div>
      </footer>
    </div>
  );
}
