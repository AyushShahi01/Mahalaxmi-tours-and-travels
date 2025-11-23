import { useSearchParams, Link } from "react-router-dom";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Calendar, Users, MapPin, Clock, CheckCircle, 
  Utensils, Bed, ArrowLeft, Heart, Loader2
} from "lucide-react";
import { getTourById, type TourPackage } from "@/data/tourPackages";

const TourDetails = () => {
  const [searchParams] = useSearchParams();
  const tourId = parseInt(searchParams.get('id') || '1');
  const [tour, setTour] = useState<TourPackage | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadTour = async () => {
      try {
        setLoading(true);
        const tourData = await getTourById(tourId);
        setTour(tourData || null);
      } catch (error) {
        console.error("Failed to load tour:", error);
      } finally {
        setLoading(false);
      }
    };

    loadTour();
  }, [tourId]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex justify-center items-center py-40">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
        </div>
        <Footer />
      </div>
    );
  }

  if (!tour) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center">
            <h1 className="text-3xl font-bold mb-4">Tour Not Found</h1>
            <p className="text-muted-foreground mb-6">The tour you're looking for doesn't exist.</p>
            <Link to="/">
              <Button>Back to Home</Button>
            </Link>
          </div>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section */}
      <section className="relative pt-20 pb-8">
        <div className="absolute inset-0 bg-gradient-to-r from-primary/20 to-secondary/20"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link to="/" className="inline-flex items-center text-primary hover:text-primary/80 mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tours
          </Link>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
                {tour.title}
              </h1>
              
              <p className="text-xl text-muted-foreground mb-6">
                {tour.description}
              </p>
              
              <div className="flex flex-wrap gap-6 text-sm text-muted-foreground mb-8">
                <div className="flex items-center">
                  <Clock className="h-4 w-4 mr-2" />
                  {tour.duration} Days
                </div>
                <div className="flex items-center">
                  <Users className="h-4 w-4 mr-2" />
                  {tour.groupSize} People
                </div>
              </div>
              
              <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div className="text-3xl md:text-4xl font-bold text-primary">
                  Rs{tour.price}
                  <span className="text-base md:text-lg font-normal text-muted-foreground ml-2">per person</span>
                </div>
                <div className="flex gap-2 sm:gap-3">
                  <Button variant="outline" size="lg" className="w-full sm:w-auto">
                    <Heart className="h-4 w-4 mr-2" />
                    <span className="hidden sm:inline">Save</span>
                  </Button>
                  <Link to={`/book-now?id=${tourId}`} className="w-full sm:w-auto">
                    <Button size="lg" className="bg-primary hover:bg-primary/90 w-full">
                      Book Now
                    </Button>
                  </Link>
                </div>
              </div>
            </div>
            
            <div className="relative">
              <div className="aspect-[4/3] bg-muted rounded-xl overflow-hidden">
                <img 
                  src={tour.image} 
                  alt={tour.title}
                  className="w-full h-full object-cover"
                  onError={(e) => {
                    e.currentTarget.src = 'https://imgs.search.brave.com/-norys9Fh4bCj0KPj0W7xUWcQqcZxzvMnP1y9JqEQVc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90NC5m/dGNkbi5uZXQvanBn/LzE2LzI4LzkzLzMx/LzM2MF9GXzE2Mjg5/MzMxNDhfWHFjU0F3/emZRZWQ2YTBZTkdl/T1RTQWZQOHdMNFY2/WUMuanBn';
                  }}
                />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Tour Details */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            
            {/* Main Content */}
            <div className="lg:col-span-2 space-y-8">
              
              {/* Highlights */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <MapPin className="h-5 w-5 mr-2" />
                    Tour Highlights
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {tour.highlights.map((highlight: string, index: number) => (
                      <div key={index} className="flex items-center">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-3 flex-shrink-0" />
                        <span>{highlight}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Itinerary */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <Calendar className="h-5 w-5 mr-2" />
                    Detailed Itinerary
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {tour.itinerary.map((day: string, index: number) => (
                      <div key={index} className="border-l-2 border-primary/20 pl-4 pb-4">
                        <div className="flex items-start">
                          <div className="w-6 h-6 bg-primary rounded-full flex items-center justify-center text-white text-xs font-bold -ml-[13px] mr-3 flex-shrink-0">
                            {index + 1}
                          </div>
                          <p className="text-foreground">{day}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* What's Included/Excluded */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-green-600 flex items-center">
                      <CheckCircle className="h-5 w-5 mr-2" />
                      What's Included
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {tour.included.map((item: string, index: number) => (
                        <li key={index} className="flex items-start text-sm">
                          <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                          {item}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-red-600">What's Not Included</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {tour.excluded.map((item: string, index: number) => (
                        <li key={index} className="flex items-start text-sm">
                          <div className="w-4 h-4 border border-red-300 rounded mr-2 mt-0.5 flex-shrink-0"></div>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              
              {/* Booking Card */}
              <Card className="sticky top-24">
                <CardHeader>
                  <CardTitle>Book This Tour</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-primary">Rs{tour.price}</div>
                    <div className="text-sm text-muted-foreground">per person</div>
                  </div>
                  
                  <div className="space-y-3 text-sm">
                    <div className="flex justify-between">
                      <span>Duration:</span>
                      <span className="font-medium">{tour.duration}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Group Size:</span>
                      <span className="font-medium">{tour.groupSize}</span>
                    </div>
                  </div>
                  
                  <div className="space-y-3 pt-4">
                    <Link to={`/book-now?id=${tourId}`}>
                      <Button className="w-full" size="lg">
                        Book Now
                      </Button>
                    </Link>
                    <Button variant="outline" className="w-full">
                      <Heart className="h-4 w-4 mr-2" />
                      Save for Later
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Quick Info */}
              <Card>
                <CardHeader>
                  <CardTitle>Quick Info</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex items-center text-sm">
                    <Bed className="h-4 w-4 mr-3 text-primary" />
                    <span>Tea house accommodation</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Utensils className="h-4 w-4 mr-3 text-primary" />
                    <span>All meals included</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <MapPin className="h-4 w-4 mr-3 text-primary" />
                    <span>Experienced guide</span>
                  </div>
                  <div className="flex items-center text-sm">
                    <Users className="h-4 w-4 mr-3 text-primary" />
                    <span>Porter service included</span>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default TourDetails;