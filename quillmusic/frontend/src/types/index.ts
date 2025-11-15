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

// ========== Manual Creator Types ==========

export type InstrumentType = "drums" | "bass" | "chords" | "lead" | "fx" | "vocal"

export interface ManualProjectCreate {
  name: string
  tempo_bpm: number
  time_signature: string
  key?: string | null
  description?: string | null
}

export interface ManualProject {
  id: string
  name: string
  tempo_bpm: number
  time_signature: string
  key?: string | null
  description?: string | null
  created_at: string
  updated_at: string
}

export interface TrackCreate {
  name: string
  instrument_type: InstrumentType
  channel_index: number
}

export interface TrackUpdate {
  name?: string
  volume?: number
  pan?: number
  muted?: boolean
  solo?: boolean
  channel_index?: number
}

export interface Track {
  id: string
  project_id: string
  name: string
  instrument_type: InstrumentType
  channel_index: number
  volume: number
  pan: number
  muted: boolean
  solo: boolean
}

export interface PatternCreate {
  name: string
  length_bars: number
  start_bar: number
}

export interface PatternUpdate {
  name?: string
  length_bars?: number
  start_bar?: number
}

export interface Pattern {
  id: string
  track_id: string
  name: string
  length_bars: number
  start_bar: number
}

export interface NoteCreate {
  pattern_id: string
  step_index: number
  pitch: number
  velocity: number
}

export interface Note {
  id: string
  pattern_id: string
  step_index: number
  pitch: number
  velocity: number
}

export interface ManualProjectDetail {
  project: ManualProject
  tracks: Track[]
  patterns: Pattern[]
  notes: Note[]
}

// ========== Instrumental Rendering Types ==========

export type InstrumentalEngineType = "fake" | "external_http"
export type InstrumentalSourceType = "blueprint" | "manual_project"
export type InstrumentalStatus = "queued" | "processing" | "ready" | "failed"
export type InstrumentalQuality = "draft" | "standard" | "high"

export interface InstrumentalRenderRequest {
  source_type: InstrumentalSourceType
  source_id: string
  engine_type?: InstrumentalEngineType
  duration_seconds?: number | null
  style_hint?: string | null
  quality?: InstrumentalQuality | null
}

export interface InstrumentalRenderStatus {
  id: string
  status: InstrumentalStatus
  engine_type: InstrumentalEngineType
  source_type: InstrumentalSourceType
  source_id: string
  duration_seconds?: number | null
  audio_url?: string | null
  error_message?: string | null
  created_at: string
  updated_at: string
}
