import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth'
import toast from 'react-hot-toast'
import Logo from '../components/Logo'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    try {
      await login(email, password)
      toast.success('Welcome back!')
      navigate('/')
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-[#1E3A5F] flex-col justify-between p-12 relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 opacity-10">
          <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" strokeWidth="0.5"/>
              </pattern>
            </defs>
            <rect width="100%" height="100%" fill="url(#grid)" />
          </svg>
        </div>
        {/* Decorative circles */}
        <div className="absolute -bottom-24 -right-24 w-96 h-96 rounded-full bg-blue-400 opacity-10"></div>
        <div className="absolute top-1/3 -left-16 w-64 h-64 rounded-full bg-sky-400 opacity-10"></div>

        <div className="relative z-10">
          <Logo size="lg" white />
        </div>

        <div className="relative z-10 space-y-8">
          <div>
            <h2 className="text-3xl font-bold text-white leading-tight">
              Intelligent Research<br/>& Survey Management
            </h2>
            <p className="mt-4 text-blue-200 text-sm leading-relaxed max-w-sm">
              Built for the GCC market. Manage CX surveys, mystery shopping audits, and qualitative research in one platform.
            </p>
          </div>

          <div className="grid grid-cols-3 gap-4">
            {[
              { label: 'CX Surveys', icon: '◈' },
              { label: 'Mystery Shopping', icon: '◉' },
              { label: 'Qualitative AI', icon: '◎' },
            ].map(f => (
              <div key={f.label} className="bg-white/10 rounded-xl p-3 backdrop-blur-sm border border-white/10">
                <div className="text-sky-300 text-lg mb-1">{f.icon}</div>
                <div className="text-white text-xs font-medium">{f.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="relative z-10">
          <p className="text-blue-300 text-xs">Powered by VME · © 2026 Murex Insights</p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-slate-50">
        <div className="w-full max-w-sm">
          {/* Mobile logo */}
          <div className="lg:hidden mb-8 flex justify-center">
            <Logo size="lg" />
          </div>

          <div className="bg-white rounded-2xl shadow-elevated border border-slate-100 p-8">
            <div className="mb-8">
              <h1 className="text-xl font-bold text-slate-900">Sign in</h1>
              <p className="text-slate-500 text-sm mt-1">Enter your credentials to continue</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
                  Email address
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  className="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
                             text-slate-900 bg-slate-50 focus:bg-white
                             focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]/20 focus:border-[#1E3A5F]
                             transition-all placeholder:text-slate-400"
                  placeholder="you@company.com"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-600 uppercase tracking-wider mb-1.5">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  className="w-full border border-slate-200 rounded-lg px-3.5 py-2.5 text-sm
                             text-slate-900 bg-slate-50 focus:bg-white
                             focus:outline-none focus:ring-2 focus:ring-[#1E3A5F]/20 focus:border-[#1E3A5F]
                             transition-all placeholder:text-slate-400"
                  placeholder="••••••••"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-[#1E3A5F] text-white rounded-lg py-2.5 text-sm font-semibold
                           hover:bg-[#162d4a] active:scale-[0.99] transition-all
                           disabled:opacity-60 disabled:cursor-not-allowed
                           shadow-sm mt-2"
              >
                {loading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                    </svg>
                    Signing in...
                  </span>
                ) : 'Sign In'}
              </button>
            </form>
          </div>

          <p className="text-center text-xs text-slate-400 mt-6">
            Murex Insights · Powered by VME
          </p>
        </div>
      </div>
    </div>
  )
}
