import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './hooks/useAuth'

import LoginPage        from './pages/LoginPage'
import DashboardPage    from './pages/DashboardPage'
import SurveysPage      from './pages/SurveysPage'
import SurveyDetailPage from './pages/SurveyDetailPage'
import SurveyRespondPage from './pages/SurveyRespondPage'
import MysteryShoppingPage from './pages/MysteryShoppingPage'
import QualitativePage  from './pages/QualitativePage'
import Layout           from './components/layout/Layout'

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 30000, retry: 1 } }
})

function ProtectedRoute({ children }) {
  const { user, loading } = useAuth()
  if (loading) return <div className="flex items-center justify-center h-screen">Loading...</div>
  return user ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Toaster position="top-right" />
          <Routes>
            {/* Public */}
            <Route path="/login"      element={<LoginPage />} />
            <Route path="/survey/:token" element={<SurveyRespondPage />} />
            <Route path="/s/:token"   element={<SurveyRespondPage />} />

            {/* Protected */}
            <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
              <Route index                element={<DashboardPage />} />
              <Route path="surveys"       element={<SurveysPage />} />
              <Route path="surveys/:id"   element={<SurveyDetailPage />} />
              <Route path="mystery-shopping" element={<MysteryShoppingPage />} />
              <Route path="qualitative"   element={<QualitativePage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  )
}
