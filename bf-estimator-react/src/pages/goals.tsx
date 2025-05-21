import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent } from "@/lib/utils"
import { useAuth } from "@/contexts/auth-context"
import { supabase } from "@/lib/supabaseClient"

export default function Goals() {
  const { toast } = useToast()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  
  // Current stats from most recent progress entry
  const [currentStats, setCurrentStats] = useState({
    weight: 0, // in lbs
    bodyFat: 0, // percentage
    date: new Date(),
  })
  
  const [goalData, setGoalData] = useState({
    targetWeight: 0, // in lbs
    targetBodyFat: 0, // percentage
    targetDate: "",
  })

  // Fetch user's current stats and goals on page load
  useEffect(() => {
    async function fetchData() {
      if (!user) return
      
      try {
        setIsFetching(true)
        
        // Fetch the most recent progress entry for current stats
        const { data: progressData, error: progressError } = await supabase
          .from('progress_entries')
          .select('*')
          .eq('user_id', user.id)
          .order('date', { ascending: false })
          .limit(1)
        
        if (progressError) {
          throw progressError
        }
        
        if (progressData && progressData.length > 0) {
          setCurrentStats({
            weight: progressData[0].weight,
            bodyFat: progressData[0].body_fat_percentage,
            date: new Date(progressData[0].date),
          })
        }
        
        // Fetch the user's goals
        const { data: goalsData, error: goalsError } = await supabase
          .from('goals')
          .select('*')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false })
          .limit(1)
        
        if (goalsError) {
          throw goalsError
        }
        
        if (goalsData && goalsData.length > 0) {
          setGoalData({
            targetWeight: goalsData[0].target_weight,
            targetBodyFat: goalsData[0].target_body_fat,
            targetDate: goalsData[0].target_date,
          })
        } else {
          // Set default values if no goals exist
          const defaultDate = new Date()
          defaultDate.setMonth(defaultDate.getMonth() + 3) // Default to 3 months from now
          
          setGoalData({
            targetWeight: currentStats.weight > 0 ? Math.round(currentStats.weight * 0.9) : 175, // Default to 10% less than current weight
            targetBodyFat: currentStats.bodyFat > 0 ? Math.round(currentStats.bodyFat * 0.9) : 15, // Default to 10% less than current body fat
            targetDate: defaultDate.toISOString().split('T')[0],
          })
        }
      } catch (error) {
        console.error('Error fetching data:', error)
        toast({
          title: "Failed to load data",
          description: "There was a problem loading your data. Please refresh the page.",
          variant: "destructive",
        })
      } finally {
        setIsFetching(false)
      }
    }
    
    fetchData()
  }, [user, toast])

  const handleChange = (e: any) => {
    const { name, value } = e.target
    setGoalData((prev: any) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()
    
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please log in to save your goals.",
        variant: "destructive",
      })
      return
    }
    
    setIsLoading(true)

    try {
      // Prepare the data for Supabase
      const goalRecord = {
        user_id: user.id,
        target_weight: parseFloat(goalData.targetWeight.toString()),
        target_body_fat: parseFloat(goalData.targetBodyFat.toString()),
        target_date: goalData.targetDate,
        created_at: new Date().toISOString(),
      }
      
      // Upsert the goal (insert if not exists, update if exists)
      const { error } = await supabase
        .from('goals')
        .upsert(goalRecord, {
          onConflict: 'user_id',
          ignoreDuplicates: false,
        })
      
      if (error) throw error
      
      toast({
        title: "Goals updated",
        description: "Your fitness goals have been updated successfully.",
      })
    } catch (error) {
      console.error('Error saving goals:', error)
      toast({
        title: "Update failed",
        description: "There was a problem updating your goals. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate weight to lose
  const weightToLose = currentStats.weight - parseFloat(goalData.targetWeight.toString())
  
  // Calculate body fat to lose
  const bodyFatToLose = currentStats.bodyFat - parseFloat(goalData.targetBodyFat.toString())
  
  // Calculate days until target
  const today = new Date()
  const targetDate = new Date(goalData.targetDate)
  const daysUntilTarget = Math.max(1, Math.round((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)))
  
  // Calculate daily deficit needed
  const dailyDeficit = Math.round((weightToLose * 3500) / daysUntilTarget)

  if (isFetching) {
    return (
      <div className="container mx-auto p-6 flex justify-center items-center min-h-[50vh]">
        <p>Loading your goals...</p>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Fitness Goals</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Current Stats</CardTitle>
            <CardDescription>Your current measurements</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {currentStats.weight > 0 ? (
              <>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Weight:</span>
                  <span className="font-medium">{formatWeight(currentStats.weight)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Current Body Fat:</span>
                  <span className="font-medium">{formatPercent(currentStats.bodyFat / 100)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">As of:</span>
                  <span className="font-medium">{formatDate(currentStats.date)}</span>
                </div>
              </>
            ) : (
              <p className="text-muted-foreground">No measurements recorded yet. Add your first entry in the Progress page.</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Set Your Goals</CardTitle>
            <CardDescription>Define your fitness targets</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="targetWeight">Target Weight (lbs)</Label>
                <Input
                  id="targetWeight"
                  name="targetWeight"
                  type="number"
                  value={goalData.targetWeight}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetBodyFat">Target Body Fat (%)</Label>
                <Input
                  id="targetBodyFat"
                  name="targetBodyFat"
                  type="number"
                  value={goalData.targetBodyFat}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="targetDate">Target Date</Label>
                <Input
                  id="targetDate"
                  name="targetDate"
                  type="date"
                  value={goalData.targetDate}
                  onChange={handleChange}
                  required
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Saving..." : "Save Goals"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>

      {currentStats.weight > 0 && goalData.targetWeight > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Goal Analysis</CardTitle>
            <CardDescription>What you need to achieve your goals</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Weight to Lose:</span>
              <span className="font-medium">{formatWeight(weightToLose)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Body Fat to Lose:</span>
              <span className="font-medium">{formatPercent(bodyFatToLose / 100)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Days Until Target:</span>
              <span className="font-medium">{daysUntilTarget} days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Daily Calorie Deficit Needed:</span>
              <span className="font-medium">{dailyDeficit} kcal</span>
            </div>
            <div className="mt-4 p-4 bg-muted rounded-md">
              <p className="text-sm">
                To reach your goal of {formatWeight(parseFloat(goalData.targetWeight.toString()))} by {new Date(goalData.targetDate).toLocaleDateString()}, 
                you need to maintain a daily calorie deficit of approximately {dailyDeficit} kcal.
              </p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}