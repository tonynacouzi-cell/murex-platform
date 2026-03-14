import { useAuth } from '../hooks/useAuth'
import { useQuery } from '@tanstack/react-query'
import api from '../api/client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import { ClipboardList, TrendingUp, Users, CheckCircle, ShoppingBag, Video, ArrowUpRight } from 'lucide-react'

const COLORS = ['#1E3A5F', '#0ea5e9', '#38bdf8', '#93c5fd']

export default function DashboardPage() {
  const { user } = useAuth()
  const { data: surveys = [] } = useQuery({
    queryKey: ['surveys'],
    queryFn: () => api.get('/surveys/').then(r => r.data),
  })

  const total   = surveys.length
  const active  = surveys.filter(s => s.status === 'active').length
  const draft   = surveys.filter(s => s.status === 'draft').length
  const closed  = surveys.filter(s => s.status === 'closed').length

  const statusData = [
    { name: 'Active',  value: active  || 0 },
    { name: 'Draft',   value: draft   || 1 },
    { name: 'Closed',  value: closed  || 0 },
    { name: 'Paused',  value: 0 },
  ].filter(d => d.value > 0)

  const barData = [
    { month: 'Jan', surveys: 2 },
    { month: 'Feb', surveys: 4 },
    { month: 'Mar', surveys: total || 1 },
  ]

  const stats = [
    { label: 'Total Surveys',   value: total,  icon: ClipboardList, color: 'bg-blue-50 text-[#1E3A5F]' },
    { label: 'Active Surveys',  value: active, icon: TrendingUp,    color: 'bg-sky-50 text-sky-600'    },
    { label: 'Draft',           value: draft,  icon: Users,         color: 'bg-amber-50 text-amber-600' },
    { label: 'Closed',          value: closed, icon: CheckCircle,   color: 'bg-green-50 text-green-600' },
  ]

  const modules = [
    { title: 'CX Surveys',       desc: 'NPS, CSAT & custom surveys',   icon: ClipboardList, href: '/surveys',          color: 'bg-[#1E3A5F]' },
    { title: 'Mystery Shopping', desc: 'Audit & field research',        icon: ShoppingBag,   href: '/mystery-shopping', color: 'bg-sky-600'   },
    { title: 'Qualitative AI',   desc: 'Transcription & analysis',      icon: Video,         href: '/qualitative',      color: 'bg-teal-600'  },
  ]

  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening'
  const firstName = user?.full_name?.split(' ')[0] || 'there'

  return (
    <div className="p-6 space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-900">{greeting}, {firstName}</h1>
          <p className="text-sm text-slate-500 mt-0.5">Here's what's happening on your platform today.</p>
        </div>
        <div className="text-xs text-slate-400 bg-slate-100 px-3 py-1.5 rounded-full">
          {new Date().toLocaleDateString('en-AE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl border border-slate-100 p-4 shadow-card hover:shadow-card-hover transition-shadow">
            <div className="flex items-center justify-between mb-3">
              <div className={`w-9 h-9 rounded-lg ${color} flex items-center justify-center`}>
                <Icon size={16} />
              </div>
              <ArrowUpRight size={14} className="text-slate-300" />
            </div>
            <div className="text-2xl font-bold text-slate-900">{value}</div>
            <div className="text-xs text-slate-500 mt-0.5">{label}</div>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-100 p-5 shadow-card">
          <h3 className="text-sm font-semibold text-slate-900 mb-4">Survey Activity</h3>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={barData} barSize={32}>
              <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
              <Bar dataKey="surveys" fill="#1E3A5F" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white rounded-xl border border-slate-100 p-5 shadow-card">
          <h3 className="text-sm font-semibold text-slate-900 mb-4">Survey Status</h3>
          {statusData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={140}>
                <PieChart>
                  <Pie data={statusData} cx="50%" cy="50%" innerRadius={40} outerRadius={60} paddingAngle={3} dataKey="value">
                    {statusData.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: 8, border: '1px solid #e2e8f0', fontSize: 12 }} />
                </PieChart>
              </ResponsiveContainer>
              <div className="space-y-1.5 mt-2">
                {statusData.map((d, i) => (
                  <div key={d.name} className="flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 rounded-full" style={{ background: COLORS[i % COLORS.length] }}></div>
                      <span className="text-slate-600">{d.name}</span>
                    </div>
                    <span className="font-medium text-slate-900">{d.value}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-36 text-slate-400 text-sm">No data yet</div>
          )}
        </div>
      </div>

      {/* Module cards */}
      <div>
        <h3 className="text-sm font-semibold text-slate-900 mb-3">Platform Modules</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {modules.map(({ title, desc, icon: Icon, href, color }) => (
            <a key={title} href={href}
               className="group bg-white rounded-xl border border-slate-100 p-5 shadow-card hover:shadow-card-hover transition-all hover:-translate-y-0.5">
              <div className={`w-10 h-10 ${color} rounded-lg flex items-center justify-center mb-3`}>
                <Icon size={18} className="text-white" />
              </div>
              <div className="font-semibold text-slate-900 text-sm group-hover:text-[#1E3A5F]">{title}</div>
              <div className="text-xs text-slate-500 mt-1">{desc}</div>
            </a>
          ))}
        </div>
      </div>
    </div>
  )
}
