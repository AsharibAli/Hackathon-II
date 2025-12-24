"use client";

import { cn } from "@/lib/utils";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

/**
 * Custom App Logo - Combines a checkmark with AI/chat elements
 * A modern, minimalist logo for an AI-powered todo application
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
      {/* Background circle with gradient */}
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#3B82F6" />
          <stop offset="100%" stopColor="#1D4ED8" />
        </linearGradient>
        <linearGradient id="checkGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#E0E7FF" />
        </linearGradient>
      </defs>
      
      {/* Main circle background */}
      <circle cx="24" cy="24" r="22" fill="url(#logoGradient)" />
      
      {/* Checkmark with AI sparkle effect */}
      <path
        d="M14 24L21 31L34 18"
        stroke="url(#checkGradient)"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      
      {/* AI sparkle dots */}
      <circle cx="36" cy="12" r="2" fill="#93C5FD" opacity="0.9" />
      <circle cx="40" cy="16" r="1.5" fill="#BFDBFE" opacity="0.7" />
      <circle cx="38" cy="10" r="1" fill="#DBEAFE" opacity="0.8" />
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
      <circle cx="24" cy="24" r="22" fill="#3B82F6" />
      <path
        d="M14 24L21 31L34 18"
        stroke="white"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="36" cy="12" r="2" fill="#93C5FD" opacity="0.9" />
      <circle cx="40" cy="16" r="1.5" fill="#BFDBFE" opacity="0.7" />
    </svg>
  );
}
