import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { supabase } from "@/lib/supabaseClient"

export default function UpdatePassword() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    password: "",
    confirmPassword: "",
  })

  // Check if we have a recovery token in the URL
  useEffect(() => {
    const hashParams = new URLSearchParams(window.location.hash.substring(1))
    if (!hashParams.get("access_token")) {
      toast({
        title: "Invalid reset link",
        description: "This password reset link is invalid or has expired.",
        variant: "destructive",
      })
      navigate("/reset-password")
    }
  }, [navigate, toast])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setFormData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.password !== formData.confirmPassword) {
      toast({
        title: "Passwords don't match",
        description: "Please make sure your passwords match.",
        variant: "destructive",
      })
      return
    }
    
    setIsLoading(true)

    try {
      const { error } = await supabase.auth.updateUser({
        password: formData.password,
      })
      
      if (error) {
        throw error
      }
      
      toast({
        title: "Password updated",
        description: "Your password has been successfully updated.",
      })
      
      // Redirect to login page
      navigate("/login")
    } catch (error: any) {
      console.error("Password update error:", error)
      toast({
        title: "Password update failed",
        description: error.message || "There was a problem updating your password. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl text-center">Update Password</CardTitle>
          <CardDescription className="text-center">
            Enter your new password
          </CardDescription>
        </CardHeader>
        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="password">New Password</Label>
              <Input
                id="password"
                name="password"
                type="password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirm New Password</Label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>
          </CardContent>
          <CardFooter className="flex flex-col space-y-4">
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Updating password..." : "Update Password"}
            </Button>
            <div className="text-center text-sm">
              Remember your password?{" "}
              <a 
                href="#" 
                className="text-primary hover:underline"
                onClick={(e) => {
                  e.preventDefault()
                  navigate("/login")
                }}
              >
                Back to Login
              </a>
            </div>
          </CardFooter>
        </form>
      </Card>
    </div>
  )
}