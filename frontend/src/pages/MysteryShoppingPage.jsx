import { useQuery } from '@tanstack/react-query'
import { msApi } from '../api/client'
import { MapPin, Calendar, DollarSign } from 'lucide-react'

export default function MysteryShoppingPage() {
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ['ms-projects'],
    queryFn: () => msApi.projects.list().then(r => r.data),
  })

  return (
    <div className="p-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-bold text-gray-900">Mystery Shopping</h2>
          <p className="text-gray-500 text-sm">{projects.length} active projects</p>
        </div>
      </div>

      {isLoading ? (
        <p className="text-gray-400">Loading projects...</p>
      ) : projects.length === 0 ? (
        <div className="bg-white rounded-xl border border-gray-100 p-12 text-center">
          <p className="text-gray-400 text-sm">No projects yet.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {projects.map(p => (
            <div key={p.id} className="bg-white rounded-xl border border-gray-100 p-5 hover:shadow-sm transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <h3 className="font-semibold text-gray-900 text-sm leading-snug">{p.name}</h3>
                <span className={`text-xs px-2 py-1 rounded-full font-medium shrink-0 ml-2 ${
                  p.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                }`}>{p.status}</span>
              </div>
              <p className="text-xs text-gray-500 mb-3">{p.client_name}</p>
              <div className="space-y-1.5 text-xs text-gray-500">
                {p.incentive_per_visit && (
                  <div className="flex items-center gap-1.5">
                    <DollarSign size={13} />
                    AED {p.incentive_per_visit} per visit
                  </div>
                )}
                <div className="flex items-center gap-1.5">
                  <Calendar size={13} />
                  {new Date(p.created_at).toLocaleDateString()}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
