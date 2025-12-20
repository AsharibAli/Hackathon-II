"use client";

import { useState } from "react";
import { PanelLeftClose, PanelLeft, Plus, LogOut, Settings } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConversationItem } from "@/components/chat/ConversationItem";
import { ConversationSummary } from "@/types/chat";
import { UserProfile } from "@/lib/api";
import { cn } from "@/lib/utils";
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

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  onDeleteConversation: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
  user: UserProfile | null;
  onLogout: () => void;
  onUpdateProfile: (data: { full_name?: string; profile_picture?: string }) => void;
}

export function Sidebar({
  conversations,
  activeConversationId,
  onNewChat,
  onSelectConversation,
  onRenameConversation,
  onDeleteConversation,
  isCollapsed,
  onToggleCollapse,
  user,
  onLogout,
  onUpdateProfile,
}: SidebarProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const [editName, setEditName] = useState(user?.full_name || "");
  const [editPicture, setEditPicture] = useState(user?.profile_picture || "");

  const handleSaveProfile = () => {
    onUpdateProfile({
      full_name: editName || undefined,
      profile_picture: editPicture || undefined,
    });
    setIsProfileOpen(false);
  };

  const displayName = user?.full_name || user?.email?.split("@")[0] || "User";
  const avatarLetter = displayName.charAt(0).toUpperCase();

  return (
    <aside
      className={cn(
        "flex flex-col h-full bg-sidebar transition-all duration-300 ease-in-out",
        isCollapsed ? "w-0 overflow-hidden" : "w-[280px]"
      )}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-3 border-b border-sidebar-border">
        <Button
          onClick={onNewChat}
          variant="ghost"
          className="flex-1 justify-start gap-3 text-sidebar-foreground hover:bg-sidebar-accent"
        >
          <Plus className="h-4 w-4" />
          <span className="font-medium">New chat</span>
        </Button>
        <Button
          onClick={onToggleCollapse}
          variant="ghost"
          size="icon"
          className="text-sidebar-foreground hover:bg-sidebar-accent ml-2"
        >
          <PanelLeftClose className="h-4 w-4" />
        </Button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto py-2 scrollbar-thin">
        {conversations.length === 0 ? (
          <div className="px-4 py-8 text-center text-sidebar-muted text-sm">
            No conversations yet.
            <br />
            Start a new chat!
          </div>
        ) : (
          <nav className="space-y-1 px-2">
            {conversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isActive={conversation.id === activeConversationId}
                onSelect={() => onSelectConversation(conversation.id)}
                onRename={(title: string) => onRenameConversation(conversation.id, title)}
                onDelete={() => onDeleteConversation(conversation.id)}
              />
            ))}
          </nav>
        )}
      </div>

      {/* User Section */}
      <div className="p-3 border-t border-sidebar-border">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1 min-w-0">
            {/* User Avatar */}
            {user?.profile_picture ? (
              <img
                src={user.profile_picture}
                alt={displayName}
                className="h-8 w-8 rounded-full object-cover flex-shrink-0"
              />
            ) : (
              <div className="h-8 w-8 rounded-full bg-sidebar-accent flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-medium text-sidebar-foreground">{avatarLetter}</span>
              </div>
            )}
            
            {/* User Info */}
            <div className="flex flex-col min-w-0">
              <span className="text-sm font-medium text-sidebar-foreground truncate">
                {displayName}
              </span>
              {user?.email && (
                <span className="text-xs text-sidebar-muted truncate">
                  {user.email}
                </span>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-1 flex-shrink-0">
            {/* Profile Settings Dialog */}
            <Dialog open={isProfileOpen} onOpenChange={setIsProfileOpen}>
              <DialogTrigger asChild>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-8 w-8 text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent"
                  onClick={() => {
                    setEditName(user?.full_name || "");
                    setEditPicture(user?.profile_picture || "");
                  }}
                >
                  <Settings className="h-4 w-4" />
                </Button>
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

            {/* Logout Button */}
            <Button
              variant="ghost"
              size="icon"
              className="h-8 w-8 text-sidebar-muted hover:text-destructive hover:bg-sidebar-accent"
              onClick={onLogout}
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </aside>
  );
}

// Sidebar Toggle Button for when sidebar is collapsed
export function SidebarToggle({ onClick }: { onClick: () => void }) {
  return (
    <Button
      onClick={onClick}
      variant="ghost"
      size="icon"
      className="fixed left-4 top-4 z-50 bg-background/80 backdrop-blur-sm border shadow-sm hover:bg-accent"
    >
      <PanelLeft className="h-4 w-4" />
    </Button>
  );
}
