/**
 * Home page - Dynamic entry point for the Todo application.
 * Shows tasks if authenticated, landing page if not.
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ChatInterface } from "@/components/ChatInterface";
import { authApi } from "@/lib/api";
import { toast } from "sonner";
import { 
  CheckSquare, 
  LogOut, 
  ArrowRight,
  Shield,
  Zap,
  Users
} from "lucide-react";

export default function Home() {
  const router = useRouter();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("auth_token");
    
    if (token) {
      setIsAuthenticated(true);
    }
    setIsLoading(false);
  }, []);

  const handleLogout = async () => {
    try {
      await authApi.logout();
      toast.success("Logged out successfully");
      setIsAuthenticated(false);
      router.refresh();
    } catch {
      authApi.logout();
      setIsAuthenticated(false);
      router.refresh();
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

  // Authenticated - Show Tasks Dashboard
  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-muted/30">
        {/* Header */}
        <header className="container mx-auto px-4 py-6">
          <nav className="flex justify-between items-center">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
                <CheckSquare className="h-6 w-6 text-primary-foreground" />
              </div>
              <div className="flex flex-col">
                <span className="text-xl font-bold">AI-powered Todo App</span>
                <p className="text-xs text-muted-foreground">
                  Chat with your AI assistant to manage tasks
                </p>
              </div>
            </div>
            <Button 
              variant="ghost" 
              onClick={handleLogout} 
              className="gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </nav>
        </header>

        {/* Main content */}
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            <ChatInterface />
          </div>
        </main>
      </div>
    );
  }

  // Not authenticated - Show Landing Page
  return (
    <div className="min-h-screen bg-gradient-to-b from-background to-muted/30">
      {/* Header */}
      <header className="container mx-auto px-4 py-6">
        <nav className="flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary flex items-center justify-center">
              <CheckSquare className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">AI Todo App</span>
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
      <main className="container mx-auto px-4 py-20">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-5xl font-bold tracking-tight mb-6">
            Organize your life with{" "}
            <span className="text-primary">AI-powered Todo App</span>
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
            A modern, secure, and intuitive task management application. 
            Stay focused, get organized, and accomplish more every day.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="gap-2">
                Start for Free
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline">
                Sign In
              </Button>
            </Link>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-8 mt-24 max-w-4xl mx-auto">
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Zap className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Fast & Simple</h3>
            <p className="text-muted-foreground text-sm">
              Create, edit, and complete tasks with ease. No complexity, just productivity.
            </p>
          </div>
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Shield className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Secure</h3>
            <p className="text-muted-foreground text-sm">
              Your data is protected with industry-standard security and encryption.
            </p>
          </div>
          <div className="text-center p-6 rounded-xl bg-card border shadow-sm">
            <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mx-auto mb-4">
              <Users className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-semibold text-lg mb-2">Multi-User</h3>
            <p className="text-muted-foreground text-sm">
              Create your personal account and manage your tasks from anywhere.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="container mx-auto px-4 py-8 mt-20 border-t">
        <div className="text-center text-sm text-muted-foreground">
          <p>© {new Date().getFullYear()} AI-powered Todo App</p>
        </div>
      </footer>
    </div>
  );
}
