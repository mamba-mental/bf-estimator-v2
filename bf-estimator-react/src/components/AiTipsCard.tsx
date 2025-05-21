import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import { Sparkles } from "lucide-react";
import { getPersonalizedTips, PersonalizedTip } from "@/lib/aiService";
import { useAuth } from "@/contexts/auth-context";

export function AiTipsCard() {
  const { toast } = useToast();
  const { user } = useAuth();
  const [tips, setTips] = useState<PersonalizedTip[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    if (user) {
      fetchTips();
    }
  }, [user]);

  const fetchTips = async () => {
    if (!user) return;
    
    setIsLoading(true);
    try {
      const fetchedTips = await getPersonalizedTips(user.id);
      setTips(fetchedTips);
    } catch (error) {
      console.error("Error fetching AI tips:", error);
      toast({
        title: "Error",
        description: "Failed to load personalized tips. Please try again later.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const refreshTips = () => {
    fetchTips();
    toast({
      title: "Refreshing Tips",
      description: "Generating new personalized tips for you...",
    });
  };

  const filteredTips = activeTab === "all" 
    ? tips 
    : tips.filter(tip => tip.category === activeTab);

  return (
    <Card className="h-full">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <div>
          <CardTitle className="text-xl flex items-center">
            <Sparkles className="h-5 w-5 mr-2 text-yellow-500" />
            AI-Powered Tips
          </CardTitle>
          <CardDescription>
            Personalized recommendations for your fitness journey
          </CardDescription>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={refreshTips}
          disabled={isLoading}
        >
          {isLoading ? (
            <span className="flex items-center">
              <span className="animate-spin h-4 w-4 mr-2 border-b-2 border-primary rounded-full"></span>
              Loading
            </span>
          ) : (
            "Refresh"
          )}
        </Button>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="all" value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid grid-cols-4 mb-4">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="nutrition">Nutrition</TabsTrigger>
            <TabsTrigger value="fitness">Fitness</TabsTrigger>
            <TabsTrigger value="lifestyle">Lifestyle</TabsTrigger>
          </TabsList>
          
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : filteredTips.length > 0 ? (
            <div className="space-y-4">
              {filteredTips.map((tip, index) => (
                <div key={index} className="bg-muted/50 p-4 rounded-lg">
                  <h3 className="font-semibold text-lg mb-1">{tip.title}</h3>
                  <p className="text-muted-foreground">{tip.content}</p>
                  <div className="mt-2">
                    <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded-full">
                      {tip.category.charAt(0).toUpperCase() + tip.category.slice(1)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <p>No tips available. Click refresh to generate new tips.</p>
            </div>
          )}
        </Tabs>
      </CardContent>
    </Card>
  );
}