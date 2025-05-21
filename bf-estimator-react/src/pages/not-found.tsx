import { Button } from "@/components/ui/button"
import { useNavigate } from "react-router-dom"

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div className="flex flex-col items-center justify-center min-h-screen p-6 text-center">
      <h1 className="text-6xl font-bold">404</h1>
      <h2 className="text-2xl font-semibold mt-4">Page Not Found</h2>
      <p className="text-muted-foreground mt-2 mb-6">
        The page you are looking for doesn't exist or has been moved.
      </p>
      <div className="flex gap-4">
        <Button onClick={() => navigate(-1)}>
          Go Back
        </Button>
        <Button variant="outline" onClick={() => navigate("/")}>
          Go to Dashboard
        </Button>
      </div>
    </div>
  )
}