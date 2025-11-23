import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { vehicles } from "@/data/vehicles";
import { Car, Users, DollarSign } from "lucide-react";
import { useNavigate } from "react-router-dom";

const Vehicles = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen">
      <Navbar />
      
      {/* Hero Section */}
      <section className="pt-32 pb-16 px-4 bg-gradient-to-b from-adventure-mountain/20 to-background">
        <div className="container mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            Our Fleet
          </h1>
          <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto">
            Choose from our diverse range of well-maintained vehicles for your Nepal adventure. 
            All vehicles come with experienced drivers and are regularly serviced for your safety.
          </p>
        </div>
      </section>

      {/* Vehicle Gallery */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {vehicles.map((vehicle) => (
              <Card key={vehicle.id} className="overflow-hidden hover:shadow-lg transition-shadow">
                <div className="aspect-video overflow-hidden">
                  <img
                    src={vehicle.image}
                    alt={vehicle.name}
                    className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                  />
                </div>
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <CardTitle className="text-2xl">{vehicle.name}</CardTitle>
                    <div className="flex items-center gap-1 text-primary">
                      <DollarSign className="w-5 h-5" />
                      <span className="font-bold">{vehicle.pricePerDay}/day</span>
                    </div>
                  </div>
                  <CardDescription className="flex items-center gap-4">
                    <span className="flex items-center gap-1">
                      <Car className="w-4 h-4" />
                      {vehicle.type}
                    </span>
                    <span className="flex items-center gap-1">
                      <Users className="w-4 h-4" />
                      {vehicle.capacity} seats
                    </span>
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground mb-4">{vehicle.description}</p>
                  <div className="space-y-2">
                    <h4 className="font-semibold">Features:</h4>
                    <ul className="grid grid-cols-2 gap-2 text-sm">
                      {vehicle.features.map((feature, index) => (
                        <li key={index} className="flex items-center gap-2">
                          <span className="w-1.5 h-1.5 rounded-full bg-primary" />
                          {feature}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
                <CardFooter>
                  <Button 
                    className="w-full"
                    onClick={() => navigate('/contact')}
                  >
                    Inquire Now
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 bg-gradient-to-b from-background to-adventure-mountain/20">
        <div className="container mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Need a Custom Vehicle Solution?
          </h2>
          <p className="text-lg text-muted-foreground mb-8 max-w-2xl mx-auto">
            Have specific requirements? Contact us for customized vehicle arrangements 
            tailored to your tour needs.
          </p>
          <Button size="lg" onClick={() => navigate('/contact')}>
            Contact Us
          </Button>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Vehicles;
