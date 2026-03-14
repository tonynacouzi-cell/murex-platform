import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'
import {
  LayoutDashboard, ClipboardList, ShoppingBag,
  Video, LogOut, Bell, Search
} from 'lucide-react'
import Logo from '../Logo'

const navItems = [
  { to: '/',                 icon: LayoutDashboard, label: 'Dashboard'        },
  { to: '/surveys',          icon: ClipboardList,   label: 'CX Surveys'       },
  { to: '/mystery-shopping', icon: ShoppingBag,     label: 'Mystery Shopping' },
  { to: '/qualitative',      icon: Video,           label: 'Qualitative AI'   },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const handleLogout = () => { logout(); navigate('/login') }
  const initials = user?.full_name?.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase() || 'U'

  return (
    <div className="flex h-screen bg-slate-50 font-sans">
      {/* Sidebar */}
      <aside className="w-60 bg-[#1E3A5F] text-white flex flex-col shrink-0 shadow-xl">
        <div className="px-5 py-5 border-b border-white/10">
          <Logo size="md" white />
        </div>

        <nav className="flex-1 px-3 py-5 space-y-0.5">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all
                 ${isActive
                   ? 'bg-white/15 text-white font-semibold shadow-sm'
                   : 'text-blue-100/80 hover:bg-white/10 hover:text-white'
                 }`
              }
            >
              <Icon size={16} strokeWidth={isActive => isActive ? 2.5 : 1.5} />
              {label}
            </NavLink>
          ))}
        </nav>

        {/* User section */}
        <div className="px-4 py-4 border-t border-white/10">
          <div className="flex items-center gap-3 mb-3 px-1">
            <div className="w-8 h-8 rounded-full bg-sky-400 flex items-center justify-center text-xs font-bold text-white shrink-0">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold truncate text-white">{user?.full_name}</p>
              <p className="text-xs text-blue-300 truncate capitalize">{user?.role?.replace('_', ' ')}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 text-xs text-blue-300 hover:text-white transition-colors w-full px-1 py-1 rounded-lg hover:bg-white/10"
          >
            <LogOut size={13} /> Sign out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top bar */}
        <header className="bg-white border-b border-slate-100 px-6 py-3 flex items-center justify-between shrink-0 shadow-sm">
          <div className="flex items-center gap-2 bg-slate-50 border border-slate-200 rounded-lg px-3 py-2 w-64">
            <Search size={14} className="text-slate-400" />
            <input
              type="text"
              placeholder="Search..."
              className="bg-transparent text-sm text-slate-600 placeholder:text-slate-400 outline-none w-full"
            />
          </div>
          <div className="flex items-center gap-3">
            <button className="relative p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
              <Bell size={18} />
              <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-sky-500 rounded-full"></span>
            </button>
            <div className="w-8 h-8 rounded-full bg-[#1E3A5F] flex items-center justify-center text-xs font-bold text-white">
              {initials}
            </div>
          </div>
        </header>

        <main className="flex-1 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
