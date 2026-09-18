import { Navigate, Route, Routes } from 'react-router-dom'
import { HomePage } from '../pages/HomePage'
import { GpsPage } from '../pages/GpsPage'
import { LoginPage } from '../pages/LoginPage'
import { RegisterPage } from '../pages/RegisterPage'

function isAuthenticated() {
  try {
    return Boolean(JSON.parse(localStorage.getItem('sentinela-auth') || 'null')?.access_token)
  } catch {
    localStorage.removeItem('sentinela-auth')
    return false
  }
}

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/home" element={isAuthenticated() ? <HomePage /> : <Navigate to="/login" replace />} />
      <Route path="/gps" element={isAuthenticated() ? <GpsPage /> : <Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to={isAuthenticated() ? '/home' : '/login'} replace />} />
    </Routes>
  )
}
