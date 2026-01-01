/**
 * Button component.
 * Neo-Editorial styled button with multiple variants.
 */
import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:ring-offset-2 focus-visible:ring-offset-background disabled:pointer-events-none disabled:opacity-50 [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default:
          "bg-primary text-primary-foreground shadow-soft hover:bg-primary/90 hover:shadow-elevated active:scale-[0.98] rounded-xl",
        destructive:
          "bg-destructive text-destructive-foreground shadow-soft hover:bg-destructive/90 hover:shadow-elevated rounded-xl",
        outline:
          "border border-border/60 bg-background hover:bg-muted hover:border-border hover:text-foreground rounded-xl",
        secondary:
          "bg-secondary text-secondary-foreground shadow-sm hover:bg-secondary/80 rounded-xl",
        ghost:
          "hover:bg-muted hover:text-foreground rounded-lg",
        link:
          "text-primary underline-offset-4 hover:underline",
        accent:
          "bg-accent text-accent-foreground shadow-soft hover:bg-accent/90 hover:shadow-elevated rounded-xl",
        success:
          "bg-emerald-600 text-white shadow-soft hover:bg-emerald-700 hover:shadow-elevated dark:bg-emerald-500 dark:hover:bg-emerald-600 rounded-xl",
      },
      size: {
        default: "h-11 px-5 py-2",
        sm: "h-9 px-4 text-xs rounded-lg",
        lg: "h-12 px-8 text-base rounded-xl",
        xl: "h-14 px-10 text-base rounded-xl",
        icon: "h-10 w-10 rounded-lg",
        "icon-sm": "h-8 w-8 rounded-lg",
        "icon-lg": "h-12 w-12 rounded-xl",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

export { Button, buttonVariants };
