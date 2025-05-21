import { Navigate, Outlet } from "react-router-dom"
import { useToast } from "@/components/ui/use-toast"

// Mock authentication state
const useAuth = () => {
  // This is a placeholder for actual authentication logic
  // In a real app, this would check if the user is logged in
  // For now, we'll just return true to simulate being logged in
  return { isAuthenticated: true }
}

export default function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  const { toast } = useToast()
  
  if (!isAuthenticated) {
    // Show toast notification when redirecting
    toast({
      title: "Authentication required",
      description: "Please log in to access this page",
      variant: "destructive",
    })
    
    // Redirect to login page
    return <Navigate to="/login" replace />
  }
  
  // If authenticated, render the child routes
  return <Outlet />
}