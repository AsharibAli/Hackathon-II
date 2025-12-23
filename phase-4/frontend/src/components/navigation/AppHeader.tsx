/**
 * AppHeader component.
 * Header with logo, navigation mode toggle, and user menu.
 */
"use client";

import { useState } from "react";
import { LogOut, User } from "lucide-react";
import { Logo } from "@/components/ui/Logo";
import { Button } from "@/components/ui/button";
import { ModeToggle, AppMode } from "./ModeToggle";
import { UserProfile } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

interface AppHeaderProps {
  activeMode: AppMode;
  onModeChange: (mode: AppMode) => void;
  user: UserProfile | null;
  onLogout: () => void;
  onUpdateProfile?: (data: { full_name?: string; profile_picture?: string }) => void;
}

export function AppHeader({ activeMode, onModeChange, user, onLogout, onUpdateProfile }: AppHeaderProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [editName, setEditName] = useState(user?.full_name || "");
  const [editPicture, setEditPicture] = useState(user?.profile_picture || "");

  const handleSaveProfile = () => {
    if (onUpdateProfile) {
      onUpdateProfile({
        full_name: editName || undefined,
        profile_picture: editPicture || undefined,
      });
    }
    setIsProfileOpen(false);
  };

  const displayName = user?.full_name || user?.email?.split("@")[0] || "User";

  return (
    <header className="h-14 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
      <div className="container mx-auto h-full flex items-center justify-between px-4">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <Logo size="md" />
          <span className="font-semibold text-lg hidden sm:inline">TaskAI</span>
        </div>

        {/* Mode Toggle - Centered */}
        <ModeToggle activeMode={activeMode} onModeChange={onModeChange} />

        {/* User Info & Actions */}
        <div className="flex items-center gap-2">
          {/* Profile Settings Dialog - Clickable Profile Area */}
          {onUpdateProfile ? (
            <Dialog open={isProfileOpen} onOpenChange={setIsProfileOpen}>
              <DialogTrigger asChild>
                <button
                  className="hidden sm:flex items-center gap-2 px-2 py-1.5 rounded-lg hover:bg-accent transition-colors cursor-pointer"
                  onClick={() => {
                    setEditName(user?.full_name || "");
                    setEditPicture(user?.profile_picture || "");
                  }}
                >
                  {user?.profile_picture ? (
                    <img
                      src={user.profile_picture}
                      alt={displayName}
                      className="h-8 w-8 rounded-full object-cover"
                    />
                  ) : (
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                      <User className="h-4 w-4 text-primary" />
                    </div>
                  )}
                  <span className="text-sm text-muted-foreground max-w-[120px] truncate">
                    {displayName}
                  </span>
                </button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Profile Settings</DialogTitle>
                  <DialogDescription>
                    Update your profile information.
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label htmlFor="email">Email</Label>
                    <Input
                      id="email"
                      value={user?.email || ""}
                      disabled
                      className="bg-muted"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      placeholder="Enter your full name"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label htmlFor="profilePicture">Profile Picture URL</Label>
                    <Input
                      id="profilePicture"
                      value={editPicture}
                      onChange={(e) => setEditPicture(e.target.value)}
                      placeholder="https://example.com/avatar.jpg"
                    />
                  </div>
                </div>
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsProfileOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleSaveProfile}>
                    Save Changes
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          ) : (
            <div className="hidden sm:flex items-center gap-2">
              {user?.profile_picture ? (
                <img
                  src={user.profile_picture}
                  alt={displayName}
                  className="h-8 w-8 rounded-full object-cover"
                />
              ) : (
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <User className="h-4 w-4 text-primary" />
                </div>
              )}
              <span className="text-sm text-muted-foreground max-w-[120px] truncate">
                {displayName}
              </span>
            </div>
          )}

          {/* Logout Button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={onLogout}
            className="text-muted-foreground hover:text-destructive"
          >
            <LogOut className="h-4 w-4" />
            <span className="hidden sm:inline ml-2">Logout</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
