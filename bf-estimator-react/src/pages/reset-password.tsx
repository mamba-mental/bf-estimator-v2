import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { supabase } from "@/lib/supabaseClient"

export default function ResetPassword() {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [email, setEmail] = useState("")
  const [resetSent, setResetSent] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/update-password`,
      })

      if (error) {
        throw error
      }

      setResetSent(true)
      toast({
        title: "Reset email sent",
        description: "Check your email for a password reset link",
      })
    } catch (error: any) {
      console.error("Password reset error:", error)
      toast({
        title: "Password reset failed",
        description: error.message || "There was a problem sending the reset email. Please try again.",
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
          <CardTitle className="text-2xl text-center">Reset Password</CardTitle>
          <CardDescription className="text-center">
            {resetSent 
              ? "Check your email for a password reset link" 
              : "Enter your email to receive a password reset link"}
          </CardDescription>
        </CardHeader>
        {!resetSent ? (
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  placeholder="your.email@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Sending reset link..." : "Send Reset Link"}
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
        ) : (
          <CardFooter className="flex flex-col space-y-4">
            <Button 
              className="w-full" 
              onClick={() => navigate("/login")}
            >
              Back to Login
            </Button>
          </CardFooter>
        )}
      </Card>
    </div>
  )
}