"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import Link from "next/link";

/**
 * Home page - Entry point for the Todo application.
 * Redirects to /app if authenticated, otherwise shows landing page.
 */
export default function Home() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem("auth_token");
    
    if (token) {
      // User is authenticated, redirect to app
      router.push("/app");
    } else {
      // Not authenticated, show landing page
      setIsLoading(false);
    }
  }, [router]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <main className="min-h-screen flex items-center justify-center bg-background">
        <p className="text-muted-foreground">Loading...</p>
      </main>
    );
  }

  return (
    <main className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">Todo App</h1>
        <p className="text-muted-foreground">
          A modern, secure, multi-user todo application
        </p>
        <Link href="/register">
          <Button className="mt-4">Get Started</Button>
        </Link>
      </div>
    </main>
  );
}
