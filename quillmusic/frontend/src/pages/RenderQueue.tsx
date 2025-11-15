import { useState } from 'react'
import { toast } from 'sonner'
import { RefreshCw, CheckCircle2, XCircle, Clock, Play } from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/apiClient'
import type { RenderJobStatus } from '@/types'

export default function RenderQueue() {
  const [jobId, setJobId] = useState('')
  const [jobs, setJobs] = useState<RenderJobStatus[]>([])
  const [isChecking, setIsChecking] = useState(false)

  const handleCheckStatus = async () => {
    if (!jobId.trim()) {
      toast.error('Please enter a job ID')
      return
    }

    setIsChecking(true)
    try {
      const result = await apiClient.getRenderJob(jobId.trim())

      // Add or update job in the list
      setJobs((prev) => {
        const existing = prev.findIndex((j) => j.job_id === result.job_id)
        if (existing >= 0) {
          const updated = [...prev]
          updated[existing] = result
          return updated
        }
        return [result, ...prev]
      })

      toast.success('Job status retrieved')
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Failed to get job status')
    } finally {
      setIsChecking(false)
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'ready':
        return (
          <Badge className="bg-green-600">
            <CheckCircle2 className="w-3 h-3 mr-1" />
            Ready
          </Badge>
        )
      case 'processing':
        return (
          <Badge className="bg-blue-600">
            <RefreshCw className="w-3 h-3 mr-1 animate-spin" />
            Processing
          </Badge>
        )
      case 'queued':
        return (
          <Badge className="bg-yellow-600">
            <Clock className="w-3 h-3 mr-1" />
            Queued
          </Badge>
        )
      case 'failed':
        return (
          <Badge className="bg-red-600">
            <XCircle className="w-3 h-3 mr-1" />
            Failed
          </Badge>
        )
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const getRenderTypeColor = (type: string) => {
    switch (type) {
      case 'full_mix':
        return 'bg-purple-600/20 text-purple-300 border-purple-600'
      case 'instrumental':
        return 'bg-blue-600/20 text-blue-300 border-blue-600'
      case 'vocals':
        return 'bg-pink-600/20 text-pink-300 border-pink-600'
      default:
        return 'bg-gray-600/20 text-gray-300 border-gray-600'
    }
  }

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Render Queue</h1>

        {/* Check Status Card */}
        <Card className="bg-gray-900 border-gray-800 mb-8">
          <CardHeader>
            <CardTitle>Check Render Status</CardTitle>
            <CardDescription>
              Enter a job ID to check its status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-4">
              <Input
                placeholder="job_abc123..."
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleCheckStatus()}
                className="bg-gray-950 border-gray-700"
              />
              <Button
                onClick={handleCheckStatus}
                disabled={isChecking}
                className="bg-purple-600 hover:bg-purple-700"
              >
                {isChecking ? (
                  <>
                    <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                    Checking...
                  </>
                ) : (
                  'Check Status'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Jobs List */}
        <Card className="bg-gray-900 border-gray-800">
          <CardHeader>
            <CardTitle>Render Jobs</CardTitle>
            <CardDescription>
              Recent and checked render jobs
            </CardDescription>
          </CardHeader>
          <CardContent>
            {jobs.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No render jobs yet. Check a job ID or create a render from the AI Song Builder.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div
                    key={job.job_id}
                    className="p-4 bg-gray-950 rounded-lg border border-gray-800"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-mono text-sm text-gray-400">
                            {job.job_id}
                          </span>
                          {getStatusBadge(job.status)}
                        </div>
                        <div className="flex items-center gap-2 text-sm text-gray-400">
                          <span>Song: {job.song_id}</span>
                          <span>•</span>
                          <Badge
                            variant="outline"
                            className={getRenderTypeColor(job.render_type)}
                          >
                            {job.render_type}
                          </Badge>
                        </div>
                      </div>

                      {job.status === 'ready' && job.audio_url && (
                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => {
                            toast.info('Audio URL', {
                              description: job.audio_url,
                            })
                          }}
                        >
                          <Play className="w-4 h-4 mr-2" />
                          Play
                        </Button>
                      )}
                    </div>

                    {job.audio_url && (
                      <div className="text-sm">
                        <span className="text-gray-500">Audio URL: </span>
                        <span className="text-blue-400 font-mono">{job.audio_url}</span>
                      </div>
                    )}

                    {job.error && (
                      <div className="mt-2 p-2 bg-red-900/20 border border-red-800 rounded text-sm text-red-400">
                        Error: {job.error}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
