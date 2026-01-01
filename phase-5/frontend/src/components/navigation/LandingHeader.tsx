/**
 * LandingHeader component.
 * Header for landing pages with navigation and theme toggle.
 * Shows different buttons based on authentication state.
 */
"use client";

import Link from "next/link";
import { Moon, Sun, ArrowRight } from "lucide-react";
import { useTheme } from "next-themes";
import { Logo } from "@/components/ui/Logo";
import { Button } from "@/components/ui/button";

interface LandingHeaderProps {
  isAuthenticated?: boolean;
}

export function LandingHeader({ isAuthenticated = false }: LandingHeaderProps) {
  const { theme, setTheme } = useTheme();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 glass border-b border-border/50">
      <nav className="container-wide py-4">
        <div className="flex justify-between items-center">
          <Link href="/home" className="flex items-center gap-3 group">
            <Logo size="lg" />
            <span className="text-xl font-display font-semibold tracking-tight">
              TaskAI
            </span>
          </Link>
          <div className="flex items-center gap-2">
            {/* Theme toggle */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
              className="h-9 w-9 rounded-full text-muted-foreground hover:text-foreground"
            >
              <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
              <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
              <span className="sr-only">Toggle theme</span>
            </Button>

            {isAuthenticated ? (
              <>
                {/* Authenticated user buttons */}
                <Link href="/">
                  <Button size="sm" className="font-medium shadow-soft gap-2">
                    Open App
                    <ArrowRight className="h-3.5 w-3.5" />
                  </Button>
                </Link>
              </>
            ) : (
              <>
                {/* Unauthenticated user buttons */}
                <Link href="/login">
                  <Button variant="ghost" size="sm" className="font-medium">
                    Sign In
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm" className="font-medium shadow-soft">
                    Get Started
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
