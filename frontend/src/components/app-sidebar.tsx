"use client";

import * as React from "react";
import {
  History,
  LayoutDashboard,
  Settings,
  Play,
  Plus,
  MoreHorizontal,
  Pencil,
  Trash2,
  ExternalLink,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuAction,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { getHistory, deleteSession, renameSession, VideoSession } from "@/lib/api";

interface AppSidebarProps extends React.ComponentProps<typeof Sidebar> {
  onSelectSession?: (session: VideoSession) => void;
  onNewChat?: () => void;
}

export function AppSidebar({ onSelectSession, onNewChat, ...props }: AppSidebarProps) {
  const [history, setHistory] = React.useState<VideoSession[]>([]);
  const [editingSession, setEditingSession] = React.useState<VideoSession | null>(null);
  const [newName, setNewName] = React.useState("");
  const [isLoading, setIsLoading] = React.useState(true);

  const loadHistory = async () => {
    try {
      setIsLoading(true);
      const data = await getHistory();
      setHistory(data);
    } catch (error) {
      console.error("Failed to load history:", error);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    loadHistory();
  }, []);

  const handleDelete = async (videoId: string) => {
    if (confirm("Are you sure you want to delete this session and its index?")) {
      try {
        await deleteSession(videoId);
        setHistory((prev) => prev.filter((s) => s.video_id !== videoId));
      } catch (error) {
        alert("Failed to delete session");
      }
    }
  };

  const handleRename = async () => {
    if (!editingSession || !newName.trim()) return;
    try {
      await renameSession(editingSession.video_id, newName);
      setHistory((prev) =>
        prev.map((s) =>
          s.video_id === editingSession.video_id ? { ...s, custom_name: newName } : s
        )
      );
      setEditingSession(null);
    } catch (error) {
      alert("Failed to rename session");
    }
  };

  return (
    <>
      <Sidebar collapsible="icon" {...props}>
        <SidebarHeader>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton
                size="lg"
                className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
              >
                <div className="flex aspect-square size-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                  <Play className="size-4" />
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-white">YouTube RAG</span>
                  <span className="truncate text-xs text-muted-foreground">Premium Insights</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarHeader>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Main Navigation</SidebarGroupLabel>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton tooltip="Dashboard" isActive onClick={onNewChat}>
                  <LayoutDashboard />
                  <span>Dashboard</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton tooltip="Global History">
                  <History />
                  <span>Full History</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton tooltip="Settings">
                  <Settings />
                  <span>Settings</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>

          <SidebarGroup className="group-data-[collapsible=icon]:hidden">
            <SidebarGroupLabel>Recent Videos</SidebarGroupLabel>
            <SidebarMenu>
              {history.map((item) => (
                <SidebarMenuItem key={item.video_id}>
                  <SidebarMenuButton 
                    onClick={() => onSelectSession?.(item)}
                    tooltip={item.custom_name || item.youtube_title}
                  >
                    <div className="flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-primary/20 text-[10px] text-primary">
                      {(item.custom_name || item.youtube_title)[0].toUpperCase()}
                    </div>
                    <span className="truncate">{item.custom_name || item.youtube_title}</span>
                  </SidebarMenuButton>
                  <DropdownMenu>
                    <DropdownMenuTrigger
                      render={
                        <SidebarMenuAction showOnHover>
                          <MoreHorizontal />
                          <span className="sr-only">More</span>
                        </SidebarMenuAction>
                      }
                    />
                    <DropdownMenuContent className="w-48 bg-zinc-950 border-white/10 text-white" side="right" align="start">
                      <DropdownMenuItem 
                        onClick={() => {
                          setEditingSession(item);
                          setNewName(item.custom_name || item.youtube_title);
                        }}
                        className="gap-2 cursor-pointer"
                      >
                        <Pencil className="size-4" />
                        <span>Rename Session</span>
                      </DropdownMenuItem>
                      <DropdownMenuItem 
                        className="text-destructive focus:text-destructive gap-2 cursor-pointer"
                        onClick={() => handleDelete(item.video_id)}
                      >
                        <Trash2 className="size-4" />
                        <span>Delete Session</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </SidebarMenuItem>
              ))}
              <SidebarMenuItem>
                <SidebarMenuButton 
                  onClick={onNewChat}
                  className="text-sidebar-foreground/70"
                >
                  <Plus className="size-4" />
                  <span>New Analysis</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroup>
        </SidebarContent>
        <SidebarFooter>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton size="lg">
                <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-muted">
                  AH
                </div>
                <div className="grid flex-1 text-left text-sm leading-tight">
                  <span className="truncate font-semibold text-white">Afzal Husen</span>
                  <span className="truncate text-xs text-muted-foreground">Local Session</span>
                </div>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>

      <Dialog open={!!editingSession} onOpenChange={(open) => !open && setEditingSession(null)}>
        <DialogContent className="bg-zinc-950 border-white/10 text-white">
          <DialogHeader>
            <DialogTitle>Rename Session</DialogTitle>
          </DialogHeader>
          <div className="py-4">
            <Input 
              value={newName} 
              onChange={(e) => setNewName(e.target.value)} 
              placeholder="Enter new name..."
              className="bg-zinc-900 border-white/5"
            />
          </div>
          <DialogFooter>
            <Button variant="ghost" onClick={() => setEditingSession(null)}>Cancel</Button>
            <Button onClick={handleRename}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
}
