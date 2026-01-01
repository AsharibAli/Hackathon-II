/**
 * Sidebar component.
 * Neo-Editorial styled sidebar for conversation history.
 */
"use client";

import { PanelLeftClose, PanelLeft, Plus, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";
import { ConversationItem } from "@/components/chat/ConversationItem";
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
        "flex flex-col h-full bg-sidebar border-r border-sidebar-border transition-all duration-300 ease-out-expo",
        isCollapsed ? "w-0 overflow-hidden" : "w-72"
      )}
    >
      {/* Sidebar Header */}
      <div className="flex items-center justify-between p-3 border-b border-sidebar-border/50">
        <Button
          onClick={onNewChat}
          className="flex-1 justify-start gap-3 bg-primary/10 hover:bg-primary/15 text-primary border-0 shadow-none"
        >
          <Plus className="h-4 w-4" />
          <span className="font-medium">New Chat</span>
        </Button>
        <Button
          onClick={onToggleCollapse}
          variant="ghost"
          size="icon"
          className="text-sidebar-muted hover:text-sidebar-foreground hover:bg-sidebar-accent ml-2 rounded-lg"
        >
          <PanelLeftClose className="h-4 w-4" />
        </Button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto py-3 scrollbar-thin">
        {conversations.length === 0 ? (
          <div className="flex flex-col items-center justify-center px-4 py-12 text-center">
            <div className="h-12 w-12 rounded-full bg-sidebar-accent flex items-center justify-center mb-4">
              <MessageSquare className="h-6 w-6 text-sidebar-muted" />
            </div>
            <p className="text-sm text-sidebar-muted mb-1">No conversations yet</p>
            <p className="text-xs text-sidebar-muted/70">
              Start a new chat to begin
            </p>
          </div>
        ) : (
          <nav className="space-y-1 px-2">
            {conversations.map((conversation, index) => (
              <div
                key={conversation.id}
                className="animate-fade-up"
                style={{ animationDelay: `${index * 30}ms` }}
              >
                <ConversationItem
                  conversation={conversation}
                  isActive={conversation.id === activeConversationId}
                  onSelect={() => onSelectConversation(conversation.id)}
                  onRename={(title: string) =>
                    onRenameConversation(conversation.id, title)
                  }
                  onDelete={() => onDeleteConversation(conversation.id)}
                />
              </div>
            ))}
          </nav>
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-sidebar-border/50">
        <p className="text-xs text-sidebar-muted/60 text-center">
          {conversations.length} conversation{conversations.length !== 1 ? "s" : ""}
        </p>
      </div>
    </aside>
  );
}

// Sidebar Toggle Button for when sidebar is collapsed
export function SidebarToggle({ onClick }: { onClick: () => void }) {
  return (
    <Button
      onClick={onClick}
      variant="outline"
      size="icon"
      className="absolute left-4 top-4 z-40 h-10 w-10 rounded-xl bg-background/90 backdrop-blur-sm border-border/50 shadow-soft hover:shadow-elevated hover:bg-background transition-all duration-200"
    >
      <PanelLeft className="h-4 w-4" />
    </Button>
  );
}
