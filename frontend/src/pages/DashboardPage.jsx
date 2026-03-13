import { useQuery } from '@tanstack/react-query'
import { surveysApi } from '../api/client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import { ClipboardList, TrendingUp, Users, CheckCircle } from 'lucide-react'

function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="bg-white rounded-xl border border-gray-100 p-5 flex items-center gap-4">
      <div className={`w-11 h-11 rounded-lg flex items-center justify-center ${color}`}>
        <Icon size={20} className="text-white" />
      </div>
      <div>
        <p className="text-2xl font-bold text-gray-900">{value}</p>
        <p className="text-sm text-gray-500">{label}</p>
      </div>
    </div>
  )
}

export default function DashboardPage() {
  const { data: surveys = [], isLoading } = useQuery({
    queryKey: ['surveys'],
    queryFn: () => surveysApi.list({ limit: 50 }).then(r => r.data),
  })

  const active   = surveys.filter(s => s.status === 'active').length
  const draft    = surveys.filter(s => s.status === 'draft').length
  const closed   = surveys.filter(s => s.status === 'closed').length

  const statusData = [
    { name: 'Active',   value: active,  color: '#22c55e' },
    { name: 'Draft',    value: draft,   color: '#f59e0b' },
    { name: 'Closed',   value: closed,  color: '#6b7280' },
  ]

  return (
    <div className="p-8">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-gray-900">Dashboard</h2>
        <p className="text-gray-500 text-sm">Overview of your survey platform</p>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Surveys"  value={surveys.length} icon={ClipboardList} color="bg-[#1E3A5F]" />
        <StatCard label="Active Surveys" value={active}         icon={TrendingUp}    color="bg-green-500" />
        <StatCard label="Drafts"         value={draft}          icon={Users}         color="bg-amber-500" />
        <StatCard label="Closed"         value={closed}         icon={CheckCircle}   color="bg-gray-400"  />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Survey Status</h3>
          <ResponsiveContainer width="100%" height={220}>
            <BarChart data={statusData}>
              <XAxis dataKey="name" tick={{ fontSize: 13 }} />
              <YAxis allowDecimals={false} tick={{ fontSize: 13 }} />
              <Tooltip />
              <Bar dataKey="value" radius={[6, 6, 0, 0]}>
                {statusData.map((entry, i) => (
                  <Cell key={i} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-gray-100 p-6">
          <h3 className="font-semibold text-gray-900 mb-4">Recent Surveys</h3>
          {isLoading ? (
            <p className="text-gray-400 text-sm">Loading...</p>
          ) : surveys.slice(0, 5).map(s => (
            <div key={s.id} className="flex items-center justify-between py-2.5 border-b border-gray-50 last:border-0">
              <span className="text-sm text-gray-800 truncate max-w-xs">{s.title}</span>
              <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                s.status === 'active'   ? 'bg-green-100 text-green-700' :
                s.status === 'draft'    ? 'bg-amber-100 text-amber-700' :
                                          'bg-gray-100 text-gray-600'
              }`}>{s.status}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
