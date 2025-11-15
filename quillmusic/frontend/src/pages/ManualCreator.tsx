import { Music2, Grid3x3, Layers, Sliders } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export default function ManualCreator() {
  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Manual Creator</h1>

        {/* Coming Soon Notice */}
        <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 border-blue-700 mb-8">
          <CardHeader>
            <CardTitle className="text-2xl">Coming Soon: DAW Lite</CardTitle>
            <CardDescription className="text-lg">
              A powerful DAW-style interface for detailed music creation
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-gray-300 mb-4">
              The Manual Creator will provide professional-grade tools for hands-on music production,
              combining the power of AI with traditional DAW workflows.
            </p>
          </CardContent>
        </Card>

        {/* Feature Preview */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-purple-600 rounded-lg">
                  <Layers className="w-5 h-5" />
                </div>
                <CardTitle>Multi-Track Timeline</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400 text-sm">
                Arrange multiple audio and MIDI tracks with precise timing control.
                Drag, drop, and edit sections with ease.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-blue-600 rounded-lg">
                  <Music2 className="w-5 h-5" />
                </div>
                <CardTitle>Piano Roll Editor</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400 text-sm">
                Create and edit MIDI sequences with a full-featured piano roll.
                Perfect for melodies, chords, and basslines.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-green-600 rounded-lg">
                  <Sliders className="w-5 h-5" />
                </div>
                <CardTitle>Mixer & Effects</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400 text-sm">
                Professional mixing console with EQ, compression, reverb, and more.
                Automate parameters over time.
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-pink-600 rounded-lg">
                  <Grid3x3 className="w-5 h-5" />
                </div>
                <CardTitle>AI-Assisted Workflow</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <p className="text-gray-400 text-sm">
                Leverage AI suggestions for chord progressions, drum patterns, and
                arrangement ideas while maintaining full control.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Mockup/Preview */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle>Interface Preview</CardTitle>
            <CardDescription>
              A glimpse of the planned DAW interface
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="bg-gray-950 rounded-lg border-2 border-gray-800 p-4">
              {/* Top Bar */}
              <div className="bg-gray-900 rounded-lg p-3 mb-4 flex items-center justify-between">
                <div className="flex gap-2">
                  <div className="w-20 h-8 bg-gray-800 rounded"></div>
                  <div className="w-20 h-8 bg-gray-800 rounded"></div>
                  <div className="w-20 h-8 bg-gray-800 rounded"></div>
                </div>
                <div className="flex gap-2">
                  <div className="w-32 h-8 bg-purple-600/30 rounded"></div>
                  <div className="w-24 h-8 bg-gray-800 rounded"></div>
                </div>
              </div>

              {/* Main Area */}
              <div className="grid grid-cols-12 gap-4">
                {/* Track List */}
                <div className="col-span-3 space-y-2">
                  <div className="bg-gray-900 rounded p-2 flex items-center gap-2">
                    <div className="w-4 h-4 bg-blue-600 rounded"></div>
                    <div className="text-xs text-gray-400">Drums</div>
                  </div>
                  <div className="bg-gray-900 rounded p-2 flex items-center gap-2">
                    <div className="w-4 h-4 bg-green-600 rounded"></div>
                    <div className="text-xs text-gray-400">Bass</div>
                  </div>
                  <div className="bg-gray-900 rounded p-2 flex items-center gap-2">
                    <div className="w-4 h-4 bg-purple-600 rounded"></div>
                    <div className="text-xs text-gray-400">Synth</div>
                  </div>
                  <div className="bg-gray-900 rounded p-2 flex items-center gap-2">
                    <div className="w-4 h-4 bg-pink-600 rounded"></div>
                    <div className="text-xs text-gray-400">Vocals</div>
                  </div>
                </div>

                {/* Timeline Grid */}
                <div className="col-span-9">
                  <div className="bg-gray-900 rounded p-4 h-48 relative">
                    {/* Grid lines */}
                    <div className="absolute inset-0 grid grid-cols-16 gap-px opacity-20">
                      {Array.from({ length: 16 }).map((_, i) => (
                        <div key={i} className="border-l border-gray-700"></div>
                      ))}
                    </div>

                    {/* Mock clips */}
                    <div className="relative space-y-2 pt-2">
                      <div className="h-8 w-1/2 bg-blue-600/50 rounded-sm"></div>
                      <div className="h-8 w-3/4 bg-green-600/50 rounded-sm"></div>
                      <div className="h-8 w-2/3 bg-purple-600/50 rounded-sm ml-8"></div>
                      <div className="h-8 w-1/3 bg-pink-600/50 rounded-sm ml-16"></div>
                    </div>

                    <div className="absolute bottom-4 left-4 text-xs text-gray-600">
                      Timeline • Piano Roll • Automation
                    </div>
                  </div>
                </div>
              </div>

              {/* Bottom Section */}
              <div className="mt-4 bg-gray-900 rounded-lg p-3">
                <div className="text-xs text-gray-600 text-center">
                  Mixer • Master Channel • Effects Rack
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
