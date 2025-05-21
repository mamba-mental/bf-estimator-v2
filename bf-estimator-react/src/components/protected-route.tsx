import { Navigate, Outlet } from "react-router-dom"
import { useToast } from "@/components/ui/use-toast"
import { useAuth } from "@/contexts/auth-context"

export default function ProtectedRoute() {
  const { user, loading } = useAuth()
  const { toast } = useToast()
  
  // Show loading state while checking authentication
  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>
  }

  // Redirect if not authenticated
  if (!user) {
    // We call toast inside a setTimeout to avoid the render-phase state update
    setTimeout(() => {
      toast({
        title: "Authentication required",
        description: "Please log in to access this page",
        variant: "destructive",
      });
    }, 0);
    
    // Redirect to login page
    return <Navigate to="/login" replace />
  }
  
  // If authenticated, render the child routes
  return <Outlet />
}