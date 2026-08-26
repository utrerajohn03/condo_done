import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './AuthContext'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import MaintenanceRequests from './pages/MaintenanceRequests'
import Units from './pages/Units'
import ManageUsers from './pages/ManageUsers'
import ResidentAssignments from './pages/ResidentAssignments'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function GuestRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (isAuthenticated) return <Navigate to="/dashboard" replace />
  return children
}

// Second layer of enforcement beyond the sidebar's visibility filter — "Residents
// must NOT... access administrator, staff, or property manager pages" applies even
// if someone types the URL directly. The backend's permission checks are still the
// real security boundary; this just keeps the resident from landing on a page full
// of 403 errors.
function RoleProtectedRoute({ allowedRoles, children }) {
  const { isAuthenticated, role } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (!allowedRoles.includes(role)) return <Navigate to="/dashboard" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<GuestRoute><Login /></GuestRoute>} />
      <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/maintenance-requests" element={<ProtectedRoute><MaintenanceRequests /></ProtectedRoute>} />
      <Route path="/units" element={
        <RoleProtectedRoute allowedRoles={['staff', 'manager', 'admin']}><Units /></RoleProtectedRoute>
      } />
      <Route path="/manage-users" element={
        <RoleProtectedRoute allowedRoles={['staff', 'manager', 'admin']}><ManageUsers /></RoleProtectedRoute>
      } />
      <Route path="/resident-assignments" element={
        <RoleProtectedRoute allowedRoles={['staff', 'manager', 'admin']}><ResidentAssignments /></RoleProtectedRoute>
      } />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  )
}
