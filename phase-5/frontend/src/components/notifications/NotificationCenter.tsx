/**
 * NotificationCenter component.
 * Neo-Editorial styled notification bell with dropdown and reminder notifications.
 */
"use client";

import { useState, useEffect, useCallback, type Ref } from "react";
import { Bell, BellRing, Check, Clock, Calendar, X, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { ScrollArea } from "@/components/ui/scroll-area";
import { tasksApi } from "@/lib/api";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
import { format, isPast, parseISO, formatDistanceToNow } from "date-fns";

interface Notification {
  id: string;
  taskId: string;
  title: string;
  message: string;
  time: Date;
  read: boolean;
  type: "reminder" | "overdue" | "due_soon";
}

interface NotificationCenterProps {
  className?: string;
  triggerRef?: Ref<HTMLButtonElement>;
}

export function NotificationCenter({
  className,
  triggerRef,
}: NotificationCenterProps) {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  // Check for tasks with upcoming reminders and overdue tasks
  const checkForNotifications = useCallback(async () => {
    try {
      // Get tasks with reminders that are due
      const allTasks = await tasksApi.getAll();
      const newNotifications: Notification[] = [];
      const now = new Date();

      allTasks.forEach((task) => {
        // Check for reminder notifications
        if (task.remind_at && !task.reminder_sent && !task.is_completed) {
          const reminderTime = parseISO(task.remind_at);
          const timeDiff = reminderTime.getTime() - now.getTime();

          // If reminder is within the next 5 minutes or has passed (but not too old)
          if (timeDiff <= 5 * 60 * 1000 && timeDiff > -30 * 60 * 1000) {
            const exists = notifications.find(
              (n) => n.taskId === task.id && n.type === "reminder"
            );
            if (!exists) {
              newNotifications.push({
                id: `reminder-${task.id}-${Date.now()}`,
                taskId: task.id,
                title: "Reminder",
                message: task.title,
                time: reminderTime,
                read: false,
                type: "reminder",
              });
            }
          }
        }

        // Check for overdue tasks
        if (task.due_date && !task.is_completed) {
          const dueDate = parseISO(task.due_date);
          if (isPast(dueDate)) {
            const existingOverdue = notifications.find(
              (n) => n.taskId === task.id && n.type === "overdue"
            );
            if (!existingOverdue) {
              newNotifications.push({
                id: `overdue-${task.id}-${Date.now()}`,
                taskId: task.id,
                title: "Overdue Task",
                message: task.title,
                time: dueDate,
                read: false,
                type: "overdue",
              });
            }
          } else {
            // Check for tasks due within the next hour
            const timeToDue = dueDate.getTime() - now.getTime();
            if (timeToDue <= 60 * 60 * 1000 && timeToDue > 0) {
              const existingDueSoon = notifications.find(
                (n) => n.taskId === task.id && n.type === "due_soon"
              );
              if (!existingDueSoon) {
                newNotifications.push({
                  id: `due-soon-${task.id}-${Date.now()}`,
                  taskId: task.id,
                  title: "Task Due Soon",
                  message: task.title,
                  time: dueDate,
                  read: false,
                  type: "due_soon",
                });
              }
            }
          }
        }
      });

      // Show toast for new notifications
      if (newNotifications.length > 0) {
        newNotifications.forEach((notification) => {
          toast(notification.title, {
            description: notification.message,
            icon:
              notification.type === "reminder" ? (
                <BellRing className="h-4 w-4 text-primary" />
              ) : notification.type === "overdue" ? (
                <Clock className="h-4 w-4 text-destructive" />
              ) : (
                <Calendar className="h-4 w-4 text-amber-500" />
              ),
            duration: 8000,
          });
        });

        setNotifications((prev) => [...newNotifications, ...prev].slice(0, 50));
      }

      setLastCheck(new Date());
    } catch (error) {
      console.error("Failed to check notifications:", error);
    }
  }, [notifications]);

  // Poll for notifications every 30 seconds
  useEffect(() => {
    checkForNotifications();
    const interval = setInterval(checkForNotifications, 30000);
    return () => clearInterval(interval);
  }, [checkForNotifications]);

  const unreadCount = notifications.filter((n) => !n.read).length;

  const markAsRead = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const markAllAsRead = () => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  const removeNotification = (id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  };

  const clearAll = () => {
    setNotifications([]);
  };

  const getNotificationIcon = (type: Notification["type"]) => {
    switch (type) {
      case "reminder":
        return <BellRing className="h-4 w-4 text-primary" />;
      case "overdue":
        return <Clock className="h-4 w-4 text-destructive" />;
      case "due_soon":
        return <Calendar className="h-4 w-4 text-amber-500" />;
    }
  };

  const getNotificationColor = (type: Notification["type"]) => {
    switch (type) {
      case "reminder":
        return "bg-primary/10 border-primary/20";
      case "overdue":
        return "bg-destructive/10 border-destructive/20";
      case "due_soon":
        return "bg-amber-500/10 border-amber-500/20";
    }
  };

  return (
    <DropdownMenu open={isOpen} onOpenChange={setIsOpen}>
      <DropdownMenuTrigger asChild>
        <Button
          ref={triggerRef}
          variant="ghost"
          size="icon"
          className={cn(
            "relative h-9 w-9 rounded-full text-muted-foreground hover:text-foreground",
            className
          )}
        >
          {unreadCount > 0 ? (
            <BellRing className="h-4 w-4 animate-bounce-subtle" />
          ) : (
            <Bell className="h-4 w-4" />
          )}
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-destructive text-destructive-foreground text-[10px] font-bold flex items-center justify-center animate-pulse">
              {unreadCount > 9 ? "9+" : unreadCount}
            </span>
          )}
          <span className="sr-only">Notifications</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent
        align="end"
        className="w-80 p-0 rounded-xl overflow-hidden"
      >
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border/50 bg-muted/30">
          <div>
            <h3 className="font-display font-semibold text-sm">Notifications</h3>
            <p className="text-xs text-muted-foreground">
              {unreadCount > 0
                ? `${unreadCount} unread`
                : "You're all caught up"}
            </p>
          </div>
          {notifications.length > 0 && (
            <div className="flex gap-1">
              {unreadCount > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={markAllAsRead}
                  className="h-7 px-2 text-xs"
                >
                  <Check className="h-3 w-3 mr-1" />
                  Mark all
                </Button>
              )}
              <Button
                variant="ghost"
                size="sm"
                onClick={clearAll}
                className="h-7 px-2 text-xs text-muted-foreground hover:text-destructive"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
          )}
        </div>

        {/* Notifications list */}
        {notifications.length === 0 ? (
          <div className="px-4 py-8 text-center">
            <div className="mx-auto h-12 w-12 rounded-full bg-muted/50 flex items-center justify-center mb-3">
              <Bell className="h-6 w-6 text-muted-foreground/50" />
            </div>
            <p className="text-sm font-medium text-muted-foreground">
              No notifications yet
            </p>
            <p className="text-xs text-muted-foreground/70 mt-1">
              Task reminders will appear here
            </p>
          </div>
        ) : (
          <ScrollArea className="max-h-[400px]">
            <div className="divide-y divide-border/30">
              {notifications.map((notification) => (
                <div
                  key={notification.id}
                  className={cn(
                    "flex items-start gap-3 p-4 transition-colors hover:bg-muted/30",
                    !notification.read && "bg-muted/20"
                  )}
                  onClick={() => markAsRead(notification.id)}
                >
                  {/* Icon */}
                  <div
                    className={cn(
                      "h-9 w-9 rounded-lg flex items-center justify-center flex-shrink-0 border",
                      getNotificationColor(notification.type)
                    )}
                  >
                    {getNotificationIcon(notification.type)}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <p
                          className={cn(
                            "text-sm font-medium",
                            !notification.read && "text-foreground",
                            notification.read && "text-muted-foreground"
                          )}
                        >
                          {notification.title}
                        </p>
                        <p className="text-sm text-muted-foreground truncate">
                          {notification.message}
                        </p>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          removeNotification(notification.id);
                        }}
                        className="p-1 rounded hover:bg-muted transition-colors text-muted-foreground hover:text-foreground flex-shrink-0"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </div>
                    <p className="text-xs text-muted-foreground/70 mt-1">
                      {formatDistanceToNow(notification.time, {
                        addSuffix: true,
                      })}
                    </p>
                  </div>

                  {/* Unread indicator */}
                  {!notification.read && (
                    <div className="h-2 w-2 rounded-full bg-primary flex-shrink-0 mt-2" />
                  )}
                </div>
              ))}
            </div>
          </ScrollArea>
        )}

        {/* Footer */}
        <div className="px-4 py-2 border-t border-border/30 bg-muted/20">
          <p className="text-[10px] text-muted-foreground/60 text-center">
            Last checked: {format(lastCheck, "h:mm a")}
          </p>
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
