"use client"

import { Clock, ExternalLink } from "lucide-react"
import { SourceDocument } from "@/lib/api"

interface SourceChipsProps {
  sources: SourceDocument[]
}

export function SourceChips({ sources }: SourceChipsProps) {
  if (!sources || sources.length === 0) return null

  const formatTime = (seconds: number) => {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hrs > 0 ? `${hrs}:` : ""}${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="flex flex-wrap gap-2 mt-4 pt-4 border-t border-white/5">
      <p className="w-full text-[10px] uppercase tracking-wider text-muted-foreground font-semibold mb-1">
        Sources & Timestamps
      </p>
      {sources.map((source, i) => (
        <button
          key={i}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/[0.03] border border-white/10 hover:bg-white/10 transition-colors text-xs text-zinc-300 group"
          onClick={() => {
            // Ideally this would emit an event to a video player
            console.log(`Jump to ${source.metadata.start}`)
          }}
        >
          <Clock className="size-3 text-primary/70" />
          <span>{formatTime(source.metadata.start)}</span>
          <ExternalLink className="size-3 opacity-0 group-hover:opacity-100 transition-opacity ml-1" />
        </button>
      ))}
    </div>
  )
}
