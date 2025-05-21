import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { useToast } from "@/components/ui/use-toast"
import { useAuth } from "@/contexts/auth-context"
import {
  generateReportData,
  generateMockReportData,
  ReportData
} from "@/lib/reportingService"
import { AiTipsCard } from "@/components/AiTipsCard"
import { AiMealSuggestions } from "@/components/AiMealSuggestions"
import { formatDate, formatWeight, formatPercent } from "@/lib/utils"
import { Line } from "react-chartjs-2"
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

export default function Dashboard() {
  const { toast } = useToast()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [reportData, setReportData] = useState<ReportData | null>(null)

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        if (user) {
          // Fetch real data if user is authenticated
          const data = await generateReportData(user.id)
          if (data) {
            setReportData(data)
          } else {
            // Fall back to mock data if real data fetch fails
            setReportData(generateMockReportData())
            toast({
              title: "Using mock data",
              description: "Could not fetch your data. Showing example dashboard instead.",
              variant: "destructive",
            })
          }
        } else {
          // Use mock data if user is not authenticated
          setReportData(generateMockReportData())
          toast({
            title: "Welcome to BF Estimator",
            description: "Track your fitness journey and body fat percentage",
          })
        }
      } catch (error) {
        console.error("Error fetching report data:", error)
        toast({
          title: "Error",
          description: "Failed to load dashboard data. Please try again later.",
          variant: "destructive",
        })
        // Fall back to mock data
        setReportData(generateMockReportData())
      } finally {
        setIsLoading(false)
      }
    }
    
    fetchData()
  }, [user, toast])

  // Prepare chart data for weight progress
  const weightChartData = {
    labels: reportData?.weeklyProgress.map(week => week.date.toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Weight (lbs)',
        data: reportData?.weeklyProgress.map(week => week.weight) || [],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
        tension: 0.3,
      },
    ],
  }
  
  // Prepare chart data for body fat progress
  const bodyFatChartData = {
    labels: reportData?.weeklyProgress.map(week => week.date.toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Body Fat %',
        data: reportData?.weeklyProgress.map(week => week.bodyFat) || [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.3,
      },
    ],
  }

  // Prepare chart data for lean mass vs fat mass
  const compositionChartData = {
    labels: reportData?.weeklyProgress.map(week => week.date.toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Lean Mass (lbs)',
        data: reportData?.weeklyProgress.map(week => week.leanMass) || [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        tension: 0.3,
      },
      {
        label: 'Fat Mass (lbs)',
        data: reportData?.weeklyProgress.map(week => week.fatMass) || [],
        borderColor: 'rgb(255, 159, 64)',
        backgroundColor: 'rgba(255, 159, 64, 0.5)',
        tension: 0.3,
      },
    ],
  }

  // Prepare chart data for calorie balance
  const calorieChartData = {
    labels: reportData?.weeklyProgress.map(week => week.date.toLocaleDateString()) || [],
    datasets: [
      {
        label: 'TDEE (kcal)',
        data: reportData?.weeklyProgress.map(week => week.tdee) || [],
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.5)',
        tension: 0.3,
      },
      {
        label: 'Daily Intake (kcal)',
        data: reportData?.weeklyProgress.map(week => week.dailyCalorieIntake) || [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
        tension: 0.3,
      },
    ],
  }
  
  // Chart options
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: false,
      },
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
  }

  // Calculate progress percentage
  const calculateProgressPercentage = () => {
    if (!reportData) return 0
    
    const totalWeightToLose = reportData.weeklyProgress[0].weight - reportData.goalWeight
    const weightLostSoFar = reportData.weeklyProgress[0].weight - reportData.currentWeight
    
    if (totalWeightToLose <= 0) return 100
    
    const percentage = (weightLostSoFar / totalWeightToLose) * 100
    return Math.min(Math.max(percentage, 0), 100) // Clamp between 0 and 100
  }

  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg">Loading your dashboard data...</p>
        </div>
      </div>
    )
  }

  if (!reportData) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>No Data Available</CardTitle>
            <CardDescription>We couldn't find any progress data to display.</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Please make sure you have logged your progress and set your goals.</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  const progressPercentage = calculateProgressPercentage()

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {/* Summary Cards */}
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
                <span className="font-medium">{formatWeight(reportData.currentWeight)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Body Fat:</span>
                <span className="font-medium">{formatPercent(reportData.currentBodyFat / 100)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">BMI:</span>
                <span className="font-medium">{reportData.currentBMI.toFixed(1)} ({reportData.bmiCategory})</span>
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
            <div className="space-y-4">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Target Weight:</span>
                  <span className="font-medium">{formatWeight(reportData.goalWeight)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Target Body Fat:</span>
                  <span className="font-medium">{formatPercent(reportData.goalBodyFat / 100)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Target Date:</span>
                  <span className="font-medium">{formatDate(reportData.targetDate)}</span>
                </div>
              </div>
              
              <div className="space-y-1">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Progress:</span>
                  <span className="font-medium">{progressPercentage.toFixed(0)}%</span>
                </div>
                <Progress value={progressPercentage} className="h-2" />
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
                <span className="font-medium">{Math.round(reportData.tdee).toLocaleString()} kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Target Intake:</span>
                <span className="font-medium">{Math.round(reportData.recommendedCalorieIntake).toLocaleString()} kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Deficit:</span>
                <span className="font-medium">{Math.round(reportData.tdee - reportData.recommendedCalorieIntake).toLocaleString()} kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Protein Goal:</span>
                <span className="font-medium">{Math.round(reportData.currentWeight * 0.8)}g</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Weight Loss Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Weight Loss Progress</CardTitle>
          <CardDescription>Your weight changes over time</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Total Weight Lost</p>
              <p className="text-3xl font-bold">{formatWeight(reportData.totalWeightLoss)}</p>
              <p className="text-sm text-muted-foreground">
                {((reportData.totalWeightLoss / reportData.weeklyProgress[0].weight) * 100).toFixed(1)}% of starting weight
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Weekly Average</p>
              <p className="text-3xl font-bold">{reportData.avgWeeklyWeightLoss.toFixed(1)} lbs</p>
              <p className="text-sm text-muted-foreground">per week</p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Remaining</p>
              <p className="text-3xl font-bold">{(reportData.currentWeight - reportData.goalWeight).toFixed(1)} lbs</p>
              <p className="text-sm text-muted-foreground">
                Est. {Math.ceil((reportData.currentWeight - reportData.goalWeight) / reportData.avgWeeklyWeightLoss)} weeks left
              </p>
            </div>
          </div>
          
          <div className="h-[300px]">
            <Line options={chartOptions} data={weightChartData} />
          </div>
        </CardContent>
      </Card>

      {/* Body Composition */}
      <Card>
        <CardHeader>
          <CardTitle>Body Composition</CardTitle>
          <CardDescription>Your body fat and lean mass changes</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Body Fat Reduced</p>
              <p className="text-3xl font-bold">{reportData.totalBodyFatLoss.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">
                From {reportData.weeklyProgress[0].bodyFat.toFixed(1)}% to {reportData.currentBodyFat.toFixed(1)}%
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Fat Mass Lost</p>
              <p className="text-3xl font-bold">
                {(reportData.weeklyProgress[0].fatMass - reportData.currentFatMass).toFixed(1)} lbs
              </p>
              <p className="text-sm text-muted-foreground">
                {((reportData.weeklyProgress[0].fatMass - reportData.currentFatMass) / reportData.weeklyProgress[0].fatMass * 100).toFixed(1)}% reduction
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Muscle Gained</p>
              <p className="text-3xl font-bold">{reportData.totalMuscleGain.toFixed(1)} lbs</p>
              <p className="text-sm text-muted-foreground">
                {(reportData.totalMuscleGain / reportData.weeklyProgress[0].leanMass * 100).toFixed(1)}% increase
              </p>
            </div>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2">
            <div className="h-[300px]">
              <Line options={chartOptions} data={bodyFatChartData} />
            </div>
            <div className="h-[300px]">
              <Line options={chartOptions} data={compositionChartData} />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Energy Balance */}
      <Card>
        <CardHeader>
          <CardTitle>Energy Balance</CardTitle>
          <CardDescription>Your calorie metrics and metabolic adaptation</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid gap-6 md:grid-cols-3">
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Daily Deficit</p>
              <p className="text-3xl font-bold">{Math.round(reportData.tdee - reportData.recommendedCalorieIntake)} kcal</p>
              <p className="text-sm text-muted-foreground">
                {((reportData.tdee - reportData.recommendedCalorieIntake) / reportData.tdee * 100).toFixed(0)}% of TDEE
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Metabolic Adaptation</p>
              <p className="text-3xl font-bold">{reportData.adaptationPercentage.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">
                reduction in metabolic rate
              </p>
            </div>
            <div className="bg-muted/50 p-4 rounded-lg text-center">
              <p className="text-muted-foreground text-sm mb-1">Lean Mass Preserved</p>
              <p className="text-3xl font-bold">{reportData.leanMassPreservation.toFixed(1)}%</p>
              <p className="text-sm text-muted-foreground">
                {reportData.leanMassPreservation > 100 ? 'Gained muscle!' : 'Maintained muscle'}
              </p>
            </div>
          </div>
          
          <div className="h-[300px]">
            <Line options={chartOptions} data={calorieChartData} />
          </div>
        </CardContent>
      </Card>
      {/* AI-Powered Features */}
      <div className="grid gap-6 md:grid-cols-2">
        <AiTipsCard />
        <AiMealSuggestions />
      </div>
    </div>
  )
}