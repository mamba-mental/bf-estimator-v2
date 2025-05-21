import { useEffect, useState } from "react"
import { createClient } from "@supabase/supabase-js"
import { BarChart, LineChart, PieChart } from "lucide-react"
import { Button } from "@/components/ui/button"

// Initialize Supabase client
const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string
const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Types
interface UserProfile {
  id: string
  name: string
  current_weight: number
  current_bf: number
  goal_weight: number
  goal_bf: number
  start_date: string
  end_date: string
}

interface ProgressLog {
  id: string
  user_id: string
  date: string
  weight: number
  body_fat: number
}

const Dashboard = () => {
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [progressLogs, setProgressLogs] = useState<ProgressLog[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get current user
        const { data: { user } } = await supabase.auth.getUser()
        
        if (!user) {
          setLoading(false)
          return
        }

        // Get user profile
        const { data: profileData, error: profileError } = await supabase
          .from("profiles")
          .select("*")
          .eq("id", user.id)
          .single()

        if (profileError) {
          console.error("Error fetching profile:", profileError)
        } else {
          setProfile(profileData)
        }

        // Get progress logs
        const { data: logsData, error: logsError } = await supabase
          .from("progress_logs")
          .select("*")
          .eq("user_id", user.id)
          .order("date", { ascending: true })

        if (logsError) {
          console.error("Error fetching progress logs:", logsError)
        } else {
          setProgressLogs(logsData || [])
        }
      } catch (error) {
        console.error("Error fetching data:", error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent"></div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="flex h-full flex-col items-center justify-center space-y-4">
        <h2 className="text-2xl font-bold">Welcome to BF Estimator</h2>
        <p className="text-muted-foreground">Please complete your profile to get started</p>
        <Button>Set Up Profile</Button>
      </div>
    )
  }

  // Calculate progress
  const startDate = new Date(profile.start_date)
  const endDate = new Date(profile.end_date)
  const today = new Date()
  
  const totalDays = Math.max(1, (endDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
  const daysPassed = Math.max(0, Math.min(totalDays, (today.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24)))
  const progressPercentage = Math.round((daysPassed / totalDays) * 100)

  // Calculate weight loss progress
  const totalWeightLoss = profile.current_weight - profile.goal_weight
  const expectedWeightLoss = totalWeightLoss * (progressPercentage / 100)
  
  const currentWeight = progressLogs.length > 0 
    ? progressLogs[progressLogs.length - 1].weight 
    : profile.current_weight
    
  const actualWeightLoss = profile.current_weight - currentWeight
  const weightLossPercentage = Math.round((actualWeightLoss / totalWeightLoss) * 100)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <Button>Log Progress</Button>
      </div>

      {/* Progress Overview */}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <BarChart className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-semibold">Timeline Progress</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">{progressPercentage}%</p>
          <p className="text-sm text-muted-foreground">
            Day {Math.round(daysPassed)} of {Math.round(totalDays)}
          </p>
          <div className="mt-2 h-2 w-full rounded-full bg-muted">
            <div 
              className="h-full rounded-full bg-primary" 
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <LineChart className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-semibold">Weight Loss</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">{actualWeightLoss.toFixed(1)} lbs</p>
          <p className="text-sm text-muted-foreground">
            {weightLossPercentage}% of {totalWeightLoss.toFixed(1)} lbs goal
          </p>
          <div className="mt-2 h-2 w-full rounded-full bg-muted">
            <div 
              className="h-full rounded-full bg-primary" 
              style={{ width: `${weightLossPercentage}%` }}
            ></div>
          </div>
        </div>

        <div className="rounded-lg border bg-card p-4 shadow-sm">
          <div className="flex items-center gap-2">
            <PieChart className="h-5 w-5 text-muted-foreground" />
            <h3 className="font-semibold">Body Fat</h3>
          </div>
          <p className="mt-2 text-3xl font-bold">
            {progressLogs.length > 0 
              ? progressLogs[progressLogs.length - 1].body_fat.toFixed(1) 
              : profile.current_bf.toFixed(1)}%
          </p>
          <p className="text-sm text-muted-foreground">
            Goal: {profile.goal_bf.toFixed(1)}%
          </p>
          <div className="mt-2 h-2 w-full rounded-full bg-muted">
            <div 
              className="h-full rounded-full bg-primary" 
              style={{ 
                width: `${Math.min(100, Math.max(0, 100 - ((currentWeight - profile.goal_weight) / (profile.current_weight - profile.goal_weight)) * 100))}%` 
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Placeholder for charts */}
      <div className="rounded-lg border bg-card p-4 shadow-sm">
        <h3 className="mb-4 font-semibold">Progress Chart</h3>
        <div className="h-64 w-full bg-muted/20 flex items-center justify-center">
          <p className="text-muted-foreground">Chart will be displayed here</p>
        </div>
      </div>

      {/* AI Suggestions */}
      <div className="rounded-lg border bg-card p-4 shadow-sm">
        <h3 className="mb-2 font-semibold">AI Suggestions</h3>
        <div className="rounded-lg bg-muted/20 p-4">
          <p className="italic text-muted-foreground">
            Based on your progress, consider increasing your protein intake to help preserve lean mass during weight loss.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard