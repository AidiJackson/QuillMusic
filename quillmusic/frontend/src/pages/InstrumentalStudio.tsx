import { useEffect, useState } from 'react'
import { Music, Radio, Info } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/apiClient'
import type {
  SongBlueprintResponse,
  ManualProject,
  InstrumentalRenderRequest,
  InstrumentalRenderStatus,
  InstrumentalSourceType,
  InstrumentalEngineType,
  InstrumentalQuality,
  InstrumentalEngineInfo,
} from '@/types'

export default function InstrumentalStudio() {
  // Source selection
  const [sourceType, setSourceType] = useState<InstrumentalSourceType>('blueprint')
  const [blueprints, setBlueprints] = useState<SongBlueprintResponse[]>([])
  const [manualProjects, setManualProjects] = useState<ManualProject[]>([])
  const [selectedSourceId, setSelectedSourceId] = useState<string>('')
  const [selectedSource, setSelectedSource] = useState<SongBlueprintResponse | ManualProject | null>(null)

  // Render settings
  const [availableEngines, setAvailableEngines] = useState<InstrumentalEngineInfo[]>([])
  const [selectedEngineName, setSelectedEngineName] = useState<string>('fake')
  const [durationSeconds, setDurationSeconds] = useState<string>('')
  const [styleHint, setStyleHint] = useState<string>('')
  const [quality, setQuality] = useState<InstrumentalQuality>('standard')

  // Job status
  const [currentJob, setCurrentJob] = useState<InstrumentalRenderStatus | null>(null)
  const [isRendering, setIsRendering] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load config on mount to get available engines
  useEffect(() => {
    loadConfig()
  }, [])

  // Load sources on mount and when source type changes
  useEffect(() => {
    if (sourceType === 'blueprint') {
      loadBlueprints()
    } else {
      loadManualProjects()
    }
  }, [sourceType])

  // Load selected source details
  useEffect(() => {
    if (selectedSourceId) {
      loadSourceDetails()
    }
  }, [selectedSourceId, sourceType])

  const loadConfig = async () => {
    try {
      const config = await apiClient.getConfig()
      const engines = config.features.instrumental_engines || []
      setAvailableEngines(engines)

      // Set default engine to first available
      if (engines.length > 0) {
        setSelectedEngineName(engines[0].name)
      }
    } catch (error) {
      console.error('Failed to load config:', error)
    }
  }

  const loadBlueprints = async () => {
    try {
      const data = await apiClient.listSongBlueprints(20)
      setBlueprints(data)
      if (data.length > 0 && !selectedSourceId) {
        setSelectedSourceId(data[0].song_id)
      }
    } catch (error) {
      console.error('Failed to load blueprints:', error)
    }
  }

  const loadManualProjects = async () => {
    try {
      const data = await apiClient.manual.listProjects()
      setManualProjects(data)
      if (data.length > 0 && !selectedSourceId) {
        setSelectedSourceId(data[0].id)
      }
    } catch (error) {
      console.error('Failed to load manual projects:', error)
    }
  }

  const loadSourceDetails = async () => {
    try {
      if (sourceType === 'blueprint') {
        const blueprint = blueprints.find(b => b.song_id === selectedSourceId)
        setSelectedSource(blueprint || null)
      } else {
        const project = manualProjects.find(p => p.id === selectedSourceId)
        setSelectedSource(project || null)
      }
    } catch (error) {
      console.error('Failed to load source details:', error)
    }
  }

  const handleRender = async () => {
    if (!selectedSourceId) {
      setError('Please select a source')
      return
    }

    setIsRendering(true)
    setError(null)

    try {
      // Find the selected engine info
      const selectedEngine = availableEngines.find(e => e.name === selectedEngineName)
      const engineType = (selectedEngine?.engine_type || 'fake') as InstrumentalEngineType

      const request: InstrumentalRenderRequest = {
        source_type: sourceType,
        source_id: selectedSourceId,
        engine_type: engineType,
        model: selectedEngineName,  // Pass engine name as model parameter
        duration_seconds: durationSeconds ? parseInt(durationSeconds) : null,
        style_hint: styleHint || null,
        quality,
      }

      const job = await apiClient.instrumental.render(request)
      setCurrentJob(job)
    } catch (error) {
      console.error('Render failed:', error)
      setError(error instanceof Error ? error.message : 'Render failed')
    } finally {
      setIsRendering(false)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready':
        return 'bg-green-600'
      case 'processing':
        return 'bg-blue-600'
      case 'queued':
        return 'bg-yellow-600'
      case 'failed':
        return 'bg-red-600'
      default:
        return 'bg-gray-600'
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-4xl font-bold">Instrumental Studio</h1>
          <p className="text-gray-400 mt-2">
            Render instrumentals from AI blueprints or manual projects
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Source Selector */}
          <div className="col-span-3 space-y-4">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-lg">Source</CardTitle>
                <CardDescription>Choose what to render from</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Source Type Selector */}
                <div>
                  <Label>Source Type</Label>
                  <div className="grid grid-cols-2 gap-2 mt-2">
                    <Button
                      variant={sourceType === 'blueprint' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        setSourceType('blueprint')
                        setSelectedSourceId('')
                      }}
                    >
                      AI Blueprint
                    </Button>
                    <Button
                      variant={sourceType === 'manual_project' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => {
                        setSourceType('manual_project')
                        setSelectedSourceId('')
                      }}
                    >
                      Manual Project
                    </Button>
                  </div>
                </div>

                {/* Source Selector */}
                <div>
                  <Label>
                    {sourceType === 'blueprint' ? 'Blueprint' : 'Project'}
                  </Label>
                  <Select value={selectedSourceId} onValueChange={setSelectedSourceId}>
                    <SelectTrigger className="bg-gray-800 border-gray-700">
                      <SelectValue placeholder="Select source..." />
                    </SelectTrigger>
                    <SelectContent>
                      {sourceType === 'blueprint' ? (
                        blueprints.map(bp => (
                          <SelectItem key={bp.song_id} value={bp.song_id}>
                            {bp.title}
                          </SelectItem>
                        ))
                      ) : (
                        manualProjects.map(proj => (
                          <SelectItem key={proj.id} value={proj.id}>
                            {proj.name}
                          </SelectItem>
                        ))
                      )}
                    </SelectContent>
                  </Select>
                </div>

                {/* Source Summary */}
                {selectedSource && (
                  <div className="pt-2 border-t border-gray-800 text-sm">
                    {sourceType === 'blueprint' && 'title' in selectedSource ? (
                      <>
                        <div className="flex items-center gap-2 mb-1">
                          <Music className="w-4 h-4" />
                          <span>{selectedSource.bpm} BPM • {selectedSource.key}</span>
                        </div>
                        <div className="text-gray-400">
                          {selectedSource.genre} • {selectedSource.mood}
                        </div>
                        <div className="text-gray-400 mt-1">
                          {selectedSource.sections.length} sections
                        </div>
                      </>
                    ) : selectedSource && 'tempo_bpm' in selectedSource ? (
                      <>
                        <div className="flex items-center gap-2 mb-1">
                          <Music className="w-4 h-4" />
                          <span>{selectedSource.tempo_bpm} BPM</span>
                        </div>
                        <div className="text-gray-400">
                          {selectedSource.key || 'No key set'}
                        </div>
                      </>
                    ) : null}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Render Settings */}
          <div className="col-span-6">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Render Settings</CardTitle>
                <CardDescription>Configure your instrumental render</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Engine Selection */}
                <div>
                  <Label htmlFor="engine">Audio Engine</Label>
                  <Select value={selectedEngineName} onValueChange={setSelectedEngineName}>
                    <SelectTrigger id="engine" className="bg-gray-800 border-gray-700">
                      <SelectValue placeholder="Select engine..." />
                    </SelectTrigger>
                    <SelectContent>
                      {availableEngines.map(engine => (
                        <SelectItem key={engine.name} value={engine.name} disabled={!engine.available}>
                          {engine.label} {!engine.available && '(Not Configured)'}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedEngineName === 'fake' ? (
                    <p className="text-xs text-gray-500 mt-1">
                      Demo engine generates fake audio URLs for testing
                    </p>
                  ) : selectedEngineName === 'stable_audio_api' ? (
                    <div className="mt-2 p-3 bg-purple-900/20 border border-purple-700/50 rounded text-xs">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-purple-400" />
                        <div className="text-purple-200">
                          <strong className="block mb-1">Stable Audio Hosted API</strong>
                          <p className="text-purple-300/80">
                            Uses the official Stable Audio API to generate high-quality music.
                            Requires STABLE_AUDIO_API_BASE_URL and STABLE_AUDIO_API_KEY settings.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : selectedEngineName === 'replicate_musicgen' ? (
                    <div className="mt-2 p-3 bg-blue-900/20 border border-blue-700/50 rounded text-xs">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-blue-400" />
                        <div className="text-blue-200">
                          <strong className="block mb-1">Replicate MusicGen (Hosted Cloud)</strong>
                          <p className="text-blue-300/80">
                            Uses Replicate's hosted MusicGen model to generate music on-demand.
                            Requires REPLICATE_API_TOKEN and REPLICATE_MUSICGEN_VERSION settings.
                            Fast, scalable cloud inference with pay-per-use pricing.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : selectedEngineName === 'musicgen' ? (
                    <div className="mt-2 p-3 bg-purple-900/20 border border-purple-700/50 rounded text-xs">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-purple-400" />
                        <div className="text-purple-200">
                          <strong className="block mb-1">MusicGen (Meta, Free)</strong>
                          <p className="text-purple-300/80">
                            Uses a self-hosted MusicGen server to generate free, high-quality instrumentals.
                            Requires MUSICGEN_BASE_URL pointing to your MusicGen HTTP service.
                          </p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="mt-2 p-3 bg-purple-900/20 border border-purple-700/50 rounded text-xs">
                      <div className="flex items-start gap-2">
                        <Info className="w-4 h-4 mt-0.5 flex-shrink-0 text-purple-400" />
                        <div className="text-purple-200">
                          <strong className="block mb-1">External Audio Engine</strong>
                          <p className="text-purple-300/80">
                            Uses a real audio generation API. Configuration must be set on the server.
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>

                {/* Duration */}
                <div>
                  <Label htmlFor="duration">Duration (seconds)</Label>
                  <Input
                    id="duration"
                    type="number"
                    placeholder="Auto (based on source)"
                    value={durationSeconds}
                    onChange={(e) => setDurationSeconds(e.target.value)}
                    className="bg-gray-800 border-gray-700"
                    min="1"
                    max="600"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty to auto-calculate from source
                  </p>
                </div>

                {/* Style Hint */}
                <div>
                  <Label htmlFor="style">Style Hint</Label>
                  <Textarea
                    id="style"
                    placeholder="e.g., 'dark cinematic trap with atmospheric pads'"
                    value={styleHint}
                    onChange={(e) => setStyleHint(e.target.value)}
                    className="bg-gray-800 border-gray-700 min-h-[80px]"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Optional style guidance for AI engine (future use)
                  </p>
                </div>

                {/* Quality */}
                <div>
                  <Label htmlFor="quality">Quality</Label>
                  <Select value={quality} onValueChange={(v) => setQuality(v as InstrumentalQuality)}>
                    <SelectTrigger id="quality" className="bg-gray-800 border-gray-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="standard">Standard</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Render Button */}
                <Button
                  onClick={handleRender}
                  disabled={isRendering || !selectedSourceId}
                  className="w-full"
                  size="lg"
                >
                  <Radio className="w-4 h-4 mr-2" />
                  {isRendering ? 'Rendering...' : 'Render Instrumental'}
                </Button>

                {error && (
                  <div className="bg-red-900/20 border border-red-700 rounded p-3 text-sm text-red-400">
                    {error}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Job Status & Player */}
          <div className="col-span-3">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-lg">Job Status</CardTitle>
              </CardHeader>
              <CardContent>
                {currentJob ? (
                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-400">Status</span>
                        <Badge className={getStatusColor(currentJob.status)}>
                          {currentJob.status}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-500">
                        Job ID: {currentJob.id.slice(0, 8)}...
                      </div>
                    </div>

                    <div className="pt-2 border-t border-gray-800 space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Engine:</span>
                        <span>{currentJob.engine_type}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Source:</span>
                        <span>{currentJob.source_type}</span>
                      </div>
                      {currentJob.duration_seconds && (
                        <div className="flex justify-between">
                          <span className="text-gray-400">Duration:</span>
                          <span>{currentJob.duration_seconds}s</span>
                        </div>
                      )}
                    </div>

                    {currentJob.audio_url && (
                      <div className="pt-2 border-t border-gray-800">
                        <Label className="text-xs mb-2 block">Audio Preview</Label>
                        <audio
                          controls
                          className="w-full"
                          src={currentJob.audio_url}
                        />
                        <div className="mt-2 p-2 bg-blue-900/20 border border-blue-700/50 rounded text-xs">
                          <Info className="w-3 h-3 inline mr-1" />
                          Demo URL from FakeInstrumentalEngine
                        </div>
                      </div>
                    )}

                    {currentJob.error_message && (
                      <div className="pt-2 border-t border-gray-800">
                        <div className="bg-red-900/20 border border-red-700 rounded p-2 text-xs text-red-400">
                          {currentJob.error_message}
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    No render job yet. Configure settings and click "Render Instrumental"
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
