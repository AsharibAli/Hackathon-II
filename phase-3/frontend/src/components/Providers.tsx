/**
 * Providers component.
 * Wraps the app with error boundary and other providers.
 */
"use client";

import { ErrorBoundary } from "@/components/ErrorBoundary";

export function Providers({ children }: { children: React.ReactNode }) {
  return <ErrorBoundary>{children}</ErrorBoundary>;
}
