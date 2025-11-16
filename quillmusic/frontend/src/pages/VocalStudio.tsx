import { useState } from 'react'
import { Mic2, Play, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/apiClient'

export default function VocalStudio() {
  // Form state
  const [text, setText] = useState<string>('')
  const [voiceId, setVoiceId] = useState<string>('')
  const [modelId, setModelId] = useState<string>('eleven_turbo_v2_5')

  // Preview state
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isGenerating, setIsGenerating] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    // Validation
    if (!text.trim()) {
      setError('Please enter some text or lyrics')
      return
    }

    if (!voiceId.trim()) {
      setError('Please enter a voice ID')
      return
    }

    setIsGenerating(true)
    setError(null)

    try {
      // Revoke previous audio URL if exists
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }

      // Call API
      const blob = await apiClient.vocals.preview({
        text: text.trim(),
        voiceId: voiceId.trim(),
        modelId: modelId || undefined,
      })

      // Create object URL from blob
      const url = URL.createObjectURL(blob)
      setAudioUrl(url)
    } catch (err) {
      console.error('Failed to generate vocal preview:', err)
      setError(err instanceof Error ? err.message : 'Failed to generate vocal preview')
    } finally {
      setIsGenerating(false)
    }
  }

  // Cleanup audio URL on unmount
  useState(() => {
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }
    }
  })

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-6">
          <h1 className="text-4xl font-bold">Vocal Studio</h1>
          <p className="text-gray-400 mt-2">
            Generate AI vocals using ElevenLabs text-to-speech
          </p>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Input Form */}
          <div className="col-span-7">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Vocal Setup</CardTitle>
                <CardDescription>Configure your vocal generation</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Text/Lyrics Input */}
                <div>
                  <Label htmlFor="text">Text / Lyrics</Label>
                  <Textarea
                    id="text"
                    placeholder="Enter the text or lyrics you want to convert to vocals..."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    className="bg-gray-800 border-gray-700 min-h-[200px] font-mono"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Maximum 5000 characters
                  </p>
                </div>

                {/* Voice ID Input */}
                <div>
                  <Label htmlFor="voiceId">Voice ID</Label>
                  <Input
                    id="voiceId"
                    placeholder="Paste your ElevenLabs voice ID here"
                    value={voiceId}
                    onChange={(e) => setVoiceId(e.target.value)}
                    className="bg-gray-800 border-gray-700 font-mono"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Find voice IDs in your{' '}
                    <a
                      href="https://elevenlabs.io/app/voice-library"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-purple-400 hover:text-purple-300 underline"
                    >
                      ElevenLabs dashboard
                    </a>
                  </p>
                </div>

                {/* Model Selection */}
                <div>
                  <Label htmlFor="model">Model</Label>
                  <Select value={modelId} onValueChange={setModelId}>
                    <SelectTrigger id="model" className="bg-gray-800 border-gray-700">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="eleven_turbo_v2_5">
                        Turbo v2.5 (Fast, High Quality)
                      </SelectItem>
                      <SelectItem value="eleven_multilingual_v2">
                        Multilingual v2 (Stable, Multi-Language)
                      </SelectItem>
                    </SelectContent>
                  </Select>
                  <p className="text-xs text-gray-500 mt-1">
                    Choose the ElevenLabs model for generation
                  </p>
                </div>

                {/* Error Display */}
                {error && (
                  <div className="p-3 bg-red-900/20 border border-red-700/50 rounded text-sm flex items-start gap-2">
                    <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-red-400" />
                    <span className="text-red-200">{error}</span>
                  </div>
                )}

                {/* Generate Button */}
                <Button
                  onClick={handleGenerate}
                  disabled={isGenerating}
                  className="w-full"
                  size="lg"
                >
                  <Mic2 className="w-4 h-4 mr-2" />
                  {isGenerating ? 'Generating...' : 'Generate Vocal Preview'}
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Preview */}
          <div className="col-span-5">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Preview</CardTitle>
                <CardDescription>Listen to your generated vocal</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {!audioUrl && !isGenerating && (
                  <div className="text-center py-12 text-gray-500">
                    <Mic2 className="w-12 h-12 mx-auto mb-3 opacity-50" />
                    <p>No vocal generated yet</p>
                    <p className="text-sm mt-1">
                      Enter text and voice ID, then click generate
                    </p>
                  </div>
                )}

                {isGenerating && (
                  <div className="text-center py-12 text-gray-400">
                    <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mb-3"></div>
                    <p>Generating vocal...</p>
                    <p className="text-sm mt-1">This may take a few seconds</p>
                  </div>
                )}

                {audioUrl && !isGenerating && (
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Badge className="bg-green-600">Ready</Badge>
                      <span className="text-sm text-gray-400">Vocal generated successfully</span>
                    </div>

                    {/* Audio Player */}
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <audio
                        controls
                        src={audioUrl}
                        className="w-full"
                        style={{ height: '40px' }}
                      >
                        Your browser does not support the audio element.
                      </audio>
                    </div>

                    {/* Info */}
                    <div className="text-xs text-gray-500 text-center">
                      <p>Powered by ElevenLabs</p>
                    </div>
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
