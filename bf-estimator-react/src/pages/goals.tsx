import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent } from "@/lib/utils"

export default function Goals() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  
  // Mock current stats
  const currentStats = {
    weight: 185, // in lbs
    bodyFat: 18, // percentage
    date: new Date(),
  }
  
  const [goalData, setGoalData] = useState({
    targetWeight: 175, // in lbs
    targetBodyFat: 15, // percentage
    targetDate: "2025-06-30",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setGoalData((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // TODO: Implement actual goal update logic
      console.log("Goal update with:", goalData)
      
      // Simulate successful update
      setTimeout(() => {
        toast({
          title: "Goals updated",
          description: "Your fitness goals have been updated successfully.",
        })
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      toast({
        title: "Update failed",
        description: "There was a problem updating your goals. Please try again.",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  // Calculate weight to lose
  const weightToLose = currentStats.weight - goalData.targetWeight
  
  // Calculate body fat to lose
  const bodyFatToLose = currentStats.bodyFat - goalData.targetBodyFat
  
  // Calculate days until target
  const today = new Date()
  const targetDate = new Date(goalData.targetDate)
  const daysUntilTarget = Math.max(1, Math.round((targetDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)))
  
  // Calculate daily deficit needed
  const dailyDeficit = Math.round((weightToLose * 3500) / daysUntilTarget)

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
              To reach your goal of {formatWeight(goalData.targetWeight)} by {new Date(goalData.targetDate).toLocaleDateString()}, 
              you need to maintain a daily calorie deficit of approximately {dailyDeficit} kcal.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}