import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useToast } from "@/components/ui/use-toast";
import { Utensils, RefreshCw } from "lucide-react";
import { getMealSuggestions, DailyMealPlan, MealSuggestion } from "@/lib/aiService";
import { useAuth } from "@/contexts/auth-context";

export function AiMealSuggestions() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [mealPlan, setMealPlan] = useState<DailyMealPlan | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (user) {
      fetchMealPlan();
    }
  }, [user]);

  const fetchMealPlan = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const plan = await getMealSuggestions(user.id);
      setMealPlan(plan);
    } catch (error) {
      console.error("Error fetching meal suggestions:", error);
      toast({
        title: "Error",
        description: "Failed to load meal suggestions. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const refreshMealPlan = () => {
    fetchMealPlan();
    toast({
      title: "Refreshing Meal Plan",
      description: "Generating new personalized meal suggestions...",
    });
  };

  // Helper function to get meal type icon and color
  const getMealTypeStyles = (mealType: string) => {
    switch (mealType) {
      case 'breakfast':
        return { color: 'text-yellow-500', bgColor: 'bg-yellow-100' };
      case 'lunch':
        return { color: 'text-green-500', bgColor: 'bg-green-100' };
      case 'dinner':
        return { color: 'text-blue-500', bgColor: 'bg-blue-100' };
      case 'snack':
        return { color: 'text-purple-500', bgColor: 'bg-purple-100' };
      default:
        return { color: 'text-gray-500', bgColor: 'bg-gray-100' };
    }
  };

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-xl flex items-center">
            <Utensils className="h-5 w-5 mr-2 text-primary" />
            Meal Suggestions
          </CardTitle>
          <CardDescription>
            AI-generated meal ideas based on your calorie needs
          </CardDescription>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={refreshMealPlan}
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center">
              <span className="animate-spin h-4 w-4 mr-2 border-b-2 border-primary rounded-full"></span>
              Loading
            </span>
          ) : (
            <span className="flex items-center">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </span>
          )}
        </Button>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : mealPlan ? (
          <div className="space-y-6">
            <div className="bg-muted/50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-semibold">Daily Targets</h3>
                <span className="text-sm text-muted-foreground">Based on your TDEE</span>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-background p-3 rounded-md text-center">
                  <p className="text-sm text-muted-foreground">Calories</p>
                  <p className="text-xl font-bold">{mealPlan.totalCalories}</p>
                </div>
                <div className="bg-background p-3 rounded-md text-center">
                  <p className="text-sm text-muted-foreground">Protein</p>
                  <p className="text-xl font-bold">{mealPlan.targetProtein}g</p>
                </div>
              </div>
            </div>
            
            <div className="space-y-4">
              {mealPlan.meals.map((meal, index) => {
                const { color, bgColor } = getMealTypeStyles(meal.mealType);
                return (
                  <div key={index} className="border rounded-lg overflow-hidden">
                    <div className={`${bgColor} px-4 py-2 flex justify-between items-center`}>
                      <h3 className={`font-medium capitalize ${color}`}>
                        {meal.mealType}
                      </h3>
                      <span className="text-sm font-medium">{meal.calories} kcal</span>
                    </div>
                    <div className="p-4">
                      <h4 className="font-semibold text-lg mb-1">{meal.name}</h4>
                      <p className="text-sm text-muted-foreground mb-3">{meal.description}</p>
                      <div className="flex space-x-4 text-xs">
                        <div>
                          <span className="font-medium">Protein:</span> {meal.protein}g
                        </div>
                        <div>
                          <span className="font-medium">Carbs:</span> {meal.carbs}g
                        </div>
                        <div>
                          <span className="font-medium">Fat:</span> {meal.fat}g
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
            
            <div className="text-xs text-muted-foreground mt-4 pt-2 border-t">
              <em>Generated by AI based on your calorie needs. Adjust portions as needed to meet your specific requirements.</em>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            <p>No meal suggestions available. Click refresh to generate a meal plan.</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}