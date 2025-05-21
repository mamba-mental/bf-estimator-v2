import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import { ThemeProvider } from '@/components/theme-provider'

// Pages
import Dashboard from '@/pages/dashboard'
import Login from '@/pages/login'
import Register from '@/pages/register'
import ResetPassword from '@/pages/reset-password'
import UpdatePassword from '@/pages/update-password'
import Profile from '@/pages/profile'
import Goals from '@/pages/goals'
import Progress from '@/pages/progress'
import Reports from '@/pages/reports'
import NotFound from '@/pages/not-found'

// Layout components
import Layout from '@/components/layout'
import ProtectedRoute from '@/components/protected-route'

function App() {
  return (
    <ThemeProvider defaultTheme="system" storageKey="bf-estimator-theme">
      <Toaster />
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/reset-password" element={<ResetPassword />} />
        <Route path="/update-password" element={<UpdatePassword />} />
        
        {/* Protected routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<Layout />}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/goals" element={<Goals />} />
            <Route path="/progress" element={<Progress />} />
            <Route path="/reports" element={<Reports />} />
          </Route>
        </Route>
        
        {/* 404 route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </ThemeProvider>
  )
}

export default App