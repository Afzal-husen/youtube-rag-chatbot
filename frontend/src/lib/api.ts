const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ProcessUrlResponse {
  video_id: string;
  title: string;
  author: string;
  thumbnail_url?: string;
  already_indexed: boolean;
  message: string;
}

export interface SourceDocument {
  content: string;
  metadata: {
    start: number;
    duration: number;
    source: string;
    url: string;
  };
}

export interface ChatResponse {
  answer: string;
  source_documents: SourceDocument[];
}

export interface VideoSession {
  video_id: string;
  custom_name?: string;
  youtube_title: string;
  author?: string;
  thumbnail_url?: string;
  indexed_at: string;
}

export interface MessageHistoryItem {
  id: number;
  video_id: string;
  role: "user" | "assistant";
  content: string;
  sources?: any[];
  created_at: string;
}

export type StreamChunk = 
  | { type: "sources"; data: SourceDocument[] }
  | { type: "chunk"; data: string }
  | { type: "error"; data: string };

export async function processUrl(url: string): Promise<ProcessUrlResponse> {
  const response = await fetch(`${API_BASE_URL}/api/process-url`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!response.ok) throw new Error("Failed to process video URL");
  return response.json();
}

export async function* streamChatWithVideo(
  videoId: string, 
  question: string,
  modelName: string = "llama-3.1-8b-instant"
): AsyncGenerator<StreamChunk> {
  const response = await fetch(`${API_BASE_URL}/api/chat-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ video_id: videoId, question, model_name: modelName }),
  });

  if (!response.ok) throw new Error("Failed to start chat stream");

  const reader = response.body?.getReader();
  if (!reader) throw new Error("No readable stream available");

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    
    const lines = buffer.split("\n\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data === "[DONE]") return;
        try {
          yield JSON.parse(data) as StreamChunk;
        } catch (e) {
          console.error("Error parsing stream chunk:", e);
        }
      }
    }
  }
}

export async function getHistory(): Promise<VideoSession[]> {
  const response = await fetch(`${API_BASE_URL}/api/history`);
  if (!response.ok) throw new Error("Failed to fetch history");
  return response.json();
}

export async function getSessionMessages(videoId: string): Promise<MessageHistoryItem[]> {
  const response = await fetch(`${API_BASE_URL}/api/history/${videoId}/messages`);
  if (!response.ok) throw new Error("Failed to fetch messages");
  return response.json();
}

export async function renameSession(videoId: string, name: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/history/${videoId}?name=${encodeURIComponent(name)}`, {
    method: "PATCH",
  });
  if (!response.ok) throw new Error("Failed to rename session");
}

export async function deleteSession(videoId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/history/${videoId}`, {
    method: "DELETE",
  });
  if (!response.ok) throw new Error("Failed to delete session");
}
