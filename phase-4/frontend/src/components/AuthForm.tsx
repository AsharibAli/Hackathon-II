/**
 * Reusable authentication form component.
 * Handles both login and registration with validation and Google OAuth.
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { GoogleOAuthProvider, useGoogleLogin } from "@react-oauth/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { authApi, ApiError } from "@/lib/api";
import { toast } from "sonner";

interface AuthFormProps {
  mode: "login" | "register";
}

// Google Icon Component
function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        fill="#4285F4"
      />
      <path
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        fill="#34A853"
      />
      <path
        d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        fill="#FBBC05"
      />
      <path
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        fill="#EA4335"
      />
    </svg>
  );
}

// Google Sign-In Button - separate component that uses the hook
function GoogleSignInButton({ 
  isLoading, 
  onLoadingChange, 
  onError 
}: { 
  isLoading: boolean; 
  onLoadingChange: (loading: boolean) => void;
  onError: (error: string) => void;
}) {
  const router = useRouter();
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setIsGoogleLoading(true);
      onLoadingChange(true);

      try {
        // Get user info from Google using the access token
        const userInfoResponse = await fetch('https://www.googleapis.com/oauth2/v3/userinfo', {
          headers: { Authorization: `Bearer ${tokenResponse.access_token}` },
        });
        
        if (!userInfoResponse.ok) {
          throw new Error("Failed to get Google user info");
        }
        
        const userInfo = await userInfoResponse.json();

        // Call our backend OAuth endpoint
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
          onError(detail);
          toast.error(detail);
        } else {
          onError("Failed to sign in with Google");
          toast.error("Failed to sign in with Google");
        }
      } finally {
        setIsGoogleLoading(false);
        onLoadingChange(false);
      }
    },
    onError: () => {
      onError("Google sign-in was cancelled or failed");
      toast.error("Google sign-in failed");
      setIsGoogleLoading(false);
      onLoadingChange(false);
    },
  });

  const handleGoogleClick = () => {
    setIsGoogleLoading(true);
    onLoadingChange(true);
    googleLogin();
  };

  return (
    <Button
      type="button"
      variant="outline"
      className="w-full h-11 gap-3 font-medium"
      onClick={handleGoogleClick}
      disabled={isGoogleLoading || isLoading}
    >
      {isGoogleLoading ? (
        <div className="h-5 w-5 animate-spin rounded-full border-2 border-current border-t-transparent" />
      ) : (
        <GoogleIcon className="h-5 w-5" />
      )}
      Continue with Google
    </Button>
  );
}

interface AuthFormContentProps extends AuthFormProps {
  googleEnabled: boolean;
}

function AuthFormContent({ mode, googleEnabled }: AuthFormContentProps) {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isGoogleLoading, setIsGoogleLoading] = useState(false);
  const [errors, setErrors] = useState<{ email?: string; password?: string; general?: string }>({});

  const isLogin = mode === "login";
  const title = isLogin ? "Welcome Back" : "Create Account";
  const description = isLogin
    ? "Enter your credentials to access your tasks"
    : "Enter your details to create a new account";
  const submitText = isLogin ? "Sign In" : "Sign Up";
  const switchText = isLogin ? "Don't have an account?" : "Already have an account?";
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

      // Redirect to home page
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

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-2 text-center">
        <CardTitle className="text-2xl font-bold">{title}</CardTitle>
        <CardDescription className="text-base">{description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-5">
        {/* Custom Google Sign-In Button - only render if Google OAuth is enabled */}
        {googleEnabled && (
          <>
            <GoogleSignInButton 
              isLoading={isLoading} 
              onLoadingChange={setIsGoogleLoading}
              onError={(error) => setErrors({ general: error })}
            />

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <span className="w-full border-t" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">Or continue with email</span>
              </div>
            </div>
          </>
        )}

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-sm font-medium">Email</Label>
            <Input
              id="email"
              type="email"
              placeholder="user@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={isLoading || isGoogleLoading}
              aria-invalid={!!errors.email}
            />
            {errors.email && (
              <p className="text-sm text-destructive">{errors.email}</p>
            )}
          </div>

          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="password" className="text-sm font-medium">Password</Label>
              {isLogin && (
                <Link href="/forgot-password" className="text-sm text-primary hover:underline">
                  Forgot password?
                </Link>
              )}
            </div>
            <Input
              id="password"
              type="password"
              placeholder={isLogin ? "Enter password" : "Min 8 characters"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={isLoading || isGoogleLoading}
              aria-invalid={!!errors.password}
            />
            {errors.password && (
              <p className="text-sm text-destructive">{errors.password}</p>
            )}
          </div>

          {errors.general && (
            <div className="p-4 text-sm text-destructive bg-destructive/10 rounded-lg border border-destructive/20">
              {errors.general}
            </div>
          )}

          <Button type="submit" className="w-full" size="lg" disabled={isLoading || isGoogleLoading}>
            {isLoading ? "Loading..." : submitText}
          </Button>
        </form>
      </CardContent>

      <CardFooter className="flex flex-col gap-4">
        <p className="text-sm text-center text-muted-foreground">
          {switchText}{" "}
          <Link href={switchLink} className="font-medium text-primary hover:underline">
            {switchLinkText}
          </Link>
        </p>
      </CardFooter>
    </Card>
  );
}

export function AuthForm({ mode }: AuthFormProps) {
  const googleClientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "";

  // If no Google Client ID is configured, render without Google OAuth
  if (!googleClientId) {
    return <AuthFormContent mode={mode} googleEnabled={false} />;
  }

  return (
    <GoogleOAuthProvider clientId={googleClientId}>
      <AuthFormContent mode={mode} googleEnabled={true} />
    </GoogleOAuthProvider>
  );
}
