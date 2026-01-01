/**
 * Forgot Password page.
 * Neo-Editorial styled multi-step password reset flow.
 */
"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, ApiError } from "@/lib/api";
import { toast } from "sonner";
import {
  ArrowLeft,
  Mail,
  CheckCircle,
  Lock,
  Eye,
  EyeOff,
  KeyRound,
  AlertCircle,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { cn } from "@/lib/utils";

type Step = "email" | "code" | "password" | "success";

export default function ForgotPasswordPage() {
  const [step, setStep] = useState<Step>("email");
  const [email, setEmail] = useState("");
  const [code, setCode] = useState(["", "", "", "", "", ""]);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const codeInputRefs = useRef<(HTMLInputElement | null)[]>([]);

  useEffect(() => {
    if (step === "code" && codeInputRefs.current[0]) {
      codeInputRefs.current[0].focus();
    }
  }, [step]);

  const validateEmail = (): boolean => {
    if (!email) {
      setError("Email is required");
      return false;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setError("Invalid email format");
      return false;
    }
    setError("");
    return true;
  };

  const handleSendCode = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateEmail()) {
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      await authApi.forgotPassword(email);
      toast.success("Verification code sent!");
      setStep("code");
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || error.statusText;
        setError(detail);
        toast.error(detail);
      } else {
        setError("An unexpected error occurred");
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleCodeChange = (index: number, value: string) => {
    if (value.length > 1) {
      value = value.slice(-1);
    }
    if (value && !/^[0-9]$/.test(value)) {
      return;
    }

    const newCode = [...code];
    newCode[index] = value;
    setCode(newCode);

    if (value && index < 5) {
      codeInputRefs.current[index + 1]?.focus();
    }
  };

  const handleCodeKeyDown = (
    index: number,
    e: React.KeyboardEvent<HTMLInputElement>
  ) => {
    if (e.key === "Backspace" && !code[index] && index > 0) {
      codeInputRefs.current[index - 1]?.focus();
    }
  };

  const handleCodePaste = (e: React.ClipboardEvent) => {
    e.preventDefault();
    const pastedData = e.clipboardData
      .getData("text")
      .replace(/\D/g, "")
      .slice(0, 6);
    if (pastedData.length === 6) {
      setCode(pastedData.split(""));
      codeInputRefs.current[5]?.focus();
    }
  };

  const handleVerifyCode = async (e: React.FormEvent) => {
    e.preventDefault();

    const codeString = code.join("");
    if (codeString.length !== 6) {
      setError("Please enter the complete 6-digit code");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const result = await authApi.verifyResetCode(email, codeString);
      if (result.valid) {
        toast.success("Code verified!");
        setStep("password");
      } else {
        setError(result.message);
        toast.error(result.message);
      }
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || error.statusText;
        setError(detail);
        toast.error(detail);
      } else {
        setError("An unexpected error occurred");
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!password) {
      setError("Password is required");
      return;
    }
    if (password.length < 8) {
      setError("Password must be at least 8 characters");
      return;
    }
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);
    setError("");

    try {
      const codeString = code.join("");
      await authApi.resetPassword(email, codeString, password);
      toast.success("Password reset successfully!");
      setStep("success");
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || error.statusText;
        setError(detail);
        toast.error(detail);
      } else {
        setError("An unexpected error occurred");
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Success state
  if (step === "success") {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="rounded-2xl border border-border/60 bg-card shadow-elevated overflow-hidden">
          <div className="p-8 text-center space-y-6">
            <div className="mx-auto h-16 w-16 rounded-full bg-emerald-500/10 flex items-center justify-center">
              <CheckCircle className="h-8 w-8 text-emerald-600 dark:text-emerald-400" />
            </div>
            <div>
              <h1 className="font-display text-2xl font-semibold mb-2">
                Password Reset!
              </h1>
              <p className="text-muted-foreground">
                Your password has been successfully reset. You can now sign in
                with your new password.
              </p>
            </div>
            <Link href="/login" className="block">
              <Button className="w-full h-12 rounded-xl gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Sign In
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Password step
  if (step === "password") {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="rounded-2xl border border-border/60 bg-card shadow-elevated overflow-hidden">
          {/* Header */}
          <div className="px-8 pt-8 pb-6 text-center border-b border-border/50 bg-muted/20">
            <div className="mx-auto mb-6">
              <Logo size="lg" />
            </div>
            <div className="flex items-center justify-center gap-2 mb-3">
              <ShieldCheck className="h-5 w-5 text-primary" />
              <h1 className="font-display text-2xl font-semibold tracking-tight">
                Set New Password
              </h1>
            </div>
            <p className="text-sm text-muted-foreground">
              Choose a strong password with at least 8 characters
            </p>
          </div>

          <form onSubmit={handleResetPassword} className="p-8 space-y-5">
            {/* New Password */}
            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium">
                New Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter new password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading}
                  className="h-12 pl-11 pr-11 rounded-xl"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirmPassword" className="text-sm font-medium">
                Confirm Password
              </Label>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="confirmPassword"
                  type={showPassword ? "text" : "password"}
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  disabled={isLoading}
                  className="h-12 pl-11 rounded-xl"
                />
              </div>
            </div>

            {error && (
              <div className="flex items-start gap-3 p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                {error}
              </div>
            )}

            <Button
              type="submit"
              className="w-full h-12 rounded-xl gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                  Resetting...
                </>
              ) : (
                <>
                  <ShieldCheck className="h-4 w-4" />
                  Reset Password
                </>
              )}
            </Button>
          </form>
        </div>
      </div>
    );
  }

  // Code verification step
  if (step === "code") {
    return (
      <div className="w-full max-w-md mx-auto">
        <div className="rounded-2xl border border-border/60 bg-card shadow-elevated overflow-hidden">
          {/* Header */}
          <div className="px-8 pt-8 pb-6 text-center border-b border-border/50 bg-muted/20">
            <div className="mx-auto mb-6">
              <Logo size="lg" />
            </div>
            <div className="flex items-center justify-center gap-2 mb-3">
              <KeyRound className="h-5 w-5 text-primary" />
              <h1 className="font-display text-2xl font-semibold tracking-tight">
                Enter Code
              </h1>
            </div>
            <p className="text-sm text-muted-foreground">
              We&apos;ve sent a 6-digit code to{" "}
              <span className="font-medium text-foreground">{email}</span>
            </p>
          </div>

          <form onSubmit={handleVerifyCode} className="p-8 space-y-6">
            {/* Code Input Boxes */}
            <div
              className="flex justify-center gap-3"
              onPaste={handleCodePaste}
            >
              {code.map((digit, index) => (
                <Input
                  key={index}
                  ref={(el) => {
                    codeInputRefs.current[index] = el;
                  }}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  onKeyDown={(e) => handleCodeKeyDown(index, e)}
                  disabled={isLoading}
                  className={cn(
                    "w-12 h-14 text-center text-2xl font-bold rounded-xl",
                    "focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary",
                    digit && "border-primary/50 bg-primary/5"
                  )}
                />
              ))}
            </div>

            <p className="text-xs text-muted-foreground text-center">
              Code expires in 15 minutes
            </p>

            {error && (
              <div className="flex items-start gap-3 p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                {error}
              </div>
            )}

            <div className="text-sm text-muted-foreground text-center">
              Didn&apos;t receive the code?{" "}
              <button
                type="button"
                onClick={() => {
                  setCode(["", "", "", "", "", ""]);
                  setError("");
                  handleSendCode({ preventDefault: () => {} } as React.FormEvent);
                }}
                className="font-medium text-primary hover:text-primary/80 transition-colors inline-flex items-center gap-1"
                disabled={isLoading}
              >
                <RefreshCw className="h-3 w-3" />
                Resend
              </button>
            </div>

            <div className="space-y-3">
              <Button
                type="submit"
                className="w-full h-12 rounded-xl gap-2"
                disabled={isLoading || code.join("").length !== 6}
              >
                {isLoading ? (
                  <>
                    <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                    Verifying...
                  </>
                ) : (
                  "Verify Code"
                )}
              </Button>

              <Button
                type="button"
                variant="ghost"
                className="w-full h-11 rounded-xl gap-2"
                onClick={() => setStep("email")}
              >
                <ArrowLeft className="h-4 w-4" />
                Change Email
              </Button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  // Email step (default)
  return (
    <div className="w-full max-w-md mx-auto">
      <div className="rounded-2xl border border-border/60 bg-card shadow-elevated overflow-hidden">
        {/* Header */}
        <div className="px-8 pt-8 pb-6 text-center border-b border-border/50 bg-muted/20">
          <div className="mx-auto mb-6">
            <Logo size="lg" />
          </div>
          <div className="flex items-center justify-center gap-2 mb-3">
            <KeyRound className="h-5 w-5 text-primary" />
            <h1 className="font-display text-2xl font-semibold tracking-tight">
              Forgot Password?
            </h1>
          </div>
          <p className="text-sm text-muted-foreground">
            Enter your email and we&apos;ll send you a verification code
          </p>
        </div>

        <form onSubmit={handleSendCode} className="p-8 space-y-5">
          {/* Email */}
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">
              Email
            </Label>
            <div className="relative">
              <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={isLoading}
                className="h-12 pl-11 rounded-xl"
                aria-invalid={!!error}
              />
            </div>
            {error && (
              <p className="text-sm text-destructive flex items-center gap-1">
                <AlertCircle className="h-3 w-3" />
                {error}
              </p>
            )}
          </div>

          <div className="space-y-3">
            <Button
              type="submit"
              className="w-full h-12 rounded-xl gap-2"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Mail className="h-4 w-4" />
                  Send Code
                </>
              )}
            </Button>

            <Link href="/login" className="block">
              <Button
                variant="ghost"
                className="w-full h-11 rounded-xl gap-2"
                type="button"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Sign In
              </Button>
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
