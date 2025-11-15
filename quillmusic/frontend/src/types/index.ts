/**
 * QuillMusic Frontend Types
 * Mirror of backend schemas
 */

export type SectionType =
  | "intro"
  | "verse"
  | "pre_chorus"
  | "chorus"
  | "bridge"
  | "drop"
  | "outro"
  | "mix_segment"

export interface SectionSchema {
  id: string
  type: SectionType
  name: string
  bars: number
  mood: string
  description: string
  instruments: string[]
}

export interface VocalStyleSchema {
  gender: "male" | "female" | "mixed" | "auto"
  tone: string
  energy: "low" | "medium" | "high"
  accent?: string | null
}

export interface SongBlueprintRequest {
  prompt: string
  genre: string
  mood: string
  bpm?: number
  key?: string
  duration_seconds?: number
  reference_text?: string
}

export interface SongBlueprintResponse {
  song_id: string
  title: string
  genre: string
  mood: string
  bpm: number
  key: string
  sections: SectionSchema[]
  lyrics: Record<string, string>
  vocal_style: VocalStyleSchema
  notes?: string | null
}

export type RenderType = "instrumental" | "vocals" | "full_mix"
export type RenderStatus = "queued" | "processing" | "failed" | "ready"

export interface RenderJobCreate {
  song_id: string
  render_type: RenderType
}

export interface RenderJobStatus {
  job_id: string
  song_id: string
  render_type: RenderType
  status: RenderStatus
  audio_url?: string | null
  error?: string | null
}
