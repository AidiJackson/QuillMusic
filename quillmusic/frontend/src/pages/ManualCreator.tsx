import { useEffect, useState } from 'react'
import { Plus, Music, Save } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { apiClient } from '@/lib/apiClient'
import type {
  ManualProject,
  ManualProjectDetail,
  Track,
  Pattern,
  Note,
  InstrumentType,
  NoteCreate,
} from '@/types'

// Instrument colors for visual differentiation
const INSTRUMENT_COLORS: Record<InstrumentType, string> = {
  drums: 'bg-blue-600',
  bass: 'bg-green-600',
  chords: 'bg-purple-600',
  lead: 'bg-pink-600',
  fx: 'bg-yellow-600',
  vocal: 'bg-red-600',
}

// Simple pitch mapping for demo (C to B)
const PITCH_NOTES = [
  { name: 'C', pitch: 60 },
  { name: 'D', pitch: 62 },
  { name: 'E', pitch: 64 },
  { name: 'F', pitch: 65 },
  { name: 'G', pitch: 67 },
  { name: 'A', pitch: 69 },
  { name: 'B', pitch: 71 },
]

const NUM_STEPS = 16 // Steps per pattern

export default function ManualCreator() {
  const [projects, setProjects] = useState<ManualProject[]>([])
  const [selectedProjectId, setSelectedProjectId] = useState<string | null>(null)
  const [projectDetail, setProjectDetail] = useState<ManualProjectDetail | null>(null)
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null)
  const [noteGrid, setNoteGrid] = useState<Map<string, Note>>(new Map())
  const [isNewProjectOpen, setIsNewProjectOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // New project form state
  const [newProjectForm, setNewProjectForm] = useState({
    name: '',
    tempo_bpm: 120,
    time_signature: '4/4',
    key: 'C',
  })

  // Load projects on mount
  useEffect(() => {
    loadProjects()
  }, [])

  // Load project detail when selected
  useEffect(() => {
    if (selectedProjectId) {
      loadProjectDetail(selectedProjectId)
    }
  }, [selectedProjectId])

  // Load notes when pattern is selected
  useEffect(() => {
    if (selectedPattern) {
      loadPatternNotes(selectedPattern.id)
    }
  }, [selectedPattern])

  const loadProjects = async () => {
    try {
      const data = await apiClient.manual.listProjects()
      setProjects(data)
    } catch (error) {
      console.error('Failed to load projects:', error)
    }
  }

  const loadProjectDetail = async (projectId: string) => {
    setIsLoading(true)
    try {
      const data = await apiClient.manual.getProjectDetail(projectId)
      setProjectDetail(data)
    } catch (error) {
      console.error('Failed to load project detail:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const loadPatternNotes = async (patternId: string) => {
    try {
      const notes = await apiClient.manual.getPatternNotes(patternId)
      const noteMap = new Map<string, Note>()
      notes.forEach(note => {
        const key = `${note.step_index}-${note.pitch}`
        noteMap.set(key, note)
      })
      setNoteGrid(noteMap)
    } catch (error) {
      console.error('Failed to load notes:', error)
    }
  }

  const handleCreateProject = async () => {
    try {
      const project = await apiClient.manual.createProject(newProjectForm)
      setProjects([project, ...projects])
      setSelectedProjectId(project.id)
      setIsNewProjectOpen(false)
      setNewProjectForm({ name: '', tempo_bpm: 120, time_signature: '4/4', key: 'C' })
    } catch (error) {
      console.error('Failed to create project:', error)
    }
  }

  const handleAddTrack = async (instrumentType: InstrumentType) => {
    if (!selectedProjectId || !projectDetail) return

    const channelIndex = projectDetail.tracks.length
    try {
      await apiClient.manual.createTrack(selectedProjectId, {
        name: `${instrumentType} ${channelIndex + 1}`,
        instrument_type: instrumentType,
        channel_index: channelIndex,
      })
      loadProjectDetail(selectedProjectId)
    } catch (error) {
      console.error('Failed to add track:', error)
    }
  }

  const handleCellClick = async (track: Track, bar: number) => {
    if (!projectDetail) return

    // Check if pattern exists at this position
    const existingPattern = projectDetail.patterns.find(
      p => p.track_id === track.id && p.start_bar === bar
    )

    if (existingPattern) {
      // Select existing pattern
      setSelectedPattern(existingPattern)
    } else {
      // Create new pattern
      try {
        const newPattern = await apiClient.manual.createPattern(track.id, {
          name: `Pattern ${bar + 1}`,
          length_bars: 2,
          start_bar: bar,
        })
        loadProjectDetail(selectedProjectId!)
        setSelectedPattern(newPattern)
      } catch (error) {
        console.error('Failed to create pattern:', error)
      }
    }
  }

  const toggleNote = (stepIndex: number, pitch: number) => {
    const key = `${stepIndex}-${pitch}`
    const newGrid = new Map(noteGrid)

    if (newGrid.has(key)) {
      newGrid.delete(key)
    } else {
      // Create a temporary note for display
      newGrid.set(key, {
        id: 'temp',
        pattern_id: selectedPattern!.id,
        step_index: stepIndex,
        pitch,
        velocity: 100,
      })
    }

    setNoteGrid(newGrid)
  }

  const handleSaveNotes = async () => {
    if (!selectedPattern) return

    try {
      const notes: NoteCreate[] = Array.from(noteGrid.values()).map(note => ({
        pattern_id: selectedPattern.id,
        step_index: note.step_index,
        pitch: note.pitch,
        velocity: note.velocity,
      }))

      await apiClient.manual.replacePatternNotes(selectedPattern.id, notes)
      loadPatternNotes(selectedPattern.id) // Reload to get proper IDs
    } catch (error) {
      console.error('Failed to save notes:', error)
    }
  }

  const getPatternAtCell = (trackId: string, bar: number): Pattern | undefined => {
    if (!projectDetail) return undefined
    return projectDetail.patterns.find(
      p => p.track_id === trackId && bar >= p.start_bar && bar < p.start_bar + p.length_bars
    )
  }

  // Empty state if no projects
  if (projects.length === 0 && !isLoading) {
    return (
      <div className="p-8">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-4xl font-bold mb-8">Manual Creator</h1>
          <Card className="bg-gradient-to-br from-purple-900/30 to-blue-900/30 border-purple-700">
            <CardHeader>
              <CardTitle className="text-2xl">No Projects Yet</CardTitle>
              <CardDescription className="text-lg">
                Create your first manual project to start building music
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button onClick={() => setIsNewProjectOpen(true)} size="lg">
                <Plus className="w-4 h-4 mr-2" />
                Create Project
              </Button>
            </CardContent>
          </Card>

          {/* New Project Dialog */}
          <Dialog open={isNewProjectOpen} onOpenChange={setIsNewProjectOpen}>
            <DialogContent className="bg-gray-900 border-gray-700">
              <DialogHeader>
                <DialogTitle>Create New Project</DialogTitle>
                <DialogDescription>
                  Set up your manual music project
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <div>
                  <Label htmlFor="name">Project Name</Label>
                  <Input
                    id="name"
                    value={newProjectForm.name}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, name: e.target.value })}
                    placeholder="My Awesome Track"
                  />
                </div>
                <div>
                  <Label htmlFor="tempo">Tempo (BPM)</Label>
                  <Input
                    id="tempo"
                    type="number"
                    value={newProjectForm.tempo_bpm}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, tempo_bpm: parseInt(e.target.value) })}
                  />
                </div>
                <div>
                  <Label htmlFor="key">Key</Label>
                  <Input
                    id="key"
                    value={newProjectForm.key}
                    onChange={(e) => setNewProjectForm({ ...newProjectForm, key: e.target.value })}
                    placeholder="C, Am, etc."
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsNewProjectOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateProject}>
                  Create
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>
    )
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-4xl font-bold">Manual Creator</h1>
          <Button onClick={() => setIsNewProjectOpen(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Project
          </Button>
        </div>

        <div className="grid grid-cols-12 gap-6">
          {/* Left Column - Project Controls */}
          <div className="col-span-3 space-y-4">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-lg">Project</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <Label>Select Project</Label>
                  <Select value={selectedProjectId || ''} onValueChange={setSelectedProjectId}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose project..." />
                    </SelectTrigger>
                    <SelectContent>
                      {projects.map(project => (
                        <SelectItem key={project.id} value={project.id}>
                          {project.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {projectDetail && (
                  <>
                    <div className="pt-2 border-t border-gray-800">
                      <div className="flex items-center gap-2 text-sm">
                        <Music className="w-4 h-4" />
                        <span>{projectDetail.project.tempo_bpm} BPM</span>
                      </div>
                      <div className="text-sm text-gray-400 mt-1">
                        {projectDetail.project.key || 'No key set'}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-gray-800">
                      <Label className="mb-2 block">Add Track</Label>
                      <div className="grid grid-cols-2 gap-2">
                        {(['drums', 'bass', 'chords', 'lead', 'fx', 'vocal'] as InstrumentType[]).map(type => (
                          <Button
                            key={type}
                            size="sm"
                            variant="outline"
                            onClick={() => handleAddTrack(type)}
                            className="text-xs"
                          >
                            {type}
                          </Button>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Middle Column - Pattern Grid */}
          <div className="col-span-6">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Timeline Grid</CardTitle>
                <CardDescription>
                  Click cells to create/edit patterns
                </CardDescription>
              </CardHeader>
              <CardContent>
                {projectDetail && projectDetail.tracks.length > 0 ? (
                  <div className="space-y-2">
                    {projectDetail.tracks.map(track => (
                      <div key={track.id} className="flex gap-1">
                        {/* Track label */}
                        <div className={`w-24 px-2 py-2 rounded text-xs font-medium flex items-center ${INSTRUMENT_COLORS[track.instrument_type]}`}>
                          {track.name}
                        </div>

                        {/* Bar cells */}
                        <div className="flex-1 grid grid-cols-16 gap-1">
                          {Array.from({ length: 16 }).map((_, barIndex) => {
                            const pattern = getPatternAtCell(track.id, barIndex)
                            const isStart = pattern && pattern.start_bar === barIndex

                            return (
                              <div
                                key={barIndex}
                                onClick={() => handleCellClick(track, barIndex)}
                                className={`
                                  h-10 rounded cursor-pointer border transition-colors
                                  ${pattern
                                    ? `${INSTRUMENT_COLORS[track.instrument_type]} border-gray-700 hover:opacity-80`
                                    : 'bg-gray-800 border-gray-700 hover:bg-gray-750'
                                  }
                                  ${selectedPattern?.id === pattern?.id ? 'ring-2 ring-white' : ''}
                                `}
                                title={pattern ? pattern.name : `Bar ${barIndex + 1}`}
                              >
                                {isStart && pattern && (
                                  <div className="text-xs px-1 truncate">
                                    {pattern.name}
                                  </div>
                                )}
                              </div>
                            )
                          })}
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-12 text-gray-500">
                    {projectDetail ? 'Add a track to get started' : 'Select a project'}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Pattern Editor */}
          <div className="col-span-3">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle className="text-lg">Pattern Editor</CardTitle>
              </CardHeader>
              <CardContent>
                {selectedPattern ? (
                  <div className="space-y-4">
                    <div>
                      <div className="text-sm font-medium mb-1">{selectedPattern.name}</div>
                      <div className="text-xs text-gray-400">
                        {selectedPattern.length_bars} bars • Bar {selectedPattern.start_bar + 1}
                      </div>
                    </div>

                    {/* Note Grid */}
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <Label className="text-xs">Note Grid</Label>
                        <Button size="sm" onClick={handleSaveNotes}>
                          <Save className="w-3 h-3 mr-1" />
                          Save
                        </Button>
                      </div>

                      <div className="border border-gray-700 rounded">
                        {PITCH_NOTES.slice().reverse().map(({ name, pitch }) => (
                          <div key={pitch} className="flex border-b border-gray-800 last:border-b-0">
                            <div className="w-8 bg-gray-800 text-xs flex items-center justify-center border-r border-gray-700">
                              {name}
                            </div>
                            <div className="flex-1 grid grid-cols-16 gap-px bg-gray-800">
                              {Array.from({ length: NUM_STEPS }).map((_, stepIndex) => {
                                const key = `${stepIndex}-${pitch}`
                                const hasNote = noteGrid.has(key)

                                return (
                                  <div
                                    key={stepIndex}
                                    onClick={() => toggleNote(stepIndex, pitch)}
                                    className={`
                                      aspect-square cursor-pointer transition-colors
                                      ${hasNote ? 'bg-purple-600 hover:bg-purple-500' : 'bg-gray-900 hover:bg-gray-700'}
                                      ${stepIndex % 4 === 0 ? 'border-l-2 border-gray-700' : ''}
                                    `}
                                  />
                                )
                              })}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500 text-sm">
                    Select or create a pattern to edit notes
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>

      {/* New Project Dialog */}
      <Dialog open={isNewProjectOpen} onOpenChange={setIsNewProjectOpen}>
        <DialogContent className="bg-gray-900 border-gray-700">
          <DialogHeader>
            <DialogTitle>Create New Project</DialogTitle>
            <DialogDescription>
              Set up your manual music project
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="name">Project Name</Label>
              <Input
                id="name"
                value={newProjectForm.name}
                onChange={(e) => setNewProjectForm({ ...newProjectForm, name: e.target.value })}
                placeholder="My Awesome Track"
                className="bg-gray-800 border-gray-700"
              />
            </div>
            <div>
              <Label htmlFor="tempo">Tempo (BPM)</Label>
              <Input
                id="tempo"
                type="number"
                value={newProjectForm.tempo_bpm}
                onChange={(e) => setNewProjectForm({ ...newProjectForm, tempo_bpm: parseInt(e.target.value) })}
                className="bg-gray-800 border-gray-700"
              />
            </div>
            <div>
              <Label htmlFor="key">Key</Label>
              <Input
                id="key"
                value={newProjectForm.key}
                onChange={(e) => setNewProjectForm({ ...newProjectForm, key: e.target.value })}
                placeholder="C, Am, etc."
                className="bg-gray-800 border-gray-700"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsNewProjectOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateProject}>
              Create
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
