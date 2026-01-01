"use client";

import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

/**
 * Custom App Logo - Neo-Editorial styled
 * A modern, warm logo for an AI-powered todo application
 * Uses terracotta primary color (#C1666B)
 */
export function Logo({ className, size = "md" }: LogoProps) {
  const sizeClasses = {
    sm: "h-6 w-6",
    md: "h-8 w-8",
    lg: "h-10 w-10",
  };

  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={cn(sizeClasses[size], className)}
    >
      {/* Background circle with gradient - Terracotta theme */}
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#D4847A" />
          <stop offset="100%" stopColor="#A85751" />
        </linearGradient>
      </defs>

      {/* Main circle background */}
      <circle cx="24" cy="24" r="22" fill="url(#logoGradient)" />

      {/* Checkmark */}
      <path
        d="M14 24L21 31L34 18"
        stroke="white"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}

/**
 * Logo Icon only (for favicon-like use)
 */
export function LogoIcon({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <circle cx="24" cy="24" r="22" fill="#C1666B" />
      <path
        d="M14 24L21 31L34 18"
        stroke="white"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
    </svg>
  );
}
