import { Outlet } from "react-router-dom"
import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Menu, X, Home, User, Target, BarChart2, FileText, LogOut } from "lucide-react"

const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const navigate = useNavigate()

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen)
  }

  const handleLogout = () => {
    // Implement logout functionality here
    navigate("/login")
  }

  const navItems = [
    { name: "Dashboard", icon: Home, path: "/" },
    { name: "Profile", icon: User, path: "/profile" },
    { name: "Goals", icon: Target, path: "/goals" },
    { name: "Progress", icon: BarChart2, path: "/progress" },
    { name: "Reports", icon: FileText, path: "/reports" },
  ]

  return (
    <div className="flex h-screen bg-background">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={toggleSidebar}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 z-50 w-64 transform bg-card shadow-lg transition-transform duration-300 ease-in-out lg:static lg:translate-x-0 ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex h-16 items-center justify-between px-4">
          <h1 className="text-xl font-bold">BF Estimator</h1>
          <button
            onClick={toggleSidebar}
            className="rounded p-1 hover:bg-muted lg:hidden"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <nav className="mt-8 px-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.name}>
                <a
                  href={item.path}
                  className="flex items-center rounded-md px-4 py-2 text-sm hover:bg-muted"
                  onClick={(e) => {
                    e.preventDefault()
                    navigate(item.path)
                    if (window.innerWidth < 1024) {
                      setSidebarOpen(false)
                    }
                  }}
                >
                  <item.icon className="mr-3 h-5 w-5" />
                  {item.name}
                </a>
              </li>
            ))}
          </ul>

          <div className="mt-auto pt-8">
            <button
              onClick={handleLogout}
              className="flex w-full items-center rounded-md px-4 py-2 text-sm text-destructive hover:bg-muted"
            >
              <LogOut className="mr-3 h-5 w-5" />
              Logout
            </button>
          </div>
        </nav>
      </aside>

      {/* Main content */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top navigation */}
        <header className="flex h-16 items-center justify-between border-b bg-card px-4 shadow-sm">
          <button
            onClick={toggleSidebar}
            className="rounded p-1 hover:bg-muted lg:hidden"
          >
            <Menu className="h-6 w-6" />
          </button>
          <div className="flex items-center space-x-4">
            {/* Add user profile dropdown or other header elements here */}
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-4">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout