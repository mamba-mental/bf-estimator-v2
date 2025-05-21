import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent, calculateBMI, getBMICategory } from "@/lib/utils"

export default function Progress() {
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(false)
  
  // Mock progress data
  const progressHistory = [
    { date: new Date("2025-01-01"), weight: 195, bodyFat: 22, neck: 16, waist: 36, hips: 42 },
    { date: new Date("2025-02-01"), weight: 190, bodyFat: 20, neck: 15.5, waist: 35, hips: 41 },
    { date: new Date("2025-03-01"), weight: 187, bodyFat: 19, neck: 15.5, waist: 34, hips: 40 },
    { date: new Date("2025-04-01"), weight: 185, bodyFat: 18, neck: 15, waist: 33, hips: 39 },
  ]
  
  const [newEntry, setNewEntry] = useState({
    weight: "",
    neck: "",
    waist: "",
    hips: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setNewEntry((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      // TODO: Implement actual progress entry logic
      console.log("New progress entry:", newEntry)
      
      // Simulate successful entry
      setTimeout(() => {
        toast({
          title: "Progress recorded",
          description: "Your new measurements have been saved successfully.",
        })
        setNewEntry({
          weight: "",
          neck: "",
          waist: "",
          hips: "",
        })
        setIsLoading(false)
      }, 1000)
    } catch (error) {
      toast({
        title: "Entry failed",
        description: "There was a problem saving your progress. Please try again.",
        variant: "destructive",
      })
      setIsLoading(false)
    }
  }

  // Calculate body fat using Navy method (example for male)
  const calculateBodyFat = (neck: number, waist: number, hips: number, height: number, isMale: boolean) => {
    if (isMale) {
      return 495 / (1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(height)) - 450
    } else {
      return 495 / (1.29579 - 0.35004 * Math.log10(waist + hips - neck) + 0.22100 * Math.log10(height)) - 450
    }
  }

  // Mock user data
  const userData = {
    height: 180, // cm
    gender: "M",
  }

  // Calculate estimated body fat if all measurements are provided
  const estimatedBodyFat = newEntry.neck && newEntry.waist && newEntry.hips
    ? calculateBodyFat(
        parseFloat(newEntry.neck),
        parseFloat(newEntry.waist),
        parseFloat(newEntry.hips),
        userData.height,
        userData.gender === "M"
      )
    : null

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Track Progress</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Add New Measurements</CardTitle>
            <CardDescription>Record your latest stats</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="weight">Weight (lbs)</Label>
                <Input
                  id="weight"
                  name="weight"
                  type="number"
                  step="0.1"
                  placeholder="185.0"
                  value={newEntry.weight}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="neck">Neck (inches)</Label>
                <Input
                  id="neck"
                  name="neck"
                  type="number"
                  step="0.1"
                  placeholder="15.0"
                  value={newEntry.neck}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="waist">Waist (inches)</Label>
                <Input
                  id="waist"
                  name="waist"
                  type="number"
                  step="0.1"
                  placeholder="34.0"
                  value={newEntry.waist}
                  onChange={handleChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="hips">Hips (inches)</Label>
                <Input
                  id="hips"
                  name="hips"
                  type="number"
                  step="0.1"
                  placeholder="40.0"
                  value={newEntry.hips}
                  onChange={handleChange}
                  required
                />
              </div>
              
              {estimatedBodyFat !== null && (
                <div className="mt-4 p-4 bg-muted rounded-md">
                  <p className="text-sm font-medium">
                    Estimated Body Fat: {formatPercent(estimatedBodyFat / 100)}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Based on Navy Method calculation
                  </p>
                </div>
              )}
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Saving..." : "Save Measurements"}
              </Button>
            </CardFooter>
          </form>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Progress History</CardTitle>
            <CardDescription>Your recorded measurements</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {progressHistory.length === 0 ? (
                <p className="text-muted-foreground">No progress entries yet.</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b">
                        <th className="text-left py-2">Date</th>
                        <th className="text-right py-2">Weight</th>
                        <th className="text-right py-2">Body Fat</th>
                        <th className="text-right py-2">BMI</th>
                      </tr>
                    </thead>
                    <tbody>
                      {progressHistory.map((entry, index) => {
                        const bmi = calculateBMI(entry.weight, userData.height)
                        return (
                          <tr key={index} className="border-b">
                            <td className="py-2">{formatDate(entry.date)}</td>
                            <td className="text-right py-2">{formatWeight(entry.weight)}</td>
                            <td className="text-right py-2">{formatPercent(entry.bodyFat / 100)}</td>
                            <td className="text-right py-2">{bmi.toFixed(1)} ({getBMICategory(bmi)})</td>
                          </tr>
                        )
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Progress Visualization</CardTitle>
          <CardDescription>Your journey over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center border rounded">
            <p className="text-muted-foreground">Chart will be displayed here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}