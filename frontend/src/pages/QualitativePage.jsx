import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { qualApi } from '../api/client'
import toast from 'react-hot-toast'
import { Upload, FileAudio, FileVideo, CheckCircle, Loader, AlertCircle } from 'lucide-react'

const STATUS_ICONS = {
  uploaded:    <Loader size={14} className="text-blue-500 animate-spin" />,
  processing:  <Loader size={14} className="text-amber-500 animate-spin" />,
  transcribed: <Loader size={14} className="text-purple-500 animate-spin" />,
  analyzed:    <CheckCircle size={14} className="text-green-500" />,
  failed:      <AlertCircle size={14} className="text-red-500" />,
}

export default function QualitativePage() {
  const queryClient = useQueryClient()
  const [selectedFile, setSelectedFile] = useState(null)
  const [language, setLanguage] = useState('ar')
  const [activeId, setActiveId] = useState(null)

  const { data: files = [] } = useQuery({
    queryKey: ['qual-files'],
    queryFn: () => qualApi.files().then(r => r.data),
    refetchInterval: 8000, // poll every 8s for status updates
  })

  const { data: analysis } = useQuery({
    queryKey: ['qual-analysis', activeId],
    queryFn: () => qualApi.analysis(activeId).then(r => r.data),
    enabled: !!activeId,
  })

  const { data: transcript } = useQuery({
    queryKey: ['qual-transcript', activeId],
    queryFn: () => qualApi.transcript(activeId).then(r => r.data),
    enabled: !!activeId,
  })

  const uploadMutation = useMutation({
    mutationFn: () => {
      const fd = new FormData()
      fd.append('file', selectedFile)
      fd.append('language', language)
      return qualApi.upload(fd)
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['qual-files'])
      setSelectedFile(null)
      toast.success('Upload successful — transcription starting...')
    },
    onError: () => toast.error('Upload failed'),
  })

  return (
    <div className="p-8">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Qualitative Analytics</h2>
        <p className="text-gray-500 text-sm">Upload audio/video → AI transcription + Arabic sentiment analysis</p>
      </div>

      {/* Upload panel */}
      <div className="bg-white rounded-xl border border-gray-100 p-6 mb-6">
        <h3 className="font-semibold text-gray-900 mb-4">Upload Media File</h3>
        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">File (MP4, MP3, WAV, M4A)</label>
            <input
              type="file"
              accept="audio/*,video/*"
              onChange={e => setSelectedFile(e.target.files[0])}
              className="text-sm text-gray-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:bg-gray-100 file:text-gray-700 file:text-xs cursor-pointer"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Language</label>
            <select
              value={language}
              onChange={e => setLanguage(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-1.5 text-sm"
            >
              <option value="ar">Arabic (العربية)</option>
              <option value="en">English</option>
              <option value="fr">French</option>
            </select>
          </div>
          <button
            onClick={() => uploadMutation.mutate()}
            disabled={!selectedFile || uploadMutation.isPending}
            className="flex items-center gap-2 bg-[#1E3A5F] text-white px-4 py-2 rounded-lg text-sm font-medium disabled:opacity-50 hover:bg-[#162d4a] transition-colors"
          >
            <Upload size={15} />
            {uploadMutation.isPending ? 'Uploading...' : 'Upload & Analyze'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* File list */}
        <div className="bg-white rounded-xl border border-gray-100 p-5">
          <h3 className="font-semibold text-gray-900 mb-3 text-sm">Media Files</h3>
          {files.length === 0 ? (
            <p className="text-gray-400 text-xs">No files uploaded yet.</p>
          ) : files.map(f => (
            <div
              key={f.id}
              onClick={() => setActiveId(f.id)}
              className={`flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-colors mb-1 ${
                activeId === f.id ? 'bg-blue-50' : 'hover:bg-gray-50'
              }`}
            >
              {f.file_type === 'audio'
                ? <FileAudio size={16} className="text-purple-500 shrink-0" />
                : <FileVideo size={16} className="text-blue-500 shrink-0" />
              }
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium text-gray-800 truncate">{f.file_name}</p>
                <p className="text-xs text-gray-400 capitalize">{f.status}</p>
              </div>
              {STATUS_ICONS[f.status] || null}
            </div>
          ))}
        </div>

        {/* Analysis panel */}
        <div className="lg:col-span-2 space-y-4">
          {analysis && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Sentiment Analysis</h3>
              <div className="flex items-center gap-3 mb-3">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  analysis.overall_sentiment === 'positive' ? 'bg-green-100 text-green-700' :
                  analysis.overall_sentiment === 'negative' ? 'bg-red-100 text-red-700' :
                                                               'bg-gray-100 text-gray-600'
                }`}>
                  {analysis.overall_sentiment}
                </span>
                <span className="text-sm text-gray-500">
                  Score: {(analysis.sentiment_score * 100).toFixed(0)}%
                </span>
              </div>
              {analysis.summary && (
                <p className="text-sm text-gray-600 mb-3">{analysis.summary}</p>
              )}
              {analysis.keywords?.length > 0 && (
                <div>
                  <p className="text-xs font-medium text-gray-500 mb-2">Top Keywords</p>
                  <div className="flex flex-wrap gap-1.5">
                    {analysis.keywords.slice(0, 12).map((k, i) => (
                      <span key={i} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                        {k.word} ({k.count})
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {transcript && (
            <div className="bg-white rounded-xl border border-gray-100 p-5">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">
                Transcript
                {transcript.language_detected && (
                  <span className="ml-2 text-xs font-normal text-gray-400">
                    ({transcript.language_detected})
                  </span>
                )}
              </h3>
              <div
                className="text-sm text-gray-700 leading-relaxed max-h-60 overflow-y-auto"
                dir={transcript.language_detected === 'ar' ? 'rtl' : 'ltr'}
              >
                {transcript.full_text || 'Transcript not available yet.'}
              </div>
            </div>
          )}

          {!activeId && (
            <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
              <p className="text-gray-400 text-sm">Select a file to view analysis</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
