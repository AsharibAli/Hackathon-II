/**
 * AppHeader component.
 * Neo-Editorial styled header with logo, mode toggle, and user menu.
 */
"use client";

import { useRef, useState } from "react";
import Link from "next/link";
import { LogOut, User, Settings, Moon, Sun, ChevronDown, Home, Bell } from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { Button } from "@/components/ui/button";
import { ModeToggle, AppMode } from "./ModeToggle";
import { NotificationCenter } from "@/components/notifications";
import { UserProfile } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useTheme } from "next-themes";

interface AppHeaderProps {
  activeMode: AppMode;
  onModeChange: (mode: AppMode) => void;
  user: UserProfile | null;
  onLogout: () => void;
  onUpdateProfile?: (data: {
    full_name?: string;
    profile_picture?: string;
  }) => void;
}

export function AppHeader({
  activeMode,
  onModeChange,
  user,
  onLogout,
  onUpdateProfile,
}: AppHeaderProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [editName, setEditName] = useState(user?.full_name || "");
  const [editPicture, setEditPicture] = useState(user?.profile_picture || "");
  const { theme, setTheme } = useTheme();
  const notificationTriggerRef = useRef<HTMLButtonElement>(null);

  const handleSaveProfile = () => {
    if (onUpdateProfile) {
      onUpdateProfile({
        full_name: editName || undefined,
        profile_picture: editPicture || undefined,
      });
    }
    setIsProfileOpen(false);
  };

  const handleOpenProfile = () => {
    setEditName(user?.full_name || "");
    setEditPicture(user?.profile_picture || "");
    setIsProfileOpen(true);
  };

  const displayName =
    user?.full_name || user?.email?.split("@")[0] || "User";
  const initials = displayName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2);

  return (
    <>
      <header className="h-16 border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="container-wide relative h-full flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <Logo size="md" />
            <span className="font-display font-semibold text-lg tracking-tight hidden sm:inline">
              TaskAI
            </span>
          </div>

          {/* Mode Toggle - Centered */}
          <div className="absolute left-1/2 -translate-x-1/2">
            <ModeToggle activeMode={activeMode} onModeChange={onModeChange} />
          </div>

          {/* Right side - User menu & actions */}
          <div className="ml-auto flex items-center gap-2">
            {/* Header actions (desktop only) */}
            <div className="hidden items-center gap-2 sm:flex">
              <NotificationCenter />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                className="h-9 w-9 rounded-full text-muted-foreground hover:text-foreground"
              >
                <Sun className="h-4 w-4 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
                <Moon className="absolute h-4 w-4 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
                <span className="sr-only">Toggle theme</span>
              </Button>
            </div>

            {/* User dropdown menu */}
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="flex items-center gap-2 px-2 py-1.5 rounded-full hover:bg-muted transition-colors group">
                  {/* Avatar */}
                  {user?.profile_picture ? (
                    <img
                      src={user.profile_picture}
                      alt={displayName}
                      className="h-8 w-8 rounded-full object-cover ring-2 ring-background"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center ring-2 ring-background">
                      <span className="text-xs font-medium text-primary">
                        {initials}
                      </span>
                    </div>
                  )}
                  {/* Name - hidden on mobile */}
                  <span className="text-sm font-medium max-w-[100px] truncate hidden md:inline">
                    {displayName}
                  </span>
                  <ChevronDown className="h-4 w-4 text-muted-foreground group-hover:text-foreground transition-colors" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="w-56">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium">{displayName}</p>
                    <p className="text-xs text-muted-foreground truncate">
                      {user?.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link href="/home">
                    <Home className="mr-2 h-4 w-4" />
                    Home Page
                  </Link>
                </DropdownMenuItem>
                {onUpdateProfile && (
                  <DropdownMenuItem onClick={handleOpenProfile}>
                    <Settings className="mr-2 h-4 w-4" />
                    Profile Settings
                  </DropdownMenuItem>
                )}
                <div
                  className="flex flex-col gap-1 px-2 py-1 sm:hidden"
                  onClick={(e) => e.stopPropagation()}
                  onPointerDown={(e) => e.stopPropagation()}
                >
                  <NotificationCenter
                    className="absolute -left-[9999px] top-0 opacity-0 pointer-events-none"
                    triggerRef={notificationTriggerRef}
                  />
                  <div
                    className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-foreground hover:bg-muted cursor-pointer"
                    role="button"
                    tabIndex={0}
                    onClick={() => notificationTriggerRef.current?.click()}
                    onKeyDown={(e) => {
                      if (e.key === "Enter" || e.key === " ") {
                        e.preventDefault();
                        notificationTriggerRef.current?.click();
                      }
                    }}
                  >
                    <Bell className="h-4 w-4 text-muted-foreground" />
                    <span>Notifications</span>
                  </div>
                  <Button
                    variant="ghost"
                    onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
                    className="h-9 justify-start gap-2 px-2 text-sm text-foreground hover:bg-muted"
                  >
                    {theme === "dark" ? (
                      <Sun className="h-4 w-4" />
                    ) : (
                      <Moon className="h-4 w-4" />
                    )}
                    {theme === "dark"
                      ? "Switch to Light Mode"
                      : "Switch to Dark Mode"}
                  </Button>
                </div>
                <DropdownMenuItem
                  onClick={onLogout}
                  className="text-destructive focus:text-destructive focus:bg-destructive/10"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </header>

      {/* Profile Settings Dialog */}
      <Dialog open={isProfileOpen} onOpenChange={setIsProfileOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="font-display text-xl">
              Profile Settings
            </DialogTitle>
            <DialogDescription>
              Update your profile information and preferences.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Avatar preview */}
            <div className="flex justify-center">
              {editPicture ? (
                <img
                  src={editPicture}
                  alt="Preview"
                  className="h-20 w-20 rounded-full object-cover ring-4 ring-muted"
                  onError={(e) => {
                    (e.target as HTMLImageElement).style.display = "none";
                  }}
                />
              ) : (
                <div className="h-20 w-20 rounded-full bg-primary/10 flex items-center justify-center ring-4 ring-muted">
                  <User className="h-8 w-8 text-primary" />
                </div>
              )}
            </div>

            {/* Email (read-only) */}
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium">
                Email
              </Label>
              <Input
                id="email"
                value={user?.email || ""}
                disabled
                className="bg-muted/50"
              />
            </div>

            {/* Full Name */}
            <div className="space-y-2">
              <Label htmlFor="fullName" className="text-sm font-medium">
                Full Name
              </Label>
              <Input
                id="fullName"
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                placeholder="Enter your full name"
              />
            </div>

            {/* Profile Picture URL */}
            <div className="space-y-2">
              <Label htmlFor="profilePicture" className="text-sm font-medium">
                Profile Picture URL
              </Label>
              <Input
                id="profilePicture"
                value={editPicture}
                onChange={(e) => setEditPicture(e.target.value)}
                placeholder="https://example.com/avatar.jpg"
              />
              <p className="text-xs text-muted-foreground">
                Enter a URL to an image for your profile picture.
              </p>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <Button
              variant="outline"
              onClick={() => setIsProfileOpen(false)}
            >
              Cancel
            </Button>
            <Button onClick={handleSaveProfile}>Save Changes</Button>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
