/**
 * Home/Landing page - Marketing page for TaskAI.
 * Neo-Editorial design with sophisticated typography and warm aesthetics.
 * Shows different CTAs based on authentication state.
 */
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  ArrowRight,
  Shield,
  Zap,
  MessageSquare,
  ListTodo,
  RefreshCw,
  Sparkles,
  Calendar,
  Tag,
  Bell,
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { LandingHeader } from "@/components/navigation";

export default function HomePage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [previewMode, setPreviewMode] = useState<"gui" | "cui">("gui");

  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    setIsAuthenticated(!!token);
    setIsLoading(false);
  }, []);

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-6 animate-fade-in">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-2 border-primary/20" />
            <div className="absolute inset-0 h-12 w-12 rounded-full border-2 border-primary border-t-transparent animate-spin" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      {/* Navigation with theme toggle */}
      <LandingHeader isAuthenticated={isAuthenticated} />

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-40 lg:pb-32 overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-accent/5 rounded-full blur-3xl" />

        <div className="container-wide relative">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/5 border border-primary/10 mb-8 animate-fade-down">
              <Sparkles className="h-4 w-4 text-primary" />
              <span className="text-sm font-medium text-primary">
                AI-Powered Task Management
              </span>
            </div>

            {/* Main heading */}
            <h1 className="font-display text-5xl md:text-6xl lg:text-7xl font-semibold tracking-tight mb-6 animate-fade-up">
              Organize your life,{" "}
              <span className="gradient-text">your way</span>
            </h1>

            {/* Subheading */}
            <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 leading-relaxed animate-fade-up delay-100">
              The most flexible task manager. Chat naturally with AI or use a
              refined visual interface. Switch seamlessly between modes - your
              tasks stay perfectly in sync.
            </p>

            {/* CTA buttons - Different for authenticated vs unauthenticated */}
            <div className="flex flex-col sm:flex-row justify-center gap-4 animate-fade-up delay-200">
              {isAuthenticated ? (
                <Link href="/">
                  <Button
                    size="lg"
                    className="gap-2 w-full sm:w-auto px-8 shadow-elevated hover:shadow-soft transition-shadow"
                  >
                    Try the App
                    <ArrowRight className="h-4 w-4" />
                  </Button>
                </Link>
              ) : (
                <>
                  <Link href="/register">
                    <Button
                      size="lg"
                      className="gap-2 w-full sm:w-auto px-8 shadow-elevated hover:shadow-soft transition-shadow"
                    >
                      Start for Free
                      <ArrowRight className="h-4 w-4" />
                    </Button>
                  </Link>
                  <Link href="/login">
                    <Button
                      size="lg"
                      variant="outline"
                      className="w-full sm:w-auto px-8"
                    >
                      Sign In
                    </Button>
                  </Link>
                </>
              )}
            </div>
          </div>

          {/* Mode preview cards */}
          <div className="mt-20 grid md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            {/* Chat Mode Card */}
            <div className="group relative p-8 rounded-2xl bg-card border shadow-card hover:shadow-elevated transition-all duration-300 animate-slide-in-left delay-300">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-primary to-accent rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="flex items-center gap-4 mb-4">
                <div className="h-14 w-14 rounded-xl bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="h-7 w-7 text-primary" />
                </div>
                <div>
                  <h3 className="font-display text-xl font-semibold">
                    Chat Mode
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Natural language AI
                  </p>
                </div>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                Simply tell the AI what you need. &quot;Add a task for tomorrow&quot;,
                &quot;Show my high priority items&quot;, &quot;Mark grocery shopping complete&quot;
                - it understands naturally.
              </p>
              <div className="mt-6 flex flex-wrap gap-2">
                <span className="tag-chip">Voice-like input</span>
                <span className="tag-chip">Context-aware</span>
                <span className="tag-chip">Instant actions</span>
              </div>
            </div>

            {/* Tasks Mode Card */}
            <div className="group relative p-8 rounded-2xl bg-card border shadow-card hover:shadow-elevated transition-all duration-300 animate-slide-in-right delay-300">
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-accent to-primary rounded-t-2xl opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="flex items-center gap-4 mb-4">
                <div className="h-14 w-14 rounded-xl bg-accent/10 flex items-center justify-center">
                  <ListTodo className="h-7 w-7 text-accent" />
                </div>
                <div>
                  <h3 className="font-display text-xl font-semibold">
                    Tasks Mode
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Visual interface
                  </p>
                </div>
              </div>
              <p className="text-muted-foreground leading-relaxed">
                A refined, traditional interface with forms, filters, and
                checkboxes. Drag, drop, sort, and organize with familiar
                controls you already know.
              </p>
              <div className="mt-6 flex flex-wrap gap-2">
                <span className="tag-chip">Visual overview</span>
                <span className="tag-chip">Bulk actions</span>
                <span className="tag-chip">Quick edits</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 lg:py-32 border-t border-border/50">
        <div className="container-wide">
          <div className="text-center mb-16">
            <h2 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mb-4">
              Everything you need to stay organized
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Powerful features wrapped in an elegant, intuitive interface.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Priority Feature */}
            <div className="group p-6 rounded-xl bg-card border hover:border-primary/30 transition-all duration-300">
              <div className="h-12 w-12 rounded-lg bg-red-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Zap className="h-6 w-6 text-red-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Smart Priorities</h3>
              <p className="text-sm text-muted-foreground">
                Set high, medium, or low priority. Filter and sort to focus on
                what matters most.
              </p>
            </div>

            {/* Due Dates Feature */}
            <div className="group p-6 rounded-xl bg-card border hover:border-primary/30 transition-all duration-300">
              <div className="h-12 w-12 rounded-lg bg-blue-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Calendar className="h-6 w-6 text-blue-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Natural Dates</h3>
              <p className="text-sm text-muted-foreground">
                Say &quot;next Monday&quot; or &quot;in 3 days&quot;. Our AI understands natural
                language dates automatically.
              </p>
            </div>

            {/* Tags Feature */}
            <div className="group p-6 rounded-xl bg-card border hover:border-primary/30 transition-all duration-300">
              <div className="h-12 w-12 rounded-lg bg-emerald-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Tag className="h-6 w-6 text-emerald-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Flexible Tags</h3>
              <p className="text-sm text-muted-foreground">
                Organize with custom tags. Filter by category, project, or any
                label you create.
              </p>
            </div>

            {/* Reminders Feature */}
            <div className="group p-6 rounded-xl bg-card border hover:border-primary/30 transition-all duration-300">
              <div className="h-12 w-12 rounded-lg bg-amber-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <Bell className="h-6 w-6 text-amber-500" />
              </div>
              <h3 className="font-semibold text-lg mb-2">Smart Reminders</h3>
              <p className="text-sm text-muted-foreground">
                Never miss a deadline. Set reminders for &quot;1 hour before&quot; or any
                specific time.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-20 lg:py-32 bg-muted/30">
        <div className="container-wide">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mb-6">
                Two interfaces,{" "}
                <span className="text-primary">one unified experience</span>
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed mb-8">
                Whether you prefer the speed of conversational AI or the control
                of a visual interface, TaskAI adapts to your workflow. Switch
                modes with a single click.
              </p>

              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <RefreshCw className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Seamless Sync</h4>
                    <p className="text-sm text-muted-foreground">
                      Create a task in chat, edit it in the visual interface.
                      Everything stays perfectly synchronized.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Shield className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Private & Secure</h4>
                    <p className="text-sm text-muted-foreground">
                      Your data is protected with industry-standard encryption.
                      We never share your information.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4">
                  <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                    <Zap className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <h4 className="font-medium mb-1">Lightning Fast</h4>
                    <p className="text-sm text-muted-foreground">
                      Optimized for speed. Add tasks instantly and switch modes
                      without any delay.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Visual element */}
            <div className="relative">
              <div className="relative p-8 rounded-2xl bg-card border shadow-elevated">
                <div className="absolute -top-4 -right-4 h-24 w-24 bg-primary/10 rounded-full blur-2xl" />
                <div className="absolute -bottom-4 -left-4 h-32 w-32 bg-accent/10 rounded-full blur-2xl" />

                {/* Mock interface */}
                <div className="relative space-y-4 min-h-[280px]">
                  <div className="flex items-center justify-between pb-4 border-b">
                    <div className="flex items-center gap-2">
                       <span className="font-display text-lg font-semibold">
                        {previewMode === "gui" ? "My Tasks" : "TaskAI Chat"}
                      </span>
                      <div className="flex items-center gap-1.5 ml-2 px-2 py-0.5 rounded-full bg-primary/10 text-[10px] font-bold uppercase tracking-wider text-primary">
                        {previewMode === "gui" ? "GUI" : "CUI"}
                      </div>
                    </div>
                    
                    {/* Interface Toggle Switch */}
                    <div className="flex items-center bg-muted rounded-lg p-1">
                      <button
                        onClick={() => setPreviewMode("gui")}
                        className={`p-1.5 rounded-md transition-all ${
                          previewMode === "gui"
                            ? "bg-card shadow-sm text-primary"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                        title="Traditional UI"
                      >
                        <ListTodo className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => setPreviewMode("cui")}
                        className={`p-1.5 rounded-md transition-all ${
                          previewMode === "cui"
                            ? "bg-card shadow-sm text-primary"
                            : "text-muted-foreground hover:text-foreground"
                        }`}
                        title="Conversational UI"
                      >
                        <MessageSquare className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {previewMode === "gui" ? (
                    <div className="space-y-4 animate-fade-in">
                      {/* Mock task items */}
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-transparent hover:border-primary/20 transition-colors cursor-default group">
                        <div className="h-5 w-5 rounded border-2 border-muted-foreground/30 group-hover:border-primary/50 transition-colors" />
                        <span className="flex-1 text-sm font-medium">Review quarterly report</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase priority-high">
                          high
                        </span>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-transparent hover:border-primary/20 transition-colors cursor-default group">
                        <div className="h-5 w-5 rounded border-2 border-muted-foreground/30 group-hover:border-primary/50 transition-colors" />
                        <span className="flex-1 text-sm font-medium">Call with design team</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase priority-medium">
                          medium
                        </span>
                      </div>
                      <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 border border-transparent hover:border-primary/20 transition-colors cursor-default group">
                        <div className="h-5 w-5 rounded border-2 border-muted-foreground/30 group-hover:border-primary/50 transition-colors" />
                        <span className="flex-1 text-sm font-medium">Update documentation</span>
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold uppercase priority-low">
                          low
                        </span>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-4 animate-fade-in">
                      {/* Chat Messages */}
                      <div className="flex flex-col gap-3">
                        <div className="flex items-start gap-2 max-w-[85%]">
                          <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <Sparkles className="h-3 w-3 text-primary" />
                          </div>
                          <div className="p-2.5 rounded-2xl rounded-tl-none bg-muted/50 text-xs leading-relaxed">
                            Hello! You have 3 pending tasks. What would you like to do?
                          </div>
                        </div>
                        
                        <div className="flex items-start gap-2 ml-auto max-w-[85%]">
                          <div className="p-2.5 rounded-2xl rounded-tr-none bg-primary text-primary-foreground text-xs shadow-soft leading-relaxed">
                            Show my high priority tasks.
                          </div>
                        </div>

                        <div className="flex items-start gap-2 max-w-[85%]">
                          <div className="h-6 w-6 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                            <Sparkles className="h-3 w-3 text-primary" />
                          </div>
                          <div className="p-2.5 rounded-2xl rounded-tl-none bg-muted/50 text-xs leading-relaxed">
                            You have one high priority task: <span className="font-semibold italic">&quot;Review quarterly report&quot;</span>. 
                            Would you like me to mark it as complete?
                          </div>
                        </div>
                      </div>
                      
                      {/* Input mockup */}
                      <div className="mt-4 p-2.5 rounded-xl bg-muted/30 border border-border/50 flex items-center gap-2">
                        <span className="text-[10px] text-muted-foreground">Type a command...</span>
                        <div className="ml-auto h-5 w-5 rounded-md bg-primary/10 flex items-center justify-center text-primary">
                          <ArrowRight className="h-3 w-3" />
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 lg:py-32">
        <div className="container-wide">
          <div className="relative max-w-3xl mx-auto text-center p-12 rounded-3xl bg-gradient-to-br from-primary/5 via-card to-accent/5 border shadow-card">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
              <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center shadow-elevated">
                <Sparkles className="h-10 w-10 text-primary" />
              </div>
            </div>

            <h2 className="font-display text-3xl md:text-4xl font-semibold tracking-tight mb-4 mt-4">
              {isAuthenticated ? "Your tasks await!" : "Ready to get organized?"}
            </h2>
            <p className="text-muted-foreground text-lg mb-8">
              {isAuthenticated
                ? "Jump back into your workspace and stay productive."
                : "Join thousands who have transformed their productivity with TaskAI."}
            </p>
            <Link href={isAuthenticated ? "/" : "/register"}>
              <Button
                size="lg"
                className="px-10 shadow-elevated hover:shadow-soft transition-shadow"
              >
                {isAuthenticated ? "Go to Dashboard" : "Start Free Today"}
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/50 py-12">
        <div className="container-wide">
          <div className="flex flex-col md:flex-row justify-between items-center gap-6">
            <div className="flex items-center gap-3">
              <Logo size="md" />
              <span className="font-display font-semibold">TaskAI</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Build with ❤️ by{" "}
              <Link
                href="https://asharib.xyz/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-foreground hover:text-primary transition-colors underline-offset-4 hover:underline"
              >
                Asharib Ali
              </Link>
            </p>
            <p className="text-sm text-muted-foreground">
              &copy; {new Date().getFullYear()} TaskAI. Intelligent task
              management.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
