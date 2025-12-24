/**
 * Authentication layout with redirect logic.
 * Redirects to main app if user is already authenticated.
 */
"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check if user is already authenticated
    const token = localStorage.getItem("auth_token");

    if (token) {
      // User is authenticated, redirect to main app
      router.push("/");
    } else {
      setIsChecking(false);
    }
  }, [router]);

  // Show nothing while checking authentication status
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      {children}
    </div>
  );
}
