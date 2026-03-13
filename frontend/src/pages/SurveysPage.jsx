import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { surveysApi } from '../api/client'
import toast from 'react-hot-toast'
import { Plus, Eye, Trash2, Send } from 'lucide-react'

export default function SurveysPage() {
  const navigate      = useNavigate()
  const queryClient   = useQueryClient()
  const [showCreate, setShowCreate] = useState(false)
  const [form, setForm] = useState({ title: '', title_ar: '', channel: 'email' })

  const { data: surveys = [], isLoading } = useQuery({
    queryKey: ['surveys'],
    queryFn: () => surveysApi.list().then(r => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (data) => surveysApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['surveys'])
      setShowCreate(false)
      setForm({ title: '', title_ar: '', channel: 'email' })
      toast.success('Survey created!')
    },
    onError: (e) => toast.error(e.response?.data?.detail || 'Failed to create'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id) => surveysApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['surveys'])
      toast.success('Survey deleted')
    },
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">CX Surveys</h2>
          <p className="text-gray-500 text-sm">{surveys.length} surveys total</p>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="flex items-center gap-2 bg-[#1E3A5F] text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-[#162d4a] transition-colors"
        >
          <Plus size={16} /> New Survey
        </button>
      </div>

      {/* Create form modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl w-full max-w-lg p-6">
            <h3 className="font-bold text-gray-900 mb-4">Create New Survey</h3>
            <div className="space-y-3">
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                placeholder="Survey title (English)"
                value={form.title}
                onChange={e => setForm({...form, title: e.target.value})}
              />
              <input
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-right"
                placeholder="عنوان الاستبيان (عربي)"
                dir="rtl"
                value={form.title_ar}
                onChange={e => setForm({...form, title_ar: e.target.value})}
              />
              <select
                className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm"
                value={form.channel}
                onChange={e => setForm({...form, channel: e.target.value})}
              >
                <option value="email">Email</option>
                <option value="sms">SMS</option>
                <option value="whatsapp">WhatsApp</option>
                <option value="web">Web Link</option>
                <option value="qr">QR Code</option>
              </select>
            </div>
            <div className="flex gap-3 mt-5">
              <button
                onClick={() => createMutation.mutate(form)}
                disabled={!form.title || createMutation.isPending}
                className="flex-1 bg-[#1E3A5F] text-white rounded-lg py-2 text-sm font-medium disabled:opacity-50"
              >
                {createMutation.isPending ? 'Creating...' : 'Create Survey'}
              </button>
              <button
                onClick={() => setShowCreate(false)}
                className="flex-1 border border-gray-200 rounded-lg py-2 text-sm text-gray-600 hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Surveys table */}
      <div className="bg-white rounded-xl border border-gray-100 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-400">Loading surveys...</div>
        ) : surveys.length === 0 ? (
          <div className="p-8 text-center text-gray-400">No surveys yet. Create your first one!</div>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-5 py-3 text-gray-600 font-medium">Title</th>
                <th className="text-left px-5 py-3 text-gray-600 font-medium">Channel</th>
                <th className="text-left px-5 py-3 text-gray-600 font-medium">Status</th>
                <th className="text-left px-5 py-3 text-gray-600 font-medium">Created</th>
                <th className="px-5 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {surveys.map(s => (
                <tr key={s.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-5 py-3.5 font-medium text-gray-900 max-w-xs truncate">{s.title}</td>
                  <td className="px-5 py-3.5 text-gray-500 capitalize">{s.channel}</td>
                  <td className="px-5 py-3.5">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      s.status === 'active'   ? 'bg-green-100 text-green-700' :
                      s.status === 'draft'    ? 'bg-amber-100 text-amber-700' :
                      s.status === 'paused'   ? 'bg-blue-100 text-blue-700'   :
                                                'bg-gray-100 text-gray-600'
                    }`}>{s.status}</span>
                  </td>
                  <td className="px-5 py-3.5 text-gray-400">
                    {new Date(s.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-2 justify-end">
                      <button
                        onClick={() => navigate(`/surveys/${s.id}`)}
                        className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors"
                        title="View"
                      >
                        <Eye size={15} />
                      </button>
                      <button
                        onClick={() => deleteMutation.mutate(s.id)}
                        className="p-1.5 text-gray-400 hover:text-red-500 transition-colors"
                        title="Delete"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
