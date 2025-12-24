/**
 * Reusable authentication form component.
 * Handles both login and registration with validation and Google OAuth.
 */
"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { GoogleOAuthProvider, GoogleLogin, CredentialResponse } from "@react-oauth/google";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { authApi, ApiError } from "@/lib/api";
import { toast } from "sonner";

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

  // Handle Google OAuth success using the credential (JWT) response
  const handleGoogleSuccess = async (credentialResponse: CredentialResponse) => {
    if (!credentialResponse.credential) {
      setErrors({ general: "Failed to get Google credentials" });
      toast.error("Failed to get Google credentials");
      return;
    }

    setIsGoogleLoading(true);
    setErrors({});

    try {
      // Decode the JWT credential to get user info
      // The credential is a JWT token that contains user information
      const base64Url: any = credentialResponse.credential.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split('')
          .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
          .join('')
      );
      const userInfo = JSON.parse(jsonPayload);

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
    <Card className="w-full max-w-md mx-auto">
      <CardHeader className="space-y-2 text-center">
        <CardTitle className="text-2xl font-bold">{title}</CardTitle>
        <CardDescription className="text-base">{description}</CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-5">
        {/* Google Sign-In Button - only render if Google OAuth is enabled */}
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
