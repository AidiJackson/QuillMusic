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
  model?: string | null
  duration_seconds?: number | null
  style_hint?: string | null
  quality?: InstrumentalQuality | null
}

export interface InstrumentalRenderStatus {
  id: string
  status: InstrumentalStatus
  engine_type: InstrumentalEngineType
  model?: string | null
  source_type: InstrumentalSourceType
  source_id: string
  duration_seconds?: number | null
  audio_url?: string | null
  error_message?: string | null
  created_at: string
  updated_at: string
}

// ========== Config & Feature Flags ==========

export interface AudioProviderInfo {
  provider: string
  available: boolean
  models: string[]
}

export interface FeatureFlags {
  external_instrumental_available: boolean
  audio_provider: AudioProviderInfo
}

export interface AppConfig {
  app_name: string
  app_version: string
  features: FeatureFlags
}
// ========== HitMaker Types ==========

export interface SectionEnergy {
  name: string
  position_index: number
  energy: number
  tension: number
  hook_density: number
  notes?: string | null
}

export interface SongDNA {
  blueprint_id?: string | null
  manual_project_id?: string | null
  sections: SectionEnergy[]
  global_energy_curve: number[]
  global_tension_curve: number[]
  dominant_mood: string
  genre_guess: string
  structure_notes: string[]
}

export interface HitScoreBreakdown {
  overall: number
  hook_strength: number
  structure: number
  lyrics_emotion: number
  genre_fit: number
  originality: number
  replay_value: number
}

export interface HitMakerAnalysis {
  dna: SongDNA
  score: HitScoreBreakdown
  commentary: string[]
  risks: string[]
  opportunities: string[]
}

export interface InfluenceDescriptor {
  name: string
  weight: number
}

export interface HitMakerInfluenceRequest {
  source_blueprint_id?: string | null
  source_manual_project_id?: string | null
  influences: InfluenceDescriptor[]
  target_mood?: string | null
  target_genre?: string | null
}

export interface HitMakerInfluenceResponse {
  adjusted_dna: SongDNA
  hook_suggestions: string[]
  chorus_rewrite_ideas: string[]
  structure_suggestions: string[]
  instrumentation_ideas: string[]
  vocal_style_notes: string[]
}
