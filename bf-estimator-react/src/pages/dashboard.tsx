import React from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"

export default function Dashboard() {
  const { toast } = useToast()

  React.useEffect(() => {
    // Welcome toast when dashboard loads
    toast({
      title: "Welcome to BF Estimator",
      description: "Track your fitness journey and body fat percentage",
    })
  }, [])

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Current Stats</CardTitle>
            <CardDescription>Your latest measurements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Weight:</span>
                <span className="font-medium">185 lbs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Body Fat:</span>
                <span className="font-medium">18%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">BMI:</span>
                <span className="font-medium">24.5</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Last Updated:</span>
                <span className="font-medium">Today</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Goals</CardTitle>
            <CardDescription>Your fitness targets</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target Weight:</span>
                <span className="font-medium">175 lbs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target Body Fat:</span>
                <span className="font-medium">15%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target Date:</span>
                <span className="font-medium">June 30, 2025</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Progress:</span>
                <span className="font-medium">30%</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Daily Calories</CardTitle>
            <CardDescription>Recommended intake</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">TDEE:</span>
                <span className="font-medium">2,450 kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target Intake:</span>
                <span className="font-medium">2,100 kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Deficit:</span>
                <span className="font-medium">350 kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Protein Goal:</span>
                <span className="font-medium">150g</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="mt-6">
        <Card>
          <CardHeader>
            <CardTitle>Recent Progress</CardTitle>
            <CardDescription>Your journey over time</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="h-[300px] flex items-center justify-center border rounded">
              <p className="text-muted-foreground">Chart will be displayed here</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}