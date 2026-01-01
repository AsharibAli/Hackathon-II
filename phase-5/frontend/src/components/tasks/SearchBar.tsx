/**
 * SearchBar component.
 * Neo-Editorial styled search input with debounced query handling.
 */
"use client";

import { useState, useEffect, useCallback } from "react";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, X, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface SearchBarProps {
  onSearch: (query: string) => void;
  isSearching?: boolean;
  placeholder?: string;
  className?: string;
  debounceMs?: number;
}

export function SearchBar({
  onSearch,
  isSearching = false,
  placeholder = "Search tasks...",
  className,
  debounceMs = 300,
}: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [debouncedQuery, setDebouncedQuery] = useState("");

  // Debounce the search query
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedQuery(query);
    }, debounceMs);

    return () => clearTimeout(timer);
  }, [query, debounceMs]);

  // Trigger search when debounced query changes
  useEffect(() => {
    onSearch(debouncedQuery);
  }, [debouncedQuery, onSearch]);

  const handleClear = useCallback(() => {
    setQuery("");
    setDebouncedQuery("");
    onSearch("");
  }, [onSearch]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setDebouncedQuery(query);
    onSearch(query);
  };

  return (
    <form onSubmit={handleSubmit} className={cn("relative", className)}>
      <div className="relative group">
        {/* Search icon or loading spinner */}
        <div className="absolute left-4 top-1/2 -translate-y-1/2 z-10">
          {isSearching ? (
            <Loader2 className="h-4 w-4 text-primary animate-spin" />
          ) : (
            <Search className="h-4 w-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
          )}
        </div>

        {/* Search input */}
        <Input
          type="text"
          placeholder={placeholder}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className={cn(
            "h-12 pl-11 pr-11 rounded-xl",
            "bg-background/80 border-border/60",
            "placeholder:text-muted-foreground/60",
            "focus-visible:ring-2 focus-visible:ring-primary/30 focus-visible:border-primary/50",
            "transition-all duration-200",
            query && "border-primary/30"
          )}
        />

        {/* Clear button */}
        {query && (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className={cn(
              "absolute right-2 top-1/2 -translate-y-1/2",
              "h-8 w-8 rounded-lg",
              "text-muted-foreground hover:text-foreground",
              "opacity-0 group-hover:opacity-100 focus:opacity-100",
              "transition-opacity duration-200"
            )}
            onClick={handleClear}
            title="Clear search"
          >
            <X className="h-4 w-4" />
          </Button>
        )}
      </div>

      {/* Search hint */}
      {query && !isSearching && (
        <p className="absolute -bottom-5 left-4 text-xs text-muted-foreground/60">
          Press{" "}
          <kbd className="px-1 py-0.5 rounded bg-muted text-muted-foreground font-mono text-[10px]">
            Enter
          </kbd>{" "}
          to search
        </p>
      )}
    </form>
  );
}
