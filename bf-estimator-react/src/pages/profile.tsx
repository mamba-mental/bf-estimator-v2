import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { useToast } from "@/components/ui/use-toast"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { useAuth } from "@/contexts/auth-context"
import { supabase } from "@/lib/supabaseClient"
import { convertCmToFeetInches, convertFeetInchesToCm } from "@/lib/height-utils"
import { ACTIVITY_LEVELS } from "@/lib/activity-levels"

export default function Profile() {
  const { toast } = useToast()
  const { user } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [profileData, setProfileData] = useState({
    name: "",
    email: "",
    height_cm: 180,
    age: 30,
    gender: "M",
    activity_level: 3,
  })

  // Separate state for feet and inches
  const [heightFeet, setHeightFeet] = useState(5)
  const [heightInches, setHeightInches] = useState(11)

  const [passwordData, setPasswordData] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  })

  // Fetch profile data on component mount
  useEffect(() => {
    if (user) {
      fetchProfileData()
    }
  }, [user])

  const fetchProfileData = async () => {
    if (!user) return

    setIsLoading(true)
    try {
      const { data, error } = await supabase
        .from('profiles')
        .select('*')
        .eq('id', user.id)
        .single()

      if (error) {
        throw error
      }

      if (data) {
        setProfileData({
          name: data.name || "",
          email: user.email || "",
          height_cm: data.height_cm || 180,
          age: data.age || 30,
          gender: data.gender || "M",
          activity_level: data.activity_level || 3,
        })

        // Convert height_cm to feet and inches
        const { feet, inches } = convertCmToFeetInches(data.height_cm || 180)
        setHeightFeet(feet)
        setHeightInches(inches)
      }
    } catch (error) {
      console.error('Error fetching profile:', error)
      toast({
        title: "Error fetching profile",
        description: "There was a problem loading your profile data.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleProfileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setProfileData((prev) => ({ ...prev, [name]: value }))
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setPasswordData((prev) => ({ ...prev, [name]: value }))
  }

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!user) return

    setIsLoading(true)

    try {
      // Convert feet and inches to cm
      const height_cm = convertFeetInchesToCm(heightFeet, heightInches)

      // Prepare profile data
      const profileUpdateData = {
        id: user.id,
        name: profileData.name,
        height_cm,
        age: profileData.age,
        gender: profileData.gender,
        activity_level: profileData.activity_level,
        updated_at: new Date().toISOString(),
      }

      // Update profile in Supabase
      const { error } = await supabase
        .from('profiles')
        .upsert(profileUpdateData, { onConflict: 'id' })

      if (error) {
        throw error
      }

      toast({
        title: "Profile updated",
        description: "Your profile information has been updated successfully.",
      })
    } catch (error) {
      console.error('Error updating profile:', error)
      toast({
        title: "Update failed",
        description: "There was a problem updating your profile. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast({
        title: "Passwords don't match",
        description: "Please make sure your new passwords match.",
        variant: "destructive",
      })
      return
    }
    
    setIsLoading(true)

    try {
      // Update password in Supabase
      const { error } = await supabase.auth.updateUser({
        password: passwordData.newPassword
      })

      if (error) {
        throw error
      }
      
      toast({
        title: "Password updated",
        description: "Your password has been changed successfully.",
      })
      setPasswordData({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
      })
    } catch (error) {
      toast({
        title: "Update failed",
        description: "There was a problem updating your password. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <h1 className="text-3xl font-bold">Profile Settings</h1>
      
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Update your personal details</CardDescription>
          </CardHeader>
          <form onSubmit={handleProfileSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Full Name</Label>
                <Input
                  id="name"
                  name="name"
                  value={profileData.name}
                  onChange={handleProfileChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  name="email"
                  type="email"
                  value={profileData.email}
                  onChange={handleProfileChange}
                  disabled
                  required
                />
                <p className="text-sm text-muted-foreground">Email cannot be changed</p>
              </div>
              <div className="space-y-2">
                <Label>Height</Label>
                <div className="flex gap-2">
                  <div className="w-1/2">
                    <Select
                      value={heightFeet.toString()}
                      onValueChange={(value) => setHeightFeet(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Feet" />
                      </SelectTrigger>
                      <SelectContent>
                        {[4, 5, 6, 7].map((feet) => (
                          <SelectItem key={feet} value={feet.toString()}>
                            {feet} ft
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="w-1/2">
                    <Select
                      value={heightInches.toString()}
                      onValueChange={(value) => setHeightInches(parseInt(value))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Inches" />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i).map((inches) => (
                          <SelectItem key={inches} value={inches.toString()}>
                            {inches} in
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground">
                  {convertFeetInchesToCm(heightFeet, heightInches).toFixed(1)} cm
                </p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  name="age"
                  type="number"
                  value={profileData.age}
                  onChange={handleProfileChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="gender">Gender</Label>
                <Select
                  value={profileData.gender}
                  onValueChange={(value) => setProfileData(prev => ({ ...prev, gender: value }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select gender" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="M">Male</SelectItem>
                    <SelectItem value="F">Female</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Activity Level</Label>
                <RadioGroup 
                  value={profileData.activity_level.toString()}
                  onValueChange={(value) => setProfileData(prev => ({ ...prev, activity_level: parseInt(value) }))}
                  className="space-y-3"
                >
                  {Object.entries(ACTIVITY_LEVELS).map(([level, description]) => (
                    <div key={level} className="flex items-start space-x-2">
                      <RadioGroupItem value={level} id={`activity-${level}`} className="mt-1" />
                      <div className="grid gap-1.5 leading-none">
                        <Label htmlFor={`activity-${level}`} className="font-medium">
                          Level {level}
                        </Label>
                        <p className="text-sm text-muted-foreground">
                          {description}
                        </p>
                      </div>
                    </div>
                  ))}
                </RadioGroup>
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Saving..." : "Save Changes"}
              </Button>
            </CardFooter>
          </form>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Change Password</CardTitle>
            <CardDescription>Update your password</CardDescription>
          </CardHeader>
          <form onSubmit={handlePasswordSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="currentPassword">Current Password</Label>
                <Input
                  id="currentPassword"
                  name="currentPassword"
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={handlePasswordChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="newPassword">New Password</Label>
                <Input
                  id="newPassword"
                  name="newPassword"
                  type="password"
                  value={passwordData.newPassword}
                  onChange={handlePasswordChange}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={handlePasswordChange}
                  required
                />
              </div>
            </CardContent>
            <CardFooter>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? "Updating..." : "Update Password"}
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}