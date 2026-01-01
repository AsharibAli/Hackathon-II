/**
 * Root layout for the TaskAI application.
 * Neo-Editorial design with Cormorant Garamond + DM Sans typography.
 */
import type { Metadata, Viewport } from "next";
import { Cormorant_Garamond, DM_Sans, JetBrains_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";
import { Providers } from "@/components/Providers";

// Display font - Elegant serif for headings
const cormorant = Cormorant_Garamond({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-cormorant",
  display: "swap",
});

// Body font - Clean geometric sans-serif
const dmSans = DM_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-dm-sans",
  display: "swap",
});

// Mono font - For code and technical content
const jetbrainsMono = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-jetbrains-mono",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TaskAI - Intelligent Task Management",
  description:
    "A sophisticated AI-powered task management application. Manage your tasks with natural language AI chat or a refined visual interface.",
  keywords: ["task management", "AI assistant", "todo app", "productivity"],
  authors: [{ name: "TaskAI" }],
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/favicon.svg",
  },
  openGraph: {
    title: "TaskAI - Intelligent Task Management",
    description: "AI-powered task management with natural language interface",
    type: "website",
  },
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#faf9f7" },
    { media: "(prefers-color-scheme: dark)", color: "#141517" },
  ],
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${cormorant.variable} ${dmSans.variable} ${jetbrainsMono.variable} font-sans`}
      >
        <Providers>
          <div className="relative min-h-screen">
            {/* Subtle gradient mesh background */}
            <div
              className="fixed inset-0 -z-10 gradient-mesh opacity-50 dark:opacity-30"
              aria-hidden="true"
            />
            {children}
          </div>
        </Providers>
        <Toaster
          position="top-right"
          richColors
          toastOptions={{
            classNames: {
              toast: "glass-card shadow-elevated",
              title: "font-medium",
              description: "text-muted-foreground",
            },
          }}
        />
      </body>
    </html>
  );
}
