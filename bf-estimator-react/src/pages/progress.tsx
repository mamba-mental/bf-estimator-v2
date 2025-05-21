import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent, calculateBMI, getBMICategory } from "@/lib/utils"
import { useAuth } from "@/contexts/auth-context"
import { supabase } from "@/lib/supabaseClient"

export default function Progress() {
  const { toast } = useToast()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  
  // Progress history state
  const [progressHistory, setProgressHistory] = useState<any[]>([])
  
  // User data state (height and gender)
  const [userData, setUserData] = useState({
    height: 180, // cm
    gender: "M",
  })
  
  const [newEntry, setNewEntry] = useState({
    weight: "",
    neck: "",
    waist: "",
    hips: "",
    bodyFat: "", // For manual entry
  })

  // Fetch user's profile and progress history on page load
  useEffect(() => {
    async function fetchData() {
      if (!user) return
      
      try {
        setIsFetching(true)
        
        // Fetch user profile for height and gender
        const { data: profileData, error: profileError } = await supabase
          .from('profiles')
          .select('*')
          .eq('id', user.id)
          .single()
        
        if (profileError) {
          console.error('Error fetching profile:', profileError)
        } else if (profileData) {
          setUserData({
            height: profileData.height || 180,
            gender: profileData.gender || "M",
          })
        }
        
        // Fetch progress history
        const { data: progressData, error: progressError } = await supabase
          .from('progress_entries')
          .select('*')
          .eq('user_id', user.id)
          .order('date', { ascending: false })
        
        if (progressError) {
          throw progressError
        }
        
        if (progressData) {
          // Transform the data to match the expected format
          const formattedData = progressData.map(entry => ({
            date: new Date(entry.date),
            weight: entry.weight,
            bodyFat: entry.body_fat_percentage,
            neck: entry.neck,
            waist: entry.waist,
            hips: entry.hips,
          }))
          
          setProgressHistory(formattedData)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
        toast({
          title: "Failed to load data",
          description: "There was a problem loading your progress data. Please refresh the page.",
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
    setNewEntry((prev: any) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: any) => {
    e.preventDefault()
    
    if (!user) {
      toast({
        title: "Authentication required",
        description: "Please log in to save your progress.",
        variant: "destructive",
      })
      return
    }
    
    setIsLoading(true)

    try {
      // Determine body fat percentage (use manual entry if provided, otherwise calculate)
      let bodyFatPercentage = newEntry.bodyFat 
        ? parseFloat(newEntry.bodyFat) 
        : calculateBodyFat(
            parseFloat(newEntry.neck),
            parseFloat(newEntry.waist),
            parseFloat(newEntry.hips),
            userData.height,
            userData.gender === "M"
          )
      
      // Prepare the data for Supabase
      const progressRecord = {
        user_id: user.id,
        date: new Date().toISOString().split('T')[0],
        weight: parseFloat(newEntry.weight),
        body_fat_percentage: bodyFatPercentage,
        neck: parseFloat(newEntry.neck),
        waist: parseFloat(newEntry.waist),
        hips: parseFloat(newEntry.hips),
        created_at: new Date().toISOString(),
      }
      
      // Insert the new progress entry
      const { data, error } = await supabase
        .from('progress_entries')
        .insert(progressRecord)
        .select()
      
      if (error) throw error
      
      // Update the local state with the new entry
      if (data && data.length > 0) {
        const newProgressEntry = {
          date: new Date(data[0].date),
          weight: data[0].weight,
          bodyFat: data[0].body_fat_percentage,
          neck: data[0].neck,
          waist: data[0].waist,
          hips: data[0].hips,
        }
        
        setProgressHistory([newProgressEntry, ...progressHistory])
      }
      
      toast({
        title: "Progress recorded",
        description: "Your new measurements have been saved successfully.",
      })
      
      // Reset the form
      setNewEntry({
        weight: "",
        neck: "",
        waist: "",
        hips: "",
        bodyFat: "",
      })
    } catch (error) {
      console.error('Error saving progress:', error)
      toast({
        title: "Entry failed",
        description: "There was a problem saving your progress. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  // Calculate body fat using Navy method
  const calculateBodyFat = (neck: number, waist: number, hips: number, height: number, isMale: boolean) => {
    if (isMale) {
      return 495 / (1.0324 - 0.19077 * Math.log10(waist - neck) + 0.15456 * Math.log10(height)) - 450
    } else {
      return 495 / (1.29579 - 0.35004 * Math.log10(waist + hips - neck) + 0.22100 * Math.log10(height)) - 450
    }
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

  if (isFetching) {
    return (
      <div className="container mx-auto p-6 flex justify-center items-center min-h-[50vh]">
        <p>Loading your progress data...</p>
      </div>
    )
  }

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
              <div className="space-y-2">
                <Label htmlFor="bodyFat">Body Fat % (optional)</Label>
                <Input
                  id="bodyFat"
                  name="bodyFat"
                  type="number"
                  step="0.1"
                  placeholder="Enter manually or use calculated value"
                  value={newEntry.bodyFat}
                  onChange={handleChange}
                />
                <p className="text-xs text-muted-foreground">
                  Leave blank to use Navy Method calculation
                </p>
              </div>
              
              {estimatedBodyFat !== null && !newEntry.bodyFat && (
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