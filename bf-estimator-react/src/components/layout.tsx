import { useState } from "react"
import { Outlet, Link, useLocation, useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { useAuth } from "@/contexts/auth-context"

export default function Layout() {
  const location = useLocation()
  const navigate = useNavigate()
  const { toast } = useToast()
  const { signOut, user } = useAuth()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  
  const navItems = [
    { path: "/", label: "Dashboard" },
    { path: "/goals", label: "Goals" },
    { path: "/progress", label: "Progress" },
    { path: "/reports", label: "Reports" },
    { path: "/profile", label: "Profile" },
  ]
  
  const handleLogout = async () => {
    try {
      const { error } = await signOut()
      
      if (error) {
        throw error
      }
      
      toast({
        title: "Logged out",
        description: "You have been successfully logged out",
      })
      navigate("/login")
    } catch (error: any) {
      console.error("Logout error:", error)
      toast({
        title: "Logout failed",
        description: error.message || "There was a problem logging out. Please try again.",
        variant: "destructive",
      })
    }
  }
  
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen)
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-40 w-full border-b bg-background">
        <div className="container flex h-16 items-center justify-between py-4">
          <div className="flex items-center gap-2">
            <Link to="/" className="flex items-center gap-2">
              <span className="font-bold text-xl">BF Estimator</span>
            </Link>
          </div>
          
          {/* User info */}
          <div className="hidden md:block text-sm">
            {user && <span>Hello, {user.user_metadata?.name || user.email}</span>}
          </div>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center gap-6">
            {navItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`text-sm font-medium transition-colors hover:text-primary ${
                  location.pathname === item.path
                    ? "text-foreground"
                    : "text-muted-foreground"
                }`}
              >
                {item.label}
              </Link>
            ))}
            <Button variant="outline" onClick={handleLogout}>
              Logout
            </Button>
          </nav>
          
          {/* Mobile Menu Button */}
          <button
            className="md:hidden"
            onClick={toggleMobileMenu}
            aria-label="Toggle menu"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6"
            >
              {isMobileMenuOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="4" y1="12" x2="20" y2="12" />
                  <line x1="4" y1="6" x2="20" y2="6" />
                  <line x1="4" y1="18" x2="20" y2="18" />
                </>
              )}
            </svg>
          </button>
        </div>
        
        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t">
            <div className="container py-2 space-y-1">
              {navItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block py-2 text-sm font-medium transition-colors hover:text-primary ${
                    location.pathname === item.path
                      ? "text-foreground"
                      : "text-muted-foreground"
                  }`}
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              <Button
                variant="outline"
                onClick={() => {
                  handleLogout()
                  setIsMobileMenuOpen(false)
                }}
                className="w-full mt-2"
              >
                Logout
              </Button>
            </div>
          </div>
        )}
      </header>
      
      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>
      
      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col md:flex-row items-center justify-between gap-4 md:h-16">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} BF Estimator. All rights reserved.
          </p>
          <div className="flex items-center gap-4">
            <Link
              to="/privacy"
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Privacy
            </Link>
            <Link
              to="/terms"
              className="text-sm text-muted-foreground hover:text-foreground"
            >
              Terms
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}