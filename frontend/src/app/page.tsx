"use client";

import * as React from "react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Separator } from "@/components/ui/separator";
import {
  Search,
  Send,
  Clock,
  Sparkles,
  Loader2,
  Library,
  Play,
  Zap,
  BrainCircuit,
} from "lucide-react";
import { ChatInterface, Message } from "@/components/chat-interface";
import {
  processUrl,
  streamChatWithVideo,
  ProcessUrlResponse,
  getSessionMessages,
  VideoSession,
} from "@/lib/api";
import { motion, AnimatePresence } from "framer-motion";

export default function Page() {
  const [url, setUrl] = React.useState("");
  const [status, setStatus] = React.useState<
    "landing" | "processing" | "chatting"
  >("landing");
  const [videoInfo, setVideoInfo] = React.useState<ProcessUrlResponse | null>(
    null,
  );
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [isLoadingChat, setIsLoadingChat] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [selectedModel, setSelectedModel] = React.useState<
    "llama-3.1-8b-instant" | "llama-3.3-70b-versatile"
  >("llama-3.1-8b-instant");

  const handleProcessUrl = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!url.trim()) return;

    setStatus("processing");
    setError(null);

    try {
      const data = await processUrl(url);
      setVideoInfo(data);
      setStatus("chatting");
      setMessages([
        {
          id: "1",
          role: "assistant",
          content: `Hello! I've successfully indexed the video: **${data.title}**. Ask me anything about it!`,
        },
      ]);
    } catch (err: any) {
      setError(err.message);
      setStatus("landing");
    }
  };

  const handleSendMessage = async (content: string) => {
    if (!videoInfo) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content,
    };

    const aiMessageId = (Date.now() + 1).toString();
    const initialAiMessage: Message = {
      id: aiMessageId,
      role: "assistant",
      content: "",
      isStreaming: true,
    };

    setMessages((prev) => [...prev, userMessage, initialAiMessage]);
    setIsLoadingChat(true);

    try {
      const stream = streamChatWithVideo(
        videoInfo.video_id,
        content,
        selectedModel,
      );

      for await (const chunk of stream) {
        if (chunk.type === "sources") {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId ? { ...msg, sources: chunk.data } : msg,
            ),
          );
        } else if (chunk.type === "chunk") {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === aiMessageId
                ? { ...msg, content: msg.content + chunk.data }
                : msg,
            ),
          );
        } else if (chunk.type === "error") {
          setError(chunk.data);
        }
      }

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === aiMessageId ? { ...msg, isStreaming: false } : msg,
        ),
      );
    } catch (err: any) {
      setError("Failed to get response. Please try again.");
    } finally {
      setIsLoadingChat(false);
    }
  };

  const handleSelectSession = async (session: VideoSession) => {
    setStatus("processing");
    setError(null);
    try {
      const history = await getSessionMessages(session.video_id);
      setVideoInfo({
        video_id: session.video_id,
        title: session.custom_name || session.youtube_title,
        author: session.author || "YouTube Content",
        thumbnail_url: session.thumbnail_url,
        already_indexed: true,
        message: "Loaded from history",
      });

      const mappedMessages: Message[] = history.map((m) => ({
        id: m.id.toString(),
        role: m.role,
        content: m.content,
        sources: m.sources,
      }));

      setMessages(mappedMessages);
      setStatus("chatting");
    } catch (err) {
      setError("Failed to load session history");
      setStatus("landing");
    }
  };

  const handleNewChat = () => {
    setStatus("landing");
    setVideoInfo(null);
    setMessages([]);
    setUrl("");
  };

  return (
    <SidebarProvider>
      <AppSidebar
        onSelectSession={handleSelectSession}
        onNewChat={handleNewChat}
      />
      <SidebarInset className="flex flex-col h-screen overflow-hidden bg-black">
        {/* Header */}
        <header className="sticky top-0 z-30 flex h-16 shrink-0 items-center justify-between gap-2 border-b border-white/5 bg-black/60 px-4 backdrop-blur-xl">
          <div className="flex items-center gap-2">
            <SidebarTrigger className="-ml-1" />
            <Separator orientation="vertical" className="mr-2 h-4" />
            <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/5">
              <Sparkles className="size-4 text-primary animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-widest text-zinc-400">
                {status === "chatting" ? "ACTIVE ANALYSIS" : "NEW SESSION"}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {/* Model Selector */}
            <div className="flex bg-zinc-900/50 p-1 rounded-lg border border-white/5">
              <button
                onClick={() => setSelectedModel("llama-3.1-8b-instant")}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-md text-[10px] font-black transition-all",
                  selectedModel === "llama-3.1-8b-instant"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "text-muted-foreground hover:text-white",
                )}>
                <Zap className="size-3" /> FAST
              </button>
              <button
                onClick={() => setSelectedModel("llama-3.3-70b-versatile")}
                className={cn(
                  "flex items-center gap-2 px-3 py-1.5 rounded-md text-[10px] font-black transition-all",
                  selectedModel === "llama-3.3-70b-versatile"
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "text-muted-foreground hover:text-white",
                )}>
                <BrainCircuit className="size-3" /> PRO
              </button>
            </div>

            <AnimatePresence>
              {videoInfo && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="hidden lg:flex items-center gap-3 bg-white/[0.03] border border-white/5 py-1 pl-1 pr-3 rounded-full">
                  <div className="size-6 rounded-full bg-primary/20 flex items-center justify-center">
                    <Play className="size-3 text-primary" />
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-tight truncate max-w-[150px] text-zinc-400">
                    {videoInfo.title}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </header>

        {/* Dynamic Content area */}
        <div className="flex-1 flex flex-col min-h-0 overflow-hidden relative">
          <AnimatePresence mode="wait">
            {status === "landing" && (
              <motion.main
                key="landing"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.02 }}
                className="h-full flex flex-col items-center justify-center p-4 md:p-8 space-y-12 relative">
                <div className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-primary/10 blur-[120px] rounded-full z-0 pointer-events-none" />

                <div className="z-10 w-full max-w-3xl space-y-6 text-center">
                  <motion.div
                    initial={{ y: 20, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ delay: 0.2 }}>
                    <h2 className="text-6xl md:text-7xl font-black tracking-tighter bg-gradient-to-b from-white via-white to-zinc-600 bg-clip-text text-transparent leading-[0.9]">
                      CHAT WITH <br /> THE INTERNET.
                    </h2>
                  </motion.div>
                  <p className="text-zinc-500 text-xl max-w-lg mx-auto font-medium">
                    Instant AI intelligence for any YouTube video. No watching
                    required.
                  </p>
                </div>

                <form
                  onSubmit={handleProcessUrl}
                  className="z-10 w-full max-w-2xl relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-primary/50 to-purple-600/50 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-1000 group-hover:duration-200" />
                  <div className="relative flex items-center gap-2 bg-zinc-950 p-2 rounded-2xl border border-white/10 shadow-3xl">
                    <div className="flex-1 flex items-center px-4 gap-4">
                      <Search className="size-6 text-zinc-600" />
                      <input
                        type="text"
                        value={url}
                        onChange={(e) => setUrl(e.target.value)}
                        placeholder="Paste YouTube link here..."
                        className="flex-1 bg-transparent border-none focus:ring-0 outline-none text-white placeholder:text-zinc-700 text-xl py-4 font-medium"
                      />
                    </div>
                    <button
                      type="submit"
                      disabled={!url.trim()}
                      className="bg-white text-black px-8 py-4 rounded-xl font-bold hover:bg-zinc-200 transition-all flex items-center gap-2 group-active:scale-95 disabled:opacity-50">
                      START <Send className="size-5" />
                    </button>
                  </div>
                  {error && (
                    <p className="mt-4 text-destructive text-sm font-bold text-center tracking-wide uppercase">
                      {error}
                    </p>
                  )}
                </form>

                <div className="z-10 grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-3xl mt-16">
                  {[
                    {
                      icon: Sparkles,
                      text: "PRO REASONING",
                      sub: "Deep video analysis",
                    },
                    {
                      icon: Library,
                      text: "INSTANT KNOWLEDGE",
                      sub: "Skip the 20min intro",
                    },
                    {
                      icon: Clock,
                      text: "TIMESTAMPS",
                      sub: "Direct citations",
                    },
                  ].map((feature, i) => (
                    <div
                      key={i}
                      className="flex flex-col items-center gap-2 p-6 rounded-2xl border border-white/5 bg-white/[0.01] hover:bg-white/[0.03] transition-all cursor-default group">
                      <feature.icon className="size-6 text-primary/60 group-hover:text-primary transition-colors" />
                      <span className="text-xs font-black text-zinc-400 tracking-widest">
                        {feature.text}
                      </span>
                      <span className="text-[10px] text-zinc-600 font-bold">
                        {feature.sub}
                      </span>
                    </div>
                  ))}
                </div>
              </motion.main>
            )}

            {status === "processing" && (
              <motion.div
                key="processing"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="h-full flex flex-col items-center justify-center space-y-8">
                <div className="relative size-32">
                  <div className="absolute inset-0 bg-primary/30 blur-3xl rounded-full animate-pulse" />
                  <div className="relative size-32 rounded-full border-t-4 border-primary animate-spin" />
                  <div className="absolute inset-4 rounded-full border-b-4 border-purple-500 animate-spin-reverse" />
                  <Play className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 size-12 text-primary drop-shadow-[0_0_15px_rgba(255,255,255,0.5)]" />
                </div>
                <div className="text-center space-y-3">
                  <h3 className="text-3xl font-black tracking-tighter uppercase">
                    Building Context...
                  </h3>
                  <div className="flex items-center gap-2 justify-center">
                    <span className="text-zinc-500 font-bold text-sm tracking-widest animate-pulse">
                      ANALYZING TRANSCRIPT
                    </span>
                    <span className="size-1 bg-zinc-700 rounded-full" />
                    <span className="text-zinc-500 font-bold text-sm tracking-widest animate-pulse [animation-delay:0.2s]">
                      INDEXING VECTORS
                    </span>
                  </div>
                </div>
              </motion.div>
            )}

            {status === "chatting" && (
              <motion.div
                key="chatting"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex-1 flex flex-col min-h-0 h-full"
              >
                <ChatInterface
                  messages={messages}
                  isLoading={isLoadingChat}
                  onSendMessage={handleSendMessage}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
