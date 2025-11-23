import { useSearchParams, Link, useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/hooks/use-toast";
import { 
  ArrowLeft, Shield, CreditCard, 
  CheckCircle, Clock, MapPin, Loader2
} from "lucide-react";
import { getTourById, type TourPackage } from "@/data/tourPackages";
import { bookWithEsewa } from "@/api/booking_api";

const BookNow = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const tourId = parseInt(searchParams.get('id') || '1');
  const [tour, setTour] = useState<TourPackage | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [numberOfTickets, setNumberOfTickets] = useState(1);
  
  // Form state
  const [formData, setFormData] = useState({
    travelerId: '', // Optional: existing traveler ID
    fullName: '',
    email: '',
    phone: '',
    address: '',
    departureDate: '',
  });

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

  // Calculate total amount based on number of tickets
  const calculateTotal = () => {
    if (!tour) return 0;
    return tour.price * numberOfTickets;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.id]: e.target.value
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tour) return;

    // Validate all required fields
    const requiredFields = {
      'Full Name': formData.fullName,
      'Email': formData.email,
      'Phone': formData.phone,
      'Address': formData.address
    };

    const missingFields = Object.entries(requiredFields)
      .filter(([_, value]) => !value || value.trim() === '')
      .map(([field, _]) => field);

    if (missingFields.length > 0) {
      toast({
        title: "Missing Information",
        description: `Please fill in: ${missingFields.join(', ')}`,
        variant: "destructive",
      });
      return;
    }

    setSubmitting(true);

    try {
      // Prepare booking data for eSewa v2 API
      // Ensure all fields are non-empty strings
      const bookingData = {
        package_id: parseInt(tourId as string),
        payment_amount: calculateTotal(),
        traveler_name: formData.fullName.trim(),
        traveler_email: formData.email.trim(),
        traveler_phone: formData.phone.trim(),
        traveler_address: formData.address.trim()
      };

      // Log the data being sent for debugging
      console.log('Submitting booking data:', bookingData);

      // Step 1: Initiate eSewa v2 payment with HMAC signature
      const response = await bookWithEsewa(bookingData);
      
      console.log("Booking API response:", response); // Debug log
      
      if (response && response.success && response.payment_url && response.payment_form_data) {
        // Store booking reference and traveler info for verification callback
        sessionStorage.setItem('booking_reference', response.booking_reference);
        sessionStorage.setItem('booking_data', JSON.stringify(response.booking_data));
        sessionStorage.setItem('package_info', JSON.stringify({
          id: tourId,
          title: tour.title,
          price: tour.price,
          amount: calculateTotal()
        }));

        // Step 2: Create hidden form with eSewa v2 parameters (including HMAC signature)
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = response.payment_url; // v2 API URL with signature
        form.style.display = 'none';

        // Add all eSewa v2 payment fields (amount, tax_amount, total_amount, transaction_uuid, signature, etc.)
        Object.entries(response.payment_form_data).forEach(([key, value]) => {
          const input = document.createElement('input');
          input.type = 'hidden';
          input.name = key;
          input.value = String(value);
          form.appendChild(input);
        });

        document.body.appendChild(form);
        
        toast({
          title: "Redirecting to eSewa",
          description: "Please complete your payment on eSewa v2.",
        });

        // Submit form to redirect to eSewa v2
        form.submit();

      } else {
        throw new Error(response?.message || "Invalid response from server");
      }

    } catch (error: any) {
      console.error("Booking failed:", error);
      
      // Detailed error message for debugging
      let errorMessage = "There was an error processing your booking. Please try again.";
      
      if (error?.response) {
        // Server responded with error
        console.error("Server error response:", error.response.data);
        errorMessage = error.response.data?.message || 
                      error.response.data?.error || 
                      `Server error: ${error.response.status}`;
      } else if (error?.request) {
        // Request made but no response
        console.error("No response from server:", error.request);
        errorMessage = "Cannot connect to server. Please check if the backend is running on http://127.0.0.1:8000";
      } else {
        // Other error
        console.error("Error details:", error.message);
        errorMessage = error.message;
      }
      
      toast({
        title: "Booking Failed",
        description: errorMessage,
        variant: "destructive",
      });
      setSubmitting(false);
    }
  };

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
      
      {/* Header */}
      <section className="pt-20 pb-8 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <Link to={`/tour-details?id=${tourId}`} className="inline-flex items-center text-primary hover:text-primary/80 mb-6">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Tour Details
          </Link>
          
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
              Book Your Adventure
            </h1>
            <p className="text-xl text-muted-foreground">
              Complete your booking for {tour.title}
            </p>
          </div>
        </div>
      </section>

      {/* Booking Form */}
      <section className="py-16 bg-background">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            
            {/* Booking Form */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-2xl">Booking Information</CardTitle>
                  <p className="text-muted-foreground">
                    Please fill in your details to complete your booking
                  </p>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleSubmit} className="space-y-6">
                    
                    {/* Booking Details */}
                    <div className="space-y-4">
                      <h3 className="text-lg font-semibold border-b pb-2">Traveler Information</h3>
                      
                      {/* <div className="space-y-2">
                        <Label htmlFor="travelerId">Traveler ID (Optional)</Label>
                        <Input 
                          id="travelerId" 
                          placeholder="Enter your traveler ID if you have one" 
                          value={formData.travelerId}
                          onChange={handleInputChange}
                        />
                        <p className="text-xs text-muted-foreground">
                          If you have booked with us before, enter your traveler ID. Otherwise, fill in the details below.
                        </p>
                      </div> */}

                      <div className="space-y-2">
                        <Label htmlFor="fullName">Full Name *</Label>
                        <Input 
                          id="fullName" 
                          placeholder="Enter your full name" 
                          value={formData.fullName}
                          onChange={handleInputChange}
                          required={!formData.travelerId}
                          disabled={!!formData.travelerId}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="email">Email Address *</Label>
                        <Input 
                          id="email" 
                          type="email"
                          placeholder="your.email@example.com" 
                          value={formData.email}
                          onChange={handleInputChange}
                          required={!formData.travelerId}
                          disabled={!!formData.travelerId}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="phone">Phone Number *</Label>
                        <Input 
                          id="phone" 
                          type="tel" 
                          placeholder="+977-9841234567" 
                          value={formData.phone}
                          onChange={handleInputChange}
                          required={!formData.travelerId}
                          disabled={!!formData.travelerId}
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="address">Address *</Label>
                        <Textarea 
                          id="address" 
                          placeholder="Enter your full address"
                          rows={3}
                          value={formData.address}
                          onChange={handleInputChange}
                          required={!formData.travelerId}
                          disabled={!!formData.travelerId}
                        />
                      </div>
                      
                      <div className="space-y-2">
                        <Label htmlFor="departureDate">Departure Date *</Label>
                        <Input 
                          id="departureDate" 
                          type="date" 
                          value={formData.departureDate}
                          onChange={handleInputChange}
                          required 
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="numberOfTickets">Number of Tickets *</Label>
                        <Input 
                          id="numberOfTickets" 
                          type="number" 
                          min="1"
                          max="20"
                          value={numberOfTickets}
                          onChange={(e) => setNumberOfTickets(parseInt(e.target.value) || 1)}
                          required 
                        />
                        <p className="text-xs text-muted-foreground">
                          Price per ticket: Rs {tour?.price.toLocaleString()}
                        </p>
                      </div>
                    </div>

                    {/* Total Amount Display */}
                    <div className="bg-muted/50 p-4 rounded-lg">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm">Tickets:</span>
                        <span className="text-sm font-medium">{numberOfTickets} × Rs {tour?.price.toLocaleString()}</span>
                      </div>
                      <div className="border-t pt-2 flex justify-between items-center">
                        <span className="font-semibold">Total Amount:</span>
                        <span className="text-2xl font-bold text-primary">
                          Rs {calculateTotal().toLocaleString()}
                        </span>
                      </div>
                    </div>

                    {/* Submit Button */}
                    <div className="pt-4">
                      <Button 
                        type="submit" 
                        className="w-full" 
                        size="lg"
                        disabled={submitting}
                      >
                        {submitting ? (
                          <>
                            <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                            Processing...
                          </>
                        ) : (
                          <>
                            <CreditCard className="h-5 w-5 mr-2" />
                            Confirm Booking
                          </>
                        )}
                      </Button>
                      <p className="text-xs text-muted-foreground text-center mt-3">
                        🔒 Secure booking • Contact us for payment details
                      </p>
                    </div>
                  </form>
                </CardContent>
              </Card>
            </div>

            {/* Booking Summary */}
            <div className="sticky top-24 space-y-6">
              
              {/* Tour Summary */}
              <Card>
                <CardHeader>
                  <CardTitle>Booking Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  
                  {/* Tour Info */}
                  <div className="space-y-3">
                    <h4 className="font-semibold text-lg">{tour.title}</h4>
                    
                    <div className="space-y-2 text-sm text-muted-foreground">
                      <div className="flex items-center">
                        <Clock className="h-4 w-4 mr-2" />
                        {tour.duration} Days
                      </div>
                      <div className="flex items-center">
                        <MapPin className="h-4 w-4 mr-2" />
                        Nepal Himalayas
                      </div>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Price per ticket</span>
                        <span>Rs {tour.price.toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span>Number of tickets</span>
                        <span>{numberOfTickets}</span>
                      </div>
                      <div className="border-t pt-2">
                        <div className="flex justify-between font-semibold text-lg">
                          <span>Total Amount</span>
                          <span className="text-primary">Rs {calculateTotal().toLocaleString()}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Contact Support */}
              <Card>
                <CardContent className="pt-6">
                  <div className="text-center">
                    <h4 className="font-semibold mb-2">Need Help?</h4>
                    <p className="text-sm text-muted-foreground mb-4">
                      Our travel experts are here to assist you
                    </p>
                    <div className="space-y-2 text-sm">
                      <p><strong>Phone:</strong> +977-1-4123456</p>
                      <p><strong>Email:</strong> info@mahalaxmi.com</p>
                      <p><strong>WhatsApp:</strong> +977-9841234567</p>
                    </div>
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

export default BookNow;