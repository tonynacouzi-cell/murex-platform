// SurveyDetailPage.jsx
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { surveysApi } from '../api/client'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { Download } from 'lucide-react'
import toast from 'react-hot-toast'

export default function SurveyDetailPage() {
  const { id } = useParams()

  const { data: survey } = useQuery({
    queryKey: ['survey', id],
    queryFn: () => surveysApi.get(id).then(r => r.data),
  })
  const { data: dashboard } = useQuery({
    queryKey: ['dashboard', id],
    queryFn: () => surveysApi.dashboard(id).then(r => r.data),
    enabled: !!id,
  })

  const npsData = dashboard ? [
    { name: 'Promoters',  value: dashboard.promoters,  color: '#22c55e' },
    { name: 'Passives',   value: dashboard.passives,   color: '#f59e0b' },
    { name: 'Detractors', value: dashboard.detractors, color: '#ef4444' },
  ] : []

  const downloadExcel = async () => {
    try {
      const r = await surveysApi.exportExcel(id)
      const url = URL.createObjectURL(new Blob([r.data]))
      const a = document.createElement('a'); a.href = url
      a.download = `survey_${id}.xlsx`; a.click()
    } catch { toast.error('Export failed') }
  }

  return (
    <div className="p-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">{survey?.title}</h2>
          <p className="text-gray-500 text-sm mt-1">{survey?.status} · {survey?.channel}</p>
        </div>
        <button
          onClick={downloadExcel}
          className="flex items-center gap-2 border border-gray-200 text-gray-600 px-3 py-2 rounded-lg text-sm hover:bg-gray-50"
        >
          <Download size={15} /> Export Excel
        </button>
      </div>

      {dashboard && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          {[
            { label: 'Total Responses', value: dashboard.total_responses },
            { label: 'NPS Score',       value: dashboard.nps_score ?? 'N/A' },
            { label: 'Avg CSAT',        value: dashboard.avg_csat ?? 'N/A' },
            { label: 'Completion',      value: `${dashboard.completion_rate}%` },
          ].map(c => (
            <div key={c.label} className="bg-white rounded-xl border border-gray-100 p-5">
              <p className="text-2xl font-bold text-gray-900">{c.value}</p>
              <p className="text-sm text-gray-500">{c.label}</p>
            </div>
          ))}
        </div>
      )}

      {npsData.some(d => d.value > 0) && (
        <div className="bg-white rounded-xl border border-gray-100 p-6 max-w-sm">
          <h3 className="font-semibold text-gray-900 mb-4">NPS Breakdown</h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie data={npsData} cx="50%" cy="50%" outerRadius={80} dataKey="value">
                {npsData.map((e, i) => <Cell key={i} fill={e.color} />)}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  )
}
