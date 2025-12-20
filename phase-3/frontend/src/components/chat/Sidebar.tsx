"use client";


import { PanelLeftClose, PanelLeft, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConversationItem } from "./ConversationItem";
import { ConversationSummary } from "@/types/chat";
import { cn } from "@/lib/utils";

interface SidebarProps {
  conversations: ConversationSummary[];
  activeConversationId: string | null;
  onNewChat: () => void;
  onSelectConversation: (id: string) => void;
  onRenameConversation: (id: string, title: string) => void;
  onDeleteConversation: (id: string) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
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
}: SidebarProps) {
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
                onRename={(title) => onRenameConversation(conversation.id, title)}
                onDelete={() => onDeleteConversation(conversation.id)}
              />
            ))}
          </nav>
        )}
      </div>

      {/* User Section */}
      <div className="p-3 border-t border-sidebar-border">
        <div className="flex items-center gap-3 text-sidebar-foreground text-sm">
          <div className="h-8 w-8 rounded-full bg-sidebar-accent flex items-center justify-center">
            <span className="text-xs font-medium">U</span>
          </div>
          <span className="font-medium">User</span>
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
