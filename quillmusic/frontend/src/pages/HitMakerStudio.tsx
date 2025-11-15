import { useEffect, useState } from 'react'
import { Sparkles, TrendingUp, AlertCircle, Lightbulb, Target, Music } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { Slider } from '@/components/ui/slider'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { apiClient } from '@/lib/apiClient'
import type {
  SongBlueprintResponse,
  ManualProject,
  ManualProjectDetail,
  HitMakerAnalysis,
  HitMakerInfluenceRequest,
  HitMakerInfluenceResponse,
  InfluenceDescriptor,
} from '@/types'

export default function HitMakerStudio() {
  // Source selection
  const [sourceType, setSourceType] = useState<'blueprint' | 'manual'>('blueprint')
  const [blueprints, setBlueprints] = useState<SongBlueprintResponse[]>([])
  const [manualProjects, setManualProjects] = useState<ManualProject[]>([])
  const [selectedSourceId, setSelectedSourceId] = useState<string>('')
  const [selectedSource, setSelectedSource] = useState<SongBlueprintResponse | ManualProjectDetail | null>(null)

  // Analysis results
  const [analysis, setAnalysis] = useState<HitMakerAnalysis | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  // Influence settings
  const [influences, setInfluences] = useState<InfluenceDescriptor[]>([
    { name: '', weight: 0.5 },
  ])
  const [targetMood, setTargetMood] = useState<string>('')
  const [targetGenre, setTargetGenre] = useState<string>('')
  const [influenceResponse, setInfluenceResponse] = useState<HitMakerInfluenceResponse | null>(null)
  const [isApplyingInfluence, setIsApplyingInfluence] = useState(false)

  const [error, setError] = useState<string | null>(null)

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
        const blueprint = await apiClient.getSongBlueprint(selectedSourceId)
        setSelectedSource(blueprint)
      } else {
        const project = await apiClient.manual.getProjectDetail(selectedSourceId)
        setSelectedSource(project)
      }
    } catch (error) {
      console.error('Failed to load source details:', error)
    }
  }

  const handleAnalyze = async () => {
    if (!selectedSourceId) {
      setError('Please select a source')
      return
    }

    setIsAnalyzing(true)
    setError(null)

    try {
      let result: HitMakerAnalysis
      if (sourceType === 'blueprint') {
        result = await apiClient.hitmaker.analyzeBlueprint(selectedSourceId)
      } else {
        result = await apiClient.hitmaker.analyzeManual(selectedSourceId)
      }
      setAnalysis(result)
    } catch (err: any) {
      setError(err.message || 'Failed to analyze song')
    } finally {
      setIsAnalyzing(false)
    }
  }

  const handleApplyInfluences = async () => {
    if (!selectedSourceId) {
      setError('Please select a source')
      return
    }

    // Filter out empty influences
    const validInfluences = influences.filter((inf) => inf.name.trim() !== '')
    if (validInfluences.length === 0) {
      setError('Please add at least one artist influence')
      return
    }

    setIsApplyingInfluence(true)
    setError(null)

    try {
      const request: HitMakerInfluenceRequest = {
        source_blueprint_id: sourceType === 'blueprint' ? selectedSourceId : undefined,
        source_manual_project_id: sourceType === 'manual' ? selectedSourceId : undefined,
        influences: validInfluences,
        target_mood: targetMood || undefined,
        target_genre: targetGenre || undefined,
      }

      let result: HitMakerInfluenceResponse
      if (sourceType === 'blueprint') {
        result = await apiClient.hitmaker.influenceBlueprint(request)
      } else {
        result = await apiClient.hitmaker.influenceManual(request)
      }
      setInfluenceResponse(result)
    } catch (err: any) {
      setError(err.message || 'Failed to apply influences')
    } finally {
      setIsApplyingInfluence(false)
    }
  }

  const addInfluence = () => {
    if (influences.length < 3) {
      setInfluences([...influences, { name: '', weight: 0.5 }])
    }
  }

  const updateInfluence = (index: number, field: 'name' | 'weight', value: string | number) => {
    const updated = [...influences]
    updated[index] = { ...updated[index], [field]: value }
    setInfluences(updated)
  }

  const removeInfluence = (index: number) => {
    setInfluences(influences.filter((_, i) => i !== index))
  }

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-400'
    if (score >= 60) return 'text-yellow-400'
    return 'text-red-400'
  }

  const getScoreBadgeColor = (score: number): string => {
    if (score >= 80) return 'bg-green-600'
    if (score >= 60) return 'bg-yellow-600'
    return 'bg-red-600'
  }

  return (
    <div className="p-8 bg-gray-950 min-h-screen">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Sparkles className="w-8 h-8 text-purple-500" />
          <h1 className="text-3xl font-bold text-white">HitMaker Studio</h1>
        </div>
        <p className="text-gray-400">
          Analyze your songs for hit potential and get AI-powered improvement suggestions
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-6 p-4 bg-red-900/20 border border-red-700 rounded-lg flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span>{error}</span>
        </div>
      )}

      {/* Main 3-Column Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* LEFT COLUMN: Source Selection */}
        <div className="col-span-3 space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Music className="w-5 h-5 text-purple-500" />
                Source Selection
              </CardTitle>
              <CardDescription>Choose a song to analyze</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Source Type Selector */}
              <div className="space-y-2">
                <Label htmlFor="source-type" className="text-gray-300">
                  Source Type
                </Label>
                <Select value={sourceType} onValueChange={(val) => setSourceType(val as 'blueprint' | 'manual')}>
                  <SelectTrigger id="source-type" className="bg-gray-800 border-gray-700 text-white">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    <SelectItem value="blueprint">AI Blueprint</SelectItem>
                    <SelectItem value="manual">Manual Project</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {/* Source Selector */}
              <div className="space-y-2">
                <Label htmlFor="source-select" className="text-gray-300">
                  {sourceType === 'blueprint' ? 'Select Blueprint' : 'Select Project'}
                </Label>
                <Select value={selectedSourceId} onValueChange={setSelectedSourceId}>
                  <SelectTrigger id="source-select" className="bg-gray-800 border-gray-700 text-white">
                    <SelectValue placeholder="Choose a source..." />
                  </SelectTrigger>
                  <SelectContent className="bg-gray-800 border-gray-700">
                    {sourceType === 'blueprint'
                      ? blueprints.map((bp) => (
                          <SelectItem key={bp.song_id} value={bp.song_id} className="text-white">
                            {bp.title}
                          </SelectItem>
                        ))
                      : manualProjects.map((proj) => (
                          <SelectItem key={proj.id} value={proj.id} className="text-white">
                            {proj.name}
                          </SelectItem>
                        ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Source Metadata */}
              {selectedSource && (
                <div className="space-y-2 p-3 bg-gray-800 rounded-lg border border-gray-700">
                  <h4 className="text-sm font-semibold text-purple-400">Metadata</h4>
                  <div className="space-y-1 text-sm">
                    {'bpm' in selectedSource && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">BPM:</span>
                        <span className="text-white">{selectedSource.bpm}</span>
                      </div>
                    )}
                    {'tempo_bpm' in selectedSource && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">BPM:</span>
                        <span className="text-white">{String(selectedSource.tempo_bpm)}</span>
                      </div>
                    )}
                    {'key' in selectedSource && selectedSource.key && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Key:</span>
                        <span className="text-white">{selectedSource.key}</span>
                      </div>
                    )}
                    {'genre' in selectedSource && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Genre:</span>
                        <span className="text-white">{selectedSource.genre}</span>
                      </div>
                    )}
                    {'mood' in selectedSource && (
                      <div className="flex justify-between">
                        <span className="text-gray-400">Mood:</span>
                        <span className="text-white">{selectedSource.mood}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Analyze Button */}
              <Button
                onClick={handleAnalyze}
                disabled={isAnalyzing || !selectedSourceId}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
                size="lg"
              >
                <TrendingUp className="w-4 h-4 mr-2" />
                {isAnalyzing ? 'Analyzing...' : 'Analyze Song'}
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* CENTER COLUMN: Analysis Results */}
        <div className="col-span-6 space-y-6">
          {analysis ? (
            <>
              {/* HitScore Card */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white">Hit Potential Score</CardTitle>
                </CardHeader>
                <CardContent>
                  {/* Overall Score */}
                  <div className="text-center mb-6">
                    <div className={`text-7xl font-bold ${getScoreColor(analysis.score.overall)}`}>
                      {Math.round(analysis.score.overall)}
                    </div>
                    <Badge className={`mt-2 ${getScoreBadgeColor(analysis.score.overall)} text-white`}>
                      {analysis.score.overall >= 80
                        ? 'Hit Potential'
                        : analysis.score.overall >= 60
                        ? 'Strong Track'
                        : 'Needs Work'}
                    </Badge>
                  </div>

                  {/* Score Breakdown */}
                  <div className="space-y-3">
                    <h4 className="text-sm font-semibold text-purple-400 mb-3">Score Breakdown</h4>
                    {Object.entries(analysis.score)
                      .filter(([key]) => key !== 'overall')
                      .map(([key, value]) => (
                        <div key={key} className="space-y-1">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-300 capitalize">{key.replace('_', ' ')}</span>
                            <span className={`font-semibold ${getScoreColor(value)}`}>{Math.round(value)}</span>
                          </div>
                          <div className="h-2 bg-gray-800 rounded-full overflow-hidden">
                            <div
                              className="h-full bg-purple-600 rounded-full transition-all"
                              style={{ width: `${value}%` }}
                            />
                          </div>
                        </div>
                      ))}
                  </div>
                </CardContent>
              </Card>

              {/* Energy Curve */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white">Energy & Tension Curves</CardTitle>
                  <CardDescription>Track dynamics throughout the song</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Energy</span>
                      <span className="text-purple-400">●</span>
                    </div>
                    <div className="flex gap-1 h-24 items-end">
                      {analysis.dna.global_energy_curve.map((energy, idx) => (
                        <div key={idx} className="flex-1 bg-gray-800 rounded-t relative group">
                          <div
                            className="absolute bottom-0 left-0 right-0 bg-purple-600 rounded-t transition-all"
                            style={{ height: `${energy * 100}%` }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-400">Tension</span>
                      <span className="text-yellow-400">●</span>
                    </div>
                    <div className="flex gap-1 h-24 items-end">
                      {analysis.dna.global_tension_curve.map((tension, idx) => (
                        <div key={idx} className="flex-1 bg-gray-800 rounded-t relative">
                          <div
                            className="absolute bottom-0 left-0 right-0 bg-yellow-600 rounded-t transition-all"
                            style={{ height: `${tension * 100}%` }}
                          />
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Commentary & Insights */}
              <Card className="bg-gray-900 border-gray-800">
                <CardHeader>
                  <CardTitle className="text-white flex items-center gap-2">
                    <Lightbulb className="w-5 h-5 text-yellow-500" />
                    Analysis Insights
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Commentary */}
                  {analysis.commentary.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-purple-400 mb-2">Key Observations</h4>
                      <ul className="space-y-2">
                        {analysis.commentary.map((comment, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex gap-2">
                            <span className="text-purple-500">•</span>
                            <span>{comment}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Separator className="bg-gray-800" />

                  {/* Risks */}
                  {analysis.risks.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-red-400 mb-2">Potential Risks</h4>
                      <ul className="space-y-2">
                        {analysis.risks.map((risk, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex gap-2">
                            <span className="text-red-500">⚠</span>
                            <span>{risk}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <Separator className="bg-gray-800" />

                  {/* Opportunities */}
                  {analysis.opportunities.length > 0 && (
                    <div>
                      <h4 className="text-sm font-semibold text-green-400 mb-2">Opportunities</h4>
                      <ul className="space-y-2">
                        {analysis.opportunities.map((opp, idx) => (
                          <li key={idx} className="text-sm text-gray-300 flex gap-2">
                            <span className="text-green-500">✓</span>
                            <span>{opp}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Structure Notes */}
                  {analysis.dna.structure_notes.length > 0 && (
                    <>
                      <Separator className="bg-gray-800" />
                      <div>
                        <h4 className="text-sm font-semibold text-blue-400 mb-2">Structure Notes</h4>
                        <ul className="space-y-2">
                          {analysis.dna.structure_notes.map((note, idx) => (
                            <li key={idx} className="text-sm text-gray-300 flex gap-2">
                              <span className="text-blue-500">→</span>
                              <span>{note}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </>
                  )}
                </CardContent>
              </Card>
            </>
          ) : (
            <Card className="bg-gray-900 border-gray-800">
              <CardContent className="py-12 text-center">
                <TrendingUp className="w-16 h-16 text-gray-700 mx-auto mb-4" />
                <p className="text-gray-500">Select a source and click "Analyze Song" to see results</p>
              </CardContent>
            </Card>
          )}
        </div>

        {/* RIGHT COLUMN: Influence Blender */}
        <div className="col-span-3 space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="text-white flex items-center gap-2">
                <Target className="w-5 h-5 text-purple-500" />
                Influence Blender
              </CardTitle>
              <CardDescription>Apply artistic influences to your song</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <ScrollArea className="h-[300px] pr-4">
                <div className="space-y-4">
                  {/* Artist Influences */}
                  {influences.map((influence, idx) => (
                    <div key={idx} className="p-3 bg-gray-800 rounded-lg border border-gray-700 space-y-3">
                      <div className="flex justify-between items-center">
                        <Label className="text-xs text-gray-400">Influence {idx + 1}</Label>
                        {influences.length > 1 && (
                          <button
                            onClick={() => removeInfluence(idx)}
                            className="text-xs text-red-400 hover:text-red-300"
                          >
                            Remove
                          </button>
                        )}
                      </div>
                      <Input
                        placeholder="Artist name..."
                        value={influence.name}
                        onChange={(e) => updateInfluence(idx, 'name', e.target.value)}
                        className="bg-gray-900 border-gray-700 text-white"
                      />
                      <div className="space-y-2">
                        <div className="flex justify-between text-xs">
                          <span className="text-gray-400">Weight</span>
                          <span className="text-purple-400">{Math.round(influence.weight * 100)}%</span>
                        </div>
                        <Slider
                          value={[influence.weight * 100]}
                          onValueChange={(val: number[]) => updateInfluence(idx, 'weight', val[0] / 100)}
                          max={100}
                          step={5}
                          className="w-full"
                        />
                      </div>
                    </div>
                  ))}

                  {influences.length < 3 && (
                    <Button
                      onClick={addInfluence}
                      variant="outline"
                      className="w-full border-dashed border-gray-700 text-gray-400 hover:text-white hover:border-purple-500"
                    >
                      + Add Influence
                    </Button>
                  )}
                </div>
              </ScrollArea>

              <Separator className="bg-gray-800" />

              {/* Target Mood & Genre */}
              <div className="space-y-3">
                <div>
                  <Label htmlFor="target-mood" className="text-xs text-gray-400">
                    Target Mood (Optional)
                  </Label>
                  <Input
                    id="target-mood"
                    placeholder="e.g., dark, uplifting, melancholic"
                    value={targetMood}
                    onChange={(e) => setTargetMood(e.target.value)}
                    className="bg-gray-800 border-gray-700 text-white mt-1"
                  />
                </div>
                <div>
                  <Label htmlFor="target-genre" className="text-xs text-gray-400">
                    Target Genre (Optional)
                  </Label>
                  <Input
                    id="target-genre"
                    placeholder="e.g., r&b, edm, pop"
                    value={targetGenre}
                    onChange={(e) => setTargetGenre(e.target.value)}
                    className="bg-gray-800 border-gray-700 text-white mt-1"
                  />
                </div>
              </div>

              {/* Apply Button */}
              <Button
                onClick={handleApplyInfluences}
                disabled={isApplyingInfluence || !selectedSourceId}
                className="w-full bg-purple-600 hover:bg-purple-700 text-white"
              >
                {isApplyingInfluence ? 'Applying...' : 'Apply Influences'}
              </Button>

              {/* Influence Response */}
              {influenceResponse && (
                <ScrollArea className="h-[400px] pr-4">
                  <div className="space-y-4">
                    {influenceResponse.hook_suggestions.length > 0 && (
                      <div className="p-3 bg-purple-900/20 border border-purple-700/30 rounded-lg">
                        <h4 className="text-sm font-semibold text-purple-400 mb-2">Hook Suggestions</h4>
                        <ul className="space-y-1">
                          {influenceResponse.hook_suggestions.map((suggestion, idx) => (
                            <li key={idx} className="text-xs text-gray-300">
                              • {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {influenceResponse.chorus_rewrite_ideas.length > 0 && (
                      <div className="p-3 bg-blue-900/20 border border-blue-700/30 rounded-lg">
                        <h4 className="text-sm font-semibold text-blue-400 mb-2">Chorus Ideas</h4>
                        <ul className="space-y-1">
                          {influenceResponse.chorus_rewrite_ideas.map((idea, idx) => (
                            <li key={idx} className="text-xs text-gray-300">
                              • {idea}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {influenceResponse.structure_suggestions.length > 0 && (
                      <div className="p-3 bg-yellow-900/20 border border-yellow-700/30 rounded-lg">
                        <h4 className="text-sm font-semibold text-yellow-400 mb-2">Structure Suggestions</h4>
                        <ul className="space-y-1">
                          {influenceResponse.structure_suggestions.map((suggestion, idx) => (
                            <li key={idx} className="text-xs text-gray-300">
                              • {suggestion}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {influenceResponse.instrumentation_ideas.length > 0 && (
                      <div className="p-3 bg-green-900/20 border border-green-700/30 rounded-lg">
                        <h4 className="text-sm font-semibold text-green-400 mb-2">Instrumentation</h4>
                        <ul className="space-y-1">
                          {influenceResponse.instrumentation_ideas.map((idea, idx) => (
                            <li key={idx} className="text-xs text-gray-300">
                              • {idea}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {influenceResponse.vocal_style_notes.length > 0 && (
                      <div className="p-3 bg-pink-900/20 border border-pink-700/30 rounded-lg">
                        <h4 className="text-sm font-semibold text-pink-400 mb-2">Vocal Style</h4>
                        <ul className="space-y-1">
                          {influenceResponse.vocal_style_notes.map((note, idx) => (
                            <li key={idx} className="text-xs text-gray-300">
                              • {note}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </ScrollArea>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
