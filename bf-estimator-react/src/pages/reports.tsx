import { useState, useEffect, useRef } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent, calculateBMI, getBMICategory } from "@/lib/utils"
import { useAuth } from "@/contexts/auth-context"
import {
  generateReportData,
  generateMockReportData,
  downloadJSONReport,
  downloadMarkdownReport,
  ReportData
} from "@/lib/reportingService"
import { AiReportCommentary } from "@/components/AiReportCommentary"
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
} from 'chart.js'
import jsPDF from 'jspdf'
import html2canvas from 'html2canvas'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

export default function Reports() {
  const { toast } = useToast()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [reportData, setReportData] = useState<ReportData | null>(null)
  const reportRef = useRef<HTMLDivElement>(null)
  
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
              description: "Could not fetch your data. Showing example report instead.",
              variant: "destructive",
            })
          }
        } else {
          // Use mock data if user is not authenticated
          setReportData(generateMockReportData())
        }
      } catch (error) {
        console.error("Error fetching report data:", error)
        toast({
          title: "Error",
          description: "Failed to generate report. Please try again later.",
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
  
  const handleDownloadJSON = () => {
    if (!reportData) return
    
    try {
      downloadJSONReport(reportData)
      toast({
        title: "Success",
        description: "JSON report downloaded successfully",
      })
    } catch (error) {
      console.error("Error downloading JSON report:", error)
      toast({
        title: "Error",
        description: "Failed to download JSON report",
        variant: "destructive",
      })
    }
  }
  
  const handleDownloadMarkdown = () => {
    if (!reportData) return
    
    try {
      downloadMarkdownReport(reportData)
      toast({
        title: "Success",
        description: "Markdown report downloaded successfully",
      })
    } catch (error) {
      console.error("Error downloading Markdown report:", error)
      toast({
        title: "Error",
        description: "Failed to download Markdown report",
        variant: "destructive",
      })
    }
  }
  
  const handleDownloadPDF = async () => {
    if (!reportData || !reportRef.current) return
    
    try {
      setIsLoading(true)
      toast({
        title: "Generating PDF",
        description: "Please wait while we generate your PDF report...",
      })
      
      const element = reportRef.current
      const canvas = await html2canvas(element, {
        scale: 2,
        logging: false,
        useCORS: true,
      })
      
      const imgData = canvas.toDataURL('image/png')
      const pdf = new jsPDF({
        orientation: 'portrait',
        unit: 'mm',
        format: 'a4',
      })
      
      const imgWidth = 210 // A4 width in mm
      const pageHeight = 295 // A4 height in mm
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      let heightLeft = imgHeight
      let position = 0
      
      pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
      heightLeft -= pageHeight
      
      // Add new pages if content overflows
      while (heightLeft > 0) {
        position = heightLeft - imgHeight
        pdf.addPage()
        pdf.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight)
        heightLeft -= pageHeight
      }
      
      const filename = `${reportData.name.replace(/\s+/g, '_')}_report_${new Date().toISOString().split('T')[0]}.pdf`
      pdf.save(filename)
      
      toast({
        title: "Success",
        description: "PDF report downloaded successfully",
      })
    } catch (error) {
      console.error("Error downloading PDF report:", error)
      toast({
        title: "Error",
        description: "Failed to download PDF report",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }
  
  // Prepare chart data for weight progress
  const weightChartData = {
    labels: reportData?.weeklyProgress.map(week => week.date.toLocaleDateString()) || [],
    datasets: [
      {
        label: 'Weight (lbs)',
        data: reportData?.weeklyProgress.map(week => week.weight) || [],
        borderColor: 'rgb(53, 162, 235)',
        backgroundColor: 'rgba(53, 162, 235, 0.5)',
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
  
  if (isLoading) {
    return (
      <div className="container mx-auto p-6 flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-lg">Loading your report data...</p>
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
            <CardDescription>We couldn't find any progress data to generate a report.</CardDescription>
          </CardHeader>
          <CardContent>
            <p>Please make sure you have logged your progress and set your goals.</p>
          </CardContent>
        </Card>
      </div>
    )
  }
  
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
        <h1 className="text-3xl font-bold">Progress Reports</h1>
        <div className="flex flex-wrap gap-2">
          <Button onClick={handleDownloadJSON} variant="outline">
            Download JSON
          </Button>
          <Button onClick={handleDownloadMarkdown} variant="outline">
            Download MD
          </Button>
          <Button onClick={handleDownloadPDF} variant="default">
            Download PDF
          </Button>
        </div>
      </div>
      
      <div ref={reportRef}>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle>Weight Loss Summary</CardTitle>
              <CardDescription>Your progress since {reportData.startDate.toLocaleDateString()}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Starting Weight:</span>
                <span className="font-medium">{formatWeight(reportData.weeklyProgress[0].weight)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Current Weight:</span>
                <span className="font-medium">{formatWeight(reportData.currentWeight)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Weight Lost:</span>
                <span className="font-medium">
                  {formatWeight(reportData.totalWeightLoss)} 
                  ({((reportData.totalWeightLoss / reportData.weeklyProgress[0].weight) * 100).toFixed(1)}%)
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Days Tracked:</span>
                <span className="font-medium">
                  {Math.round((new Date().getTime() - reportData.startDate.getTime()) / (1000 * 60 * 60 * 24))} days
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Average Weekly Loss:</span>
                <span className="font-medium">{reportData.avgWeeklyWeightLoss.toFixed(1)} lbs/week</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Body Composition</CardTitle>
              <CardDescription>Your body fat and BMI metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Starting Body Fat:</span>
                <span className="font-medium">{formatPercent(reportData.weeklyProgress[0].bodyFat / 100)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Current Body Fat:</span>
                <span className="font-medium">{formatPercent(reportData.currentBodyFat / 100)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Body Fat Reduced:</span>
                <span className="font-medium">{reportData.totalBodyFatLoss.toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Current BMI:</span>
                <span className="font-medium">{reportData.currentBMI.toFixed(1)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">BMI Category:</span>
                <span className="font-medium">{reportData.bmiCategory}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Energy Balance</CardTitle>
              <CardDescription>Your calorie metrics</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Current TDEE:</span>
                <span className="font-medium">{Math.round(reportData.tdee)} kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Recommended Intake:</span>
                <span className="font-medium">{Math.round(reportData.recommendedCalorieIntake)} kcal</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Daily Deficit:</span>
                <span className="font-medium">
                  {Math.round(reportData.tdee - reportData.recommendedCalorieIntake)} kcal
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Protein Target:</span>
                <span className="font-medium">{Math.round(reportData.currentWeight * 0.8)}g</span>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid gap-6 mt-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Weight Progress</CardTitle>
              <CardDescription>Your weight changes over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <Line options={chartOptions} data={weightChartData} />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Body Fat Progress</CardTitle>
              <CardDescription>Your body fat changes over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="h-[300px]">
                <Line options={chartOptions} data={bodyFatChartData} />
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Projection</CardTitle>
            <CardDescription>Estimated timeline to reach your goals</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current Rate of Loss:</span>
              <span className="font-medium">{reportData.avgWeeklyWeightLoss.toFixed(1)} lbs/week</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Target Weight:</span>
              <span className="font-medium">{reportData.goalWeight} lbs</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Weight Remaining:</span>
              <span className="font-medium">{(reportData.currentWeight - reportData.goalWeight).toFixed(1)} lbs</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Estimated Time to Goal:</span>
              <span className="font-medium">
                {Math.ceil((reportData.currentWeight - reportData.goalWeight) / reportData.avgWeeklyWeightLoss)} weeks
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Projected Goal Date:</span>
              <span className="font-medium">
                {formatDate(new Date(Date.now() + Math.ceil((reportData.currentWeight - reportData.goalWeight) / reportData.avgWeeklyWeightLoss) * 7 * 24 * 60 * 60 * 1000))}
              </span>
            </div>
          </CardContent>
        </Card>
        
        {/* AI-Generated Commentary */}
        <AiReportCommentary reportData={reportData} />

        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Weekly Progress Details</CardTitle>
            <CardDescription>Detailed breakdown of your weekly progress</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-2">Date</th>
                    <th className="text-left p-2">Weight</th>
                    <th className="text-left p-2">Body Fat</th>
                    <th className="text-left p-2">Lean Mass</th>
                    <th className="text-left p-2">Fat Mass</th>
                    <th className="text-left p-2">Weight Lost</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.weeklyProgress.map((week, index) => (
                    <tr key={index} className="border-b">
                      <td className="p-2">{week.date.toLocaleDateString()}</td>
                      <td className="p-2">{week.weight.toFixed(1)} lbs</td>
                      <td className="p-2">{week.bodyFat.toFixed(1)}%</td>
                      <td className="p-2">{week.leanMass.toFixed(1)} lbs</td>
                      <td className="p-2">{week.fatMass.toFixed(1)} lbs</td>
                      <td className="p-2">{week.totalWeightLost.toFixed(1)} lbs</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}