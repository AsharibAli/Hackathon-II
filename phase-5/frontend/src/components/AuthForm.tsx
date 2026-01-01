/**
 * AuthForm component.
 * Neo-Editorial styled authentication form with login/register modes.
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  GoogleOAuthProvider,
  GoogleLogin,
  CredentialResponse,
} from "@react-oauth/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { authApi, ApiError } from "@/lib/api";
import { toast } from "sonner";
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  Sparkles,
  UserPlus,
  LogIn,
  AlertCircle,
} from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { cn } from "@/lib/utils";

interface AuthFormProps {
  mode: "login" | "register";
}

interface AuthFormContentProps extends AuthFormProps {
  googleEnabled: boolean;
}

function AuthFormContent({ mode, googleEnabled }: AuthFormContentProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [errors, setErrors] = useState<{
    email?: string;
    password?: string;
    general?: string;
  }>({});

  const isLogin = mode === "login";
  const title = isLogin ? "Welcome Back" : "Create Account";
  const description = isLogin
    ? "Sign in to continue managing your tasks"
    : "Start your productivity journey today";
  const submitText = isLogin ? "Sign In" : "Create Account";
  const switchText = isLogin
    ? "Don't have an account?"
    : "Already have an account?";
  const switchLink = isLogin ? "/register" : "/login";
  const switchLinkText = isLogin ? "Sign up" : "Sign in";

  const validateForm = (): boolean => {
    const newErrors: typeof errors = {};

    if (!email) {
      newErrors.email = "Email is required";
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = "Invalid email format";
    }

    if (!password) {
      newErrors.password = "Password is required";
    } else if (!isLogin && password.length < 8) {
      newErrors.password = "Password must be at least 8 characters";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);
    setErrors({});

    try {
      if (isLogin) {
        await authApi.login({ email, password });
        toast.success("Logged in successfully!");
      } else {
        await authApi.register({ email, password });
        toast.success("Account created successfully!");
      }

      router.push("/");
      router.refresh();
    } catch (error) {
      if (error instanceof ApiError) {
        const detail = error.data?.detail || error.statusText;
        setErrors({ general: detail });
        toast.error(detail);
      } else {
        setErrors({ general: "An unexpected error occurred" });
        toast.error("An unexpected error occurred");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      setErrors({ general: "Failed to get Google credentials" });
      toast.error("Failed to get Google credentials");
      return;
    }

    setIsGoogleLoading(true);
    setErrors({});

    try {
      const parts = credentialResponse.credential.split(".");
      const base64Url = parts[1];
      if (!base64Url) {
        throw new Error("Invalid JWT token format");
      }
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      );
      const userInfo = JSON.parse(jsonPayload);

      await authApi.oauthLogin({
        email: userInfo.email,
        provider: "google",
        provider_user_id: userInfo.sub,
        full_name: userInfo.name,
        profile_picture: userInfo.picture,
      });

      toast.success("Signed in with Google!");
      router.push("/");
      router.refresh();
    } catch (error) {
      console.error("Google sign-in error:", error);
      if (error instanceof ApiError) {
        const detail = error.data?.detail || error.statusText;
        setErrors({ general: detail });
        toast.error(detail);
      } else {
        setErrors({ general: "Failed to sign in with Google" });
        toast.error("Failed to sign in with Google");
      }
    } finally {
      setIsGoogleLoading(false);
    }
  };

  const handleGoogleError = () => {
    setErrors({ general: "Google sign-in was cancelled or failed" });
    toast.error("Google sign-in failed");
  };

  return (
    <div className="w-full max-w-md mx-auto">
      {/* Card */}
      <div className="rounded-2xl border border-border/60 bg-card shadow-elevated overflow-hidden">
        {/* Header */}
        <div className="px-8 pt-8 pb-6 text-center border-b border-border/50 bg-muted/20">
          <div className="mx-auto mb-6">
            <Logo size="lg" />
          </div>
          <div className="flex items-center justify-center gap-2 mb-3">
            {isLogin ? (
              <LogIn className="h-5 w-5 text-primary" />
            ) : (
              <UserPlus className="h-5 w-5 text-primary" />
            )}
            <h1 className="font-display text-2xl font-semibold tracking-tight">
              {title}
            </h1>
          </div>
          <p className="text-sm text-muted-foreground">{description}</p>
        </div>

        {/* Content */}
        <div className="p-8 space-y-6">
          {/* Google Sign-In Button */}
          {googleEnabled && (
            <>
              <div className="flex justify-center">
                <GoogleLogin
                  onSuccess={handleGoogleSuccess}
                  onError={handleGoogleError}
                  theme="outline"
                  size="large"
                  width="100%"
                  text="continue_with"
                  shape="rectangular"
                />
              </div>

              {/* Divider */}
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t border-border/50" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-3 text-muted-foreground">
                    Or continue with email
                  </span>
                </div>
              </div>
            </>
          )}

          {/* Email/Password Form */}
          <form onSubmit={handleSubmit} className="space-y-5">
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
                  disabled={isLoading || isGoogleLoading}
                  aria-invalid={!!errors.email}
                  className={cn(
                    "h-12 pl-11 rounded-xl bg-background/80",
                    errors.email && "border-destructive focus-visible:ring-destructive/30"
                  )}
                />
              </div>
              {errors.email && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {errors.email}
                </p>
              )}
            </div>

            {/* Password */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                {isLogin && (
                  <Link
                    href="/forgot-password"
                    className="text-xs text-primary hover:text-primary/80 transition-colors"
                  >
                    Forgot password?
                  </Link>
                )}
              </div>
              <div className="relative">
                <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  placeholder={isLogin ? "Enter password" : "Min 8 characters"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={isLoading || isGoogleLoading}
                  aria-invalid={!!errors.password}
                  className={cn(
                    "h-12 pl-11 pr-11 rounded-xl bg-background/80",
                    errors.password && "border-destructive focus-visible:ring-destructive/30"
                  )}
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
              {errors.password && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {errors.password}
                </p>
              )}
            </div>

            {/* Error message */}
            {errors.general && (
              <div className="flex items-start gap-3 p-4 text-sm text-destructive bg-destructive/10 rounded-xl border border-destructive/20">
                <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                {errors.general}
              </div>
            )}

            {/* Submit button */}
            <Button
              type="submit"
              className="w-full h-12 rounded-xl gap-2 shadow-soft hover:shadow-elevated transition-all"
              disabled={isLoading || isGoogleLoading}
            >
              {isLoading ? (
                <>
                  <div className="h-4 w-4 rounded-full border-2 border-primary-foreground border-t-transparent animate-spin" />
                  {isLogin ? "Signing in..." : "Creating account..."}
                </>
              ) : (
                <>
                  {isLogin ? (
                    <ArrowRight className="h-4 w-4" />
                  ) : (
                    <Sparkles className="h-4 w-4" />
                  )}
                  {submitText}
                </>
              )}
            </Button>
          </form>
        </div>

        {/* Footer */}
        <div className="px-8 py-5 bg-muted/20 border-t border-border/50 text-center">
          <p className="text-sm text-muted-foreground">
            {switchText}{" "}
            <Link
              href={switchLink}
              className="font-medium text-primary hover:text-primary/80 transition-colors"
            >
              {switchLinkText}
            </Link>
          </p>
        </div>
      </div>

      {/* Terms */}
      {!isLogin && (
        <p className="mt-6 text-xs text-center text-muted-foreground/60">
          By creating an account, you agree to our{" "}
          <Link href="#" className="underline hover:text-muted-foreground">
            Terms of Service
          </Link>{" "}
          and{" "}
          <Link href="#" className="underline hover:text-muted-foreground">
            Privacy Policy
          </Link>
        </p>
      )}
    </div>
  );
}

export function AuthForm({ mode }: AuthFormProps) {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  if (!googleClientId) {
    return <AuthFormContent mode={mode} googleEnabled={false} />;
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthFormContent mode={mode} googleEnabled={true} />
    </GoogleOAuthProvider>
  );
}
