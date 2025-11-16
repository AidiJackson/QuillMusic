/**
 * QuillMusic API Client
 *
 * Centralized API communication layer for the QuillMusic frontend.
 * All API calls go through /api proxy (configured in vite.config.ts)
 * which forwards to the backend at localhost:8000.
 */

import type {
  SongBlueprintRequest,
  SongBlueprintResponse,
  RenderJobCreate,
  RenderJobStatus,
  ManualProjectCreate,
  ManualProject,
  ManualProjectDetail,
  TrackCreate,
  TrackUpdate,
  Track,
  PatternCreate,
  PatternUpdate,
  Pattern,
  NoteCreate,
  Note,
  InstrumentalRenderRequest,
  InstrumentalRenderStatus,
  HitMakerAnalysis,
  HitMakerInfluenceRequest,
  HitMakerInfluenceResponse,
  AppConfig,
} from '@/types'

/**
 * Base API URL - uses relative /api path which is proxied by Vite dev server
 * to the backend at localhost:8000
 */
const API_BASE = '/api'

/**
 * Generic fetch wrapper with error handling
 */
async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE}${endpoint}`

  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  })

  if (!response.ok) {
    const errorText = await response.text()
    let errorMessage = `API Error: ${response.status} ${response.statusText}`

    try {
      const errorJson = JSON.parse(errorText)
      errorMessage = errorJson.detail || errorMessage
    } catch {
      errorMessage = errorText || errorMessage
    }

    throw new Error(errorMessage)
  }

  return response.json()
}

/**
 * Song Blueprint API
 */
const songBlueprintApi = {
  /**
   * Generate a new song blueprint from a prompt
   */
  async createBlueprint(request: SongBlueprintRequest): Promise<SongBlueprintResponse> {
    return apiFetch<SongBlueprintResponse>('/song/blueprint', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  /**
   * List all song blueprints
   */
  async listBlueprints(limit: number = 50): Promise<SongBlueprintResponse[]> {
    return apiFetch<SongBlueprintResponse[]>(`/song/blueprints?limit=${limit}`)
  },

  /**
   * Get a specific blueprint by ID
   */
  async getBlueprint(blueprintId: string): Promise<SongBlueprintResponse> {
    return apiFetch<SongBlueprintResponse>(`/song/blueprints/${blueprintId}`)
  },
}

/**
 * Render API (legacy vocal/full mix renders)
 */
const renderApi = {
  /**
   * Create a new render job
   */
  async createRender(request: RenderJobCreate): Promise<RenderJobStatus> {
    return apiFetch<RenderJobStatus>('/renders', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  /**
   * Get render job status
   */
  async getRenderStatus(jobId: string): Promise<RenderJobStatus> {
    return apiFetch<RenderJobStatus>(`/renders/${jobId}`)
  },
}

/**
 * Manual Creator API (DAW-style projects)
 */
const manualApi = {
  /**
   * Create a new manual project
   */
  async createProject(project: ManualProjectCreate): Promise<ManualProject> {
    return apiFetch<ManualProject>('/manual/projects', {
      method: 'POST',
      body: JSON.stringify(project),
    })
  },

  /**
   * List all manual projects
   */
  async listProjects(): Promise<ManualProject[]> {
    return apiFetch<ManualProject[]>('/manual/projects')
  },

  /**
   * Get project details including tracks, patterns, notes
   */
  async getProject(projectId: string): Promise<ManualProjectDetail> {
    return apiFetch<ManualProjectDetail>(`/manual/projects/${projectId}`)
  },

  /**
   * Delete a project
   */
  async deleteProject(projectId: string): Promise<void> {
    await apiFetch<void>(`/manual/projects/${projectId}`, {
      method: 'DELETE',
    })
  },

  /**
   * Create a track in a project
   */
  async createTrack(projectId: string, track: TrackCreate): Promise<Track> {
    return apiFetch<Track>(`/manual/projects/${projectId}/tracks`, {
      method: 'POST',
      body: JSON.stringify(track),
    })
  },

  /**
   * Update a track
   */
  async updateTrack(trackId: string, update: TrackUpdate): Promise<Track> {
    return apiFetch<Track>(`/manual/tracks/${trackId}`, {
      method: 'PATCH',
      body: JSON.stringify(update),
    })
  },

  /**
   * Delete a track
   */
  async deleteTrack(trackId: string): Promise<void> {
    await apiFetch<void>(`/manual/tracks/${trackId}`, {
      method: 'DELETE',
    })
  },

  /**
   * Create a pattern in a track
   */
  async createPattern(trackId: string, pattern: PatternCreate): Promise<Pattern> {
    return apiFetch<Pattern>(`/manual/tracks/${trackId}/patterns`, {
      method: 'POST',
      body: JSON.stringify(pattern),
    })
  },

  /**
   * Update a pattern
   */
  async updatePattern(patternId: string, update: PatternUpdate): Promise<Pattern> {
    return apiFetch<Pattern>(`/manual/patterns/${patternId}`, {
      method: 'PATCH',
      body: JSON.stringify(update),
    })
  },

  /**
   * Delete a pattern
   */
  async deletePattern(patternId: string): Promise<void> {
    await apiFetch<void>(`/manual/patterns/${patternId}`, {
      method: 'DELETE',
    })
  },

  /**
   * Get notes for a pattern
   */
  async getNotes(patternId: string): Promise<Note[]> {
    return apiFetch<Note[]>(`/manual/patterns/${patternId}/notes`)
  },

  /**
   * Bulk create notes
   */
  async createNotesBulk(patternId: string, notes: NoteCreate[]): Promise<Note[]> {
    return apiFetch<Note[]>(`/manual/patterns/${patternId}/notes/bulk`, {
      method: 'POST',
      body: JSON.stringify(notes),
    })
  },
}

/**
 * Instrumental Rendering API
 */
const instrumentalApi = {
  /**
   * Render an instrumental from a blueprint or manual project
   */
  async render(request: InstrumentalRenderRequest): Promise<InstrumentalRenderStatus> {
    return apiFetch<InstrumentalRenderStatus>('/instrumental/render', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  /**
   * Get instrumental job status
   */
  async getJobStatus(jobId: string): Promise<InstrumentalRenderStatus> {
    return apiFetch<InstrumentalRenderStatus>(`/instrumental/jobs/${jobId}`)
  },
}

/**
 * HitMaker API (song analysis and influence mixing)
 */
const hitmakerApi = {
  /**
   * Analyze a blueprint's hit potential
   */
  async analyzeBlueprint(blueprintId: string): Promise<HitMakerAnalysis> {
    return apiFetch<HitMakerAnalysis>('/hitmaker/analyze/blueprint', {
      method: 'POST',
      body: JSON.stringify({ blueprint_id: blueprintId }),
    })
  },

  /**
   * Analyze a manual project's hit potential
   */
  async analyzeManual(projectId: string): Promise<HitMakerAnalysis> {
    return apiFetch<HitMakerAnalysis>('/hitmaker/analyze/manual', {
      method: 'POST',
      body: JSON.stringify({ manual_project_id: projectId }),
    })
  },

  /**
   * Apply influences to a blueprint
   */
  async influenceBlueprint(request: HitMakerInfluenceRequest): Promise<HitMakerInfluenceResponse> {
    return apiFetch<HitMakerInfluenceResponse>('/hitmaker/influence/blueprint', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },

  /**
   * Apply influences to a manual project
   */
  async influenceManual(request: HitMakerInfluenceRequest): Promise<HitMakerInfluenceResponse> {
    return apiFetch<HitMakerInfluenceResponse>('/hitmaker/influence/manual', {
      method: 'POST',
      body: JSON.stringify(request),
    })
  },
}

/**
 * Vocals API (ElevenLabs TTS integration)
 */
const vocalsApi = {
  /**
   * Generate a vocal preview using ElevenLabs TTS
   * Returns audio blob (MP3 format)
   */
  async preview(params: {
    text: string
    voiceId: string
    modelId?: string
  }): Promise<Blob> {
    const url = `${API_BASE}/vocals/preview`

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        text: params.text,
        voice_id: params.voiceId,
        model_id: params.modelId,
      }),
    })

    if (!response.ok) {
      const errorText = await response.text().catch(() => '')
      let errorMessage = `Failed to generate vocal preview (${response.status})`

      try {
        const errorJson = JSON.parse(errorText)
        errorMessage = errorJson.detail || errorMessage
      } catch {
        errorMessage = errorText || errorMessage
      }

      throw new Error(errorMessage)
    }

    // Return audio blob
    return await response.blob()
  },
}

/**
 * Config & Feature Flags API
 */
const configApi = {
  /**
   * Get app configuration and feature flags
   */
  async getConfig(): Promise<AppConfig> {
    return apiFetch<AppConfig>('/')
  },

  /**
   * Health check
   */
  async health(): Promise<{ status: string; timestamp: string }> {
    return apiFetch<{ status: string; timestamp: string }>('/health')
  },
}

/**
 * Main API Client
 *
 * Usage:
 * ```typescript
 * import { apiClient } from '@/lib/apiClient'
 *
 * // Create a song blueprint
 * const blueprint = await apiClient.createBlueprint({ prompt: '...', genre: 'Pop', mood: 'Energetic' })
 *
 * // List blueprints
 * const blueprints = await apiClient.listSongBlueprints(20)
 *
 * // Render an instrumental
 * const job = await apiClient.instrumental.render({ source_type: 'blueprint', source_id: '123' })
 * ```
 */
export const apiClient = {
  // Song Blueprint shortcuts (commonly used)
  createBlueprint: songBlueprintApi.createBlueprint,
  listSongBlueprints: songBlueprintApi.listBlueprints,
  getBlueprint: songBlueprintApi.getBlueprint,

  // Backward compatibility aliases
  createSongBlueprint: songBlueprintApi.createBlueprint,
  getSongBlueprint: songBlueprintApi.getBlueprint,
  createRenderJob: renderApi.createRender,
  getRenderJob: renderApi.getRenderStatus,

  // Namespaced APIs
  render: renderApi,
  manual: {
    ...manualApi,
    // Backward compatibility aliases
    getProjectDetail: manualApi.getProject,
    getPatternNotes: manualApi.getNotes,
    replacePatternNotes: manualApi.createNotesBulk,
  },
  instrumental: instrumentalApi,
  hitmaker: hitmakerApi,
  vocals: vocalsApi,
  config: configApi,
}

export default apiClient
