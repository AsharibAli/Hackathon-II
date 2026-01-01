/**
 * Providers component.
 * Wraps the app with error boundary, theme provider, and other providers.
 */
"use client";

import { ThemeProvider } from "next-themes";
import { ErrorBoundary } from "@/components/ErrorBoundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      <ErrorBoundary>{children}</ErrorBoundary>
    </ThemeProvider>
  );
}
