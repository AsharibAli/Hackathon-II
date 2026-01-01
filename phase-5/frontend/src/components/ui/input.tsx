/**
 * Input component.
 * Neo-Editorial styled form input.
 */
import * as React from "react";
import { cn } from "@/lib/utils";

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          "flex h-11 w-full rounded-xl border border-border/60 bg-background px-4 py-2 text-sm",
          "shadow-sm transition-all duration-200",
          "placeholder:text-muted-foreground/60",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary/50",
          "disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-muted/30",
          "file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground",
          "hover:border-border",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export { Input };
