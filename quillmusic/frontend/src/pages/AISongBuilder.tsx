import { useState } from 'react'
import { toast } from 'sonner'
import { Loader2, Music, Send } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/apiClient'
import type { SongBlueprintRequest, SongBlueprintResponse } from '@/types'

const GENRES = ['Pop', 'Hip Hop', 'EDM', 'Lo-fi', 'Trap', 'Ambient', 'Rock']
const MOODS = ['Dark', 'Emotional', 'Energetic', 'Chill', 'Uplifting']
const DURATIONS = [
  { label: '30 seconds', value: 30 },
  { label: '1 minute', value: 60 },
  { label: '3 minutes', value: 180 },
  { label: '5 minutes', value: 300 },
  { label: '10 minutes', value: 600 },
]

export default function AISongBuilder() {
  const [formData, setFormData] = useState<Partial<SongBlueprintRequest>>({
    prompt: '',
    genre: 'Pop',
    mood: 'Energetic',
    duration_seconds: 180,
  })

  const [blueprint, setBlueprint] = useState<SongBlueprintResponse | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isRendering, setIsRendering] = useState(false)

  const handleGenerate = async () => {
    if (!formData.prompt || formData.prompt.length < 10) {
      toast.error('Please enter a more detailed prompt (at least 10 characters)')
      return
    }

    if (!formData.genre || !formData.mood) {
      toast.error('Please select genre and mood')
      return
    }

    setIsGenerating(true)
    setBlueprint(null)

    try {
      const result = await apiClient.createSongBlueprint(formData as SongBlueprintRequest)
      setBlueprint(result)
      toast.success('Song blueprint generated successfully!')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to generate blueprint')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleRender = async () => {
    if (!blueprint) return

    setIsRendering(true)
    try {
      const result = await apiClient.createRenderJob({
        song_id: blueprint.song_id,
        render_type: 'full_mix',
      })

      toast.success('Render job created!', {
        description: `Job ID: ${result.job_id}`,
      })

      // In a real app, you'd navigate to render queue or poll for status
      if (result.audio_url) {
        toast.success('Audio ready!', {
          description: result.audio_url,
        })
      }
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to create render job')
    } finally {
      setIsRendering(false)
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">AI Song Builder</h1>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column: Song Setup */}
          <div>
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Song Setup</CardTitle>
                <CardDescription>
                  Describe your song and configure parameters
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="prompt">Song Prompt *</Label>
                  <Textarea
                    id="prompt"
                    placeholder="Describe your song... (e.g., 'A dreamy synthwave track about late night drives through neon-lit cities')"
                    value={formData.prompt}
                    onChange={(e) =>
                      setFormData({ ...formData, prompt: e.target.value })
                    }
                    rows={4}
                    className="bg-gray-950 border-gray-700"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="genre">Genre *</Label>
                    <Select
                      value={formData.genre}
                      onValueChange={(value) =>
                        setFormData({ ...formData, genre: value })
                      }
                    >
                      <SelectTrigger id="genre" className="bg-gray-950 border-gray-700">
                        <SelectValue placeholder="Select genre" />
                      </SelectTrigger>
                      <SelectContent>
                        {GENRES.map((genre) => (
                          <SelectItem key={genre} value={genre}>
                            {genre}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="mood">Mood *</Label>
                    <Select
                      value={formData.mood}
                      onValueChange={(value) =>
                        setFormData({ ...formData, mood: value })
                      }
                    >
                      <SelectTrigger id="mood" className="bg-gray-950 border-gray-700">
                        <SelectValue placeholder="Select mood" />
                      </SelectTrigger>
                      <SelectContent>
                        {MOODS.map((mood) => (
                          <SelectItem key={mood} value={mood}>
                            {mood}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="bpm">BPM</Label>
                    <Input
                      id="bpm"
                      type="number"
                      placeholder="Auto"
                      min="40"
                      max="200"
                      value={formData.bpm || ''}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          bpm: e.target.value ? parseInt(e.target.value) : undefined,
                        })
                      }
                      className="bg-gray-950 border-gray-700"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="key">Key</Label>
                    <Input
                      id="key"
                      placeholder="Auto"
                      value={formData.key || ''}
                      onChange={(e) =>
                        setFormData({ ...formData, key: e.target.value || undefined })
                      }
                      className="bg-gray-950 border-gray-700"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="duration">Duration</Label>
                    <Select
                      value={formData.duration_seconds?.toString()}
                      onValueChange={(value) =>
                        setFormData({ ...formData, duration_seconds: parseInt(value) })
                      }
                    >
                      <SelectTrigger id="duration" className="bg-gray-950 border-gray-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {DURATIONS.map((duration) => (
                          <SelectItem key={duration.value} value={duration.value.toString()}>
                            {duration.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="reference">Reference (Optional)</Label>
                  <Textarea
                    id="reference"
                    placeholder="Additional inspiration or reference..."
                    value={formData.reference_text || ''}
                    onChange={(e) =>
                      setFormData({ ...formData, reference_text: e.target.value || undefined })
                    }
                    rows={2}
                    className="bg-gray-950 border-gray-700"
                  />
                </div>

                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full bg-purple-600 hover:bg-purple-700"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Music className="w-4 h-4 mr-2" />
                      Generate Blueprint
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column: Blueprint & Lyrics */}
          <div>
            {blueprint ? (
              <div className="space-y-6">
                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>{blueprint.title}</CardTitle>
                    <CardDescription>
                      {blueprint.genre} • {blueprint.mood} • {blueprint.bpm} BPM • {blueprint.key}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h3 className="text-sm font-semibold mb-3 text-gray-400">STRUCTURE</h3>
                      <div className="space-y-2">
                        {blueprint.sections.map((section) => (
                          <div
                            key={section.id}
                            className="flex items-center justify-between p-3 bg-gray-950 rounded-lg border border-gray-800"
                          >
                            <div className="flex items-center gap-3">
                              <Badge variant="secondary">{section.type}</Badge>
                              <div>
                                <div className="font-medium">{section.name}</div>
                                <div className="text-xs text-gray-500">
                                  {section.bars} bars • {section.instruments.join(', ')}
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm font-semibold mb-3 text-gray-400">VOCAL STYLE</h3>
                      <div className="p-3 bg-gray-950 rounded-lg border border-gray-800">
                        <div className="flex gap-2">
                          <Badge>{blueprint.vocal_style.gender}</Badge>
                          <Badge variant="outline">{blueprint.vocal_style.tone}</Badge>
                          <Badge variant="outline">{blueprint.vocal_style.energy} energy</Badge>
                        </div>
                      </div>
                    </div>

                    {blueprint.notes && (
                      <div>
                        <h3 className="text-sm font-semibold mb-3 text-gray-400">NOTES</h3>
                        <div className="p-3 bg-gray-950 rounded-lg border border-gray-800 text-sm text-gray-300 whitespace-pre-line">
                          {blueprint.notes}
                        </div>
                      </div>
                    )}

                    <Button
                      onClick={handleRender}
                      disabled={isRendering}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      {isRendering ? (
                        <>
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                          Creating Render...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Send to Render Engine
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>

                <Card className="bg-gray-900 border-gray-800">
                  <CardHeader>
                    <CardTitle>Lyrics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      {blueprint.sections.map((section) => {
                        const lyrics = blueprint.lyrics[section.id]
                        if (!lyrics) return null

                        return (
                          <div key={section.id}>
                            <h4 className="text-sm font-semibold mb-2 text-purple-400">
                              [{section.name.toUpperCase()}]
                            </h4>
                            <p className="text-gray-300 whitespace-pre-line text-sm">
                              {lyrics}
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            ) : (
              <Card className="bg-gray-900 border-gray-800 h-full">
                <CardContent className="flex items-center justify-center h-full min-h-[500px]">
                  <div className="text-center text-gray-500">
                    <Music className="w-16 h-16 mx-auto mb-4 opacity-50" />
                    <p>Generate a blueprint to see the song structure and lyrics</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
