import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Users, MapPin, Clock, Loader2 } from "lucide-react";
import { Link } from "react-router-dom";
import { getTourPackages, type TourPackage } from "@/data/tourPackages";
import { useEffect, useState } from "react";

const TourPackages = () => {
  const [tourPackages, setTourPackages] = useState<TourPackage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [displayCount, setDisplayCount] = useState(6); // Show 6 tours initially

  useEffect(() => {
    const loadTourPackages = async () => {
      try {
        setLoading(true);
        const packages = await getTourPackages();
        setTourPackages(packages);
        setError(null);
      } catch (err) {
        console.error("Failed to load tour packages:", err);
        setError("Failed to load tour packages. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    loadTourPackages();
  }, []);

  const handleLoadMore = () => {
    setDisplayCount(prev => prev + 6); // Add 6 more tours
  };

  const displayedPackages = tourPackages.slice(0, displayCount);
  const hasMore = displayCount < tourPackages.length;

  return (
    <section id="packages" className="py-20 bg-background">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            Discover Nepal Tour Packages
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            From majestic Himalayan treks to cultural heritage tours, find your perfect Nepal adventure
          </p>
        </div>

        {loading && (
          <div className="flex justify-center items-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-primary" />
          </div>
        )}

        {error && (
          <div className="text-center py-10">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Retry</Button>
          </div>
        )}

        {!loading && !error && tourPackages.length === 0 && (
          <div className="text-center py-10">
            <p className="text-muted-foreground">No tour packages available at the moment.</p>
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {!loading && !error && displayedPackages.map((pkg) => (
            <Card key={pkg.id} className="group hover:shadow-lg transition-shadow duration-300 overflow-hidden">
              <div className="relative h-48 overflow-hidden">
                <img 
                  src={pkg.image} 
                  alt={pkg.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  onError={(e) => {
                    e.currentTarget.src = 'https://imgs.search.brave.com/-norys9Fh4bCj0KPj0W7xUWcQqcZxzvMnP1y9JqEQVc/rs:fit:860:0:0:0/g:ce/aHR0cHM6Ly90NC5m/dGNkbi5uZXQvanBn/LzE2LzI4LzkzLzMx/LzM2MF9GXzE2Mjg5/MzMxNDhfWHFjU0F3/emZRZWQ2YTBZTkdl/T1RTQWZQOHdMNFY2/WUMuanBn';
                  }}
                />
              </div>
              
              <CardHeader className="pb-3">
                <CardTitle className="text-xl group-hover:text-primary transition-colors">
                  {pkg.title}
                </CardTitle>
                <CardDescription className="text-sm">
                  {pkg.description}
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between text-sm text-muted-foreground">
                  <div className="flex items-center">
                    <Clock className="h-4 w-4 mr-1" />
                    {pkg.duration} Days
                  </div>
                  <div className="flex items-center">
                    <Users className="h-4 w-4 mr-1" />
                    {pkg.groupSize}
                  </div>
                </div>

                <div className="text-xl md:text-2xl font-bold text-primary text-right">
                  Rs {pkg.price}
                  <span className="text-sm font-normal text-muted-foreground ml-1">per person</span>
                </div>

                <div className="space-y-2">
                  <div className="text-sm font-medium text-foreground">Highlights:</div>
                  <div className="flex flex-wrap gap-1">
                    {pkg.highlights.slice(0, 2).map((highlight, index) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        <MapPin className="h-3 w-3 mr-1" />
                        {highlight}
                      </Badge>
                    ))}
                    {pkg.highlights.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{pkg.highlights.length - 2} more
                      </Badge>
                    )}
                  </div>
                </div>

                <div className="pt-4 space-y-2">
                  <Link to={`/book-now?id=${pkg.id}`}>
                    <Button className="w-full bg-primary hover:bg-primary/90">
                      Book Now
                    </Button>
                  </Link>
                  <Link to={`/tour-details?id=${pkg.id}`}>
                    <Button variant="outline" className="w-full">
                      View Details
                    </Button>
                  </Link>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {!loading && !error && hasMore && (
          <div className="text-center mt-12">
            <Button 
              variant="outline" 
              size="lg"
              onClick={handleLoadMore}
            >
              Load More Tours 
            </Button>
          </div>
        )}

        {!loading && !error && !hasMore && tourPackages.length > 0 && (
          <div className="text-center mt-12">
            <p className="text-muted-foreground">You've viewed all available tours</p>
          </div>
        )}
      </div>
    </section>
  );
};

export default TourPackages;