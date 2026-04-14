"use client";

import * as React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, User, Send, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { SourceDocument } from "@/lib/api";
import { SourceChips } from "./source-chips";

export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceDocument[];
  isStreaming?: boolean;
};

interface ChatInterfaceProps {
  messages: Message[];
  isLoading?: boolean;
  onSendMessage: (content: string) => void;
}

export function ChatInterface({
  messages,
  isLoading,
  onSendMessage,
}: ChatInterfaceProps) {
  const [inputValue, setInputValue] = React.useState("");
  const scrollRef = React.useRef<HTMLDivElement>(null);

  console.log({ isLoading });

  // Auto-scroll to bottom on new messages or content change
  React.useEffect(() => {
    if (scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector(
        "[data-radix-scroll-area-viewport]",
      );
      if (scrollContainer) {
        // Use requestAnimationFrame to ensure DOM is updated before scrolling
        requestAnimationFrame(() => {
          scrollContainer.scrollTo({
            top: scrollContainer.scrollHeight,
            behavior: "smooth",
          });
        });
      }
    }
  }, [messages, isLoading, messages[messages.length - 1]?.content]); // Added content dependency

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    onSendMessage(inputValue);
    setInputValue("");
  };

  return (
    <div className="flex flex-col h-full mx-auto w-full min-h-0">
      <div className="flex-1 min-h-0 relative">
        <ScrollArea ref={scrollRef} className="h-full w-full">
          <div className="space-y-6 pb-20">
            <AnimatePresence initial={false}>
              {messages.map((message) => (
                <motion.div
                  key={message.id}
                  initial={{ opacity: 0, y: 10, scale: 0.98 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  transition={{ duration: 0.3, ease: "easeOut" }}
                  className={cn(
                    "flex gap-4 p-4 rounded-2xl border transition-all duration-300",
                    message.role === "assistant"
                      ? "bg-white/[0.03] border-white/5 mr-8 md:mr-12 shadow-sm"
                      : "bg-primary/10 border-primary/20 ml-8 md:ml-12 flex-row-reverse",
                  )}>
                  <div
                    className={cn(
                      "flex size-8 shrink-0 items-center justify-center rounded-full border shadow-inner",
                      message.role === "assistant"
                        ? "bg-primary text-primary-foreground border-primary"
                        : "bg-muted border-white/10",
                    )}>
                    {message.role === "assistant" ? (
                      <Sparkles className="size-4" />
                    ) : (
                      <User className="size-4" />
                    )}
                  </div>
                  <div className="flex-1 space-y-2 overflow-hidden">
                    <div className="flex items-center justify-between">
                      <p className="text-xs font-bold uppercase tracking-widest text-muted-foreground/70">
                        {message.role === "assistant"
                          ? "YouTube AI Brain"
                          : "You"}
                      </p>
                      {message.isStreaming && (
                        <span className="flex gap-1">
                          <span className="size-1 bg-primary rounded-full animate-bounce [animation-delay:-0.3s]" />
                          <span className="size-1 bg-primary rounded-full animate-bounce [animation-delay:-0.15s]" />
                          <span className="size-1 bg-primary rounded-full animate-bounce" />
                        </span>
                      )}
                    </div>
                    <div className="text-base leading-relaxed text-zinc-200 whitespace-pre-wrap font-sans">
                      {message.content}
                      {message.role === "assistant" && message.isStreaming && (
                        <span className="inline-block w-2 h-4 ml-1 bg-primary animate-pulse align-middle" />
                      )}
                    </div>

                    {message.sources && (
                      <SourceChips sources={message.sources} />
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>

            {isLoading &&
              messages[messages.length - 1]?.role !== "assistant" && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex gap-4 p-4 rounded-2xl border bg-white/[0.03] border-white/5 mr-12">
                  <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground">
                    <Loader2 className="size-4 animate-spin" />
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="h-3 w-3/4 bg-white/5 animate-pulse rounded-full" />
                    <div className="h-3 w-1/2 bg-white/5 animate-pulse rounded-full" />
                  </div>
                </motion.div>
              )}
          </div>
        </ScrollArea>
      </div>

      <div className="p-4 bg-background/50 backdrop-blur-xl border-t border-white/5">
        <form
          onSubmit={handleSubmit}
          className="flex items-center gap-2 max-w-4xl mx-auto relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-primary to-purple-600 rounded-2xl blur opacity-0 group-focus-within:opacity-25 transition duration-500 pointer-events-none" />
          <input
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={isLoading}
            placeholder={
              isLoading
                ? "AI is thinking..."
                : "Ask anything about the video..."
            }
            className={cn(
              "flex-1 bg-zinc-900 border border-white/10 px-6 py-4 rounded-xl focus:outline-none focus:ring-1 focus:ring-primary text-white placeholder:text-zinc-600 shadow-2xl transition-all",
              isLoading && "opacity-50 cursor-not-allowed",
            )}
            autoFocus
          />
          <Button
            size="icon"
            disabled={!inputValue.trim() || isLoading}
            className="rounded-xl h-14 w-14 bg-white text-black hover:bg-zinc-200 shadow-xl transition-all active:scale-95">
            {isLoading ? (
              <Loader2 className="size-5 animate-spin" />
            ) : (
              <Send className="size-5" />
            )}
          </Button>
        </form>
        <p className="text-[10px] text-center text-muted-foreground mt-3 uppercase tracking-tighter">
          Analysis powered by Gemini 1.5 • Select model in header
        </p>
      </div>
    </div>
  );
}
