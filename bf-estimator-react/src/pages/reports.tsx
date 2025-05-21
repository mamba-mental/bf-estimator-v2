import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { formatDate, formatWeight, formatPercent, calculateBMI, getBMICategory } from "@/lib/utils"

export default function Reports() {
  const { toast } = useToast()
  
  // Mock progress data
  const progressHistory = [
    { date: new Date("2025-01-01"), weight: 195, bodyFat: 22, neck: 16, waist: 36, hips: 42 },
    { date: new Date("2025-02-01"), weight: 190, bodyFat: 20, neck: 15.5, waist: 35, hips: 41 },
    { date: new Date("2025-03-01"), weight: 187, bodyFat: 19, neck: 15.5, waist: 34, hips: 40 },
    { date: new Date("2025-04-01"), weight: 185, bodyFat: 18, neck: 15, waist: 33, hips: 39 },
  ]
  
  // Mock user data
  const userData = {
    height: 180, // cm
    gender: "M",
    age: 35,
    activityLevel: 3,
  }
  
  // Calculate stats
  const initialWeight = progressHistory[0].weight
  const currentWeight = progressHistory[progressHistory.length - 1].weight
  const weightLost = initialWeight - currentWeight
  const weightLostPercent = (weightLost / initialWeight) * 100
  
  const initialBodyFat = progressHistory[0].bodyFat
  const currentBodyFat = progressHistory[progressHistory.length - 1].bodyFat
  const bodyFatLost = initialBodyFat - currentBodyFat
  
  const startDate = progressHistory[0].date
  const currentDate = progressHistory[progressHistory.length - 1].date
  const daysPassed = Math.round((currentDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
  
  const weightLostPerWeek = (weightLost / daysPassed) * 7
  
  // Calculate current BMI
  const currentBMI = calculateBMI(currentWeight, userData.height)
  const bmiCategory = getBMICategory(currentBMI)
  
  // Calculate TDEE (Total Daily Energy Expenditure)
  const calculateTDEE = (weight: number, heightCm: number, age: number, gender: string, activityLevel: number) => {
    // Convert weight to kg
    const weightKg = weight * 0.453592
    
    // Calculate BMR using Mifflin-St Jeor Equation
    let bmr
    if (gender.toLowerCase() === "m") {
      bmr = 10 * weightKg + 6.25 * heightCm - 5 * age + 5
    } else {
      bmr = 10 * weightKg + 6.25 * heightCm - 5 * age - 161
    }
    
    // Activity multipliers
    const activityMultipliers = [1.2, 1.375, 1.55, 1.725, 1.9]
    const multiplier = activityMultipliers[activityLevel - 1] || 1.2
    
    return Math.round(bmr * multiplier)
  }
  
  const tdee = calculateTDEE(currentWeight, userData.height, userData.age, userData.gender, userData.activityLevel)
  
  // Calculate average daily calorie deficit
  const calorieDeficit = Math.round((weightLost * 3500) / daysPassed)

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Progress Reports</h1>
      
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>Weight Loss Summary</CardTitle>
            <CardDescription>Your progress since {formatDate(startDate)}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Starting Weight:</span>
              <span className="font-medium">{formatWeight(initialWeight)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current Weight:</span>
              <span className="font-medium">{formatWeight(currentWeight)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Weight Lost:</span>
              <span className="font-medium">{formatWeight(weightLost)} ({weightLostPercent.toFixed(1)}%)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Days Tracked:</span>
              <span className="font-medium">{daysPassed} days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Average Weekly Loss:</span>
              <span className="font-medium">{weightLostPerWeek.toFixed(1)} lbs/week</span>
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
              <span className="font-medium">{formatPercent(initialBodyFat / 100)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current Body Fat:</span>
              <span className="font-medium">{formatPercent(currentBodyFat / 100)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Body Fat Reduced:</span>
              <span className="font-medium">{bodyFatLost.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current BMI:</span>
              <span className="font-medium">{currentBMI.toFixed(1)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">BMI Category:</span>
              <span className="font-medium">{bmiCategory}</span>
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
              <span className="font-medium">{tdee} kcal</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Avg. Daily Deficit:</span>
              <span className="font-medium">{calorieDeficit} kcal</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Recommended Intake:</span>
              <span className="font-medium">{tdee - 500} kcal</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Protein Target:</span>
              <span className="font-medium">{Math.round(currentWeight * 0.8)}g</span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Detailed Progress Chart</CardTitle>
          <CardDescription>Your measurements over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px] flex items-center justify-center border rounded">
            <p className="text-muted-foreground">Chart will be displayed here</p>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Projection</CardTitle>
          <CardDescription>Estimated timeline to reach your goals</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Current Rate of Loss:</span>
            <span className="font-medium">{weightLostPerWeek.toFixed(1)} lbs/week</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Target Weight:</span>
            <span className="font-medium">175 lbs</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Weight Remaining:</span>
            <span className="font-medium">{(currentWeight - 175).toFixed(1)} lbs</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Estimated Time to Goal:</span>
            <span className="font-medium">{Math.ceil((currentWeight - 175) / weightLostPerWeek)} weeks</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Projected Goal Date:</span>
            <span className="font-medium">
              {formatDate(new Date(Date.now() + Math.ceil((currentWeight - 175) / weightLostPerWeek) * 7 * 24 * 60 * 60 * 1000))}
            </span>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}