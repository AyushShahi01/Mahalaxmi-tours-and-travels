import { useEffect, useState } from "react";
import { useSearchParams, useNavigate, Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { CheckCircle, Loader2, ArrowRight, Download } from "lucide-react";

const PaymentSuccess = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [bookingDetails, setBookingDetails] = useState<any>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const processPayment = async () => {
      try {
        // eSewa v2 redirects with query parameters after backend verification
        // The backend already decoded Base64, verified signature, and created booking
        
        // Get booking details from URL parameters (sent by backend)
        const ticketId = searchParams.get('ticket_id');
        const travelerId = searchParams.get('traveler_id');
        const travelerName = searchParams.get('traveler_name');
        const travelerEmail = searchParams.get('traveler_email');
        const packageId = searchParams.get('package_id');
        const packageTitle = searchParams.get('package_title');
        const packagePrice = searchParams.get('package_price');
        const paymentAmount = searchParams.get('payment_amount');
        const paymentDate = searchParams.get('payment_date');
        const esewaRefId = searchParams.get('esewa_ref_id');
        const transactionCode = searchParams.get('transaction_code');

        // Check if we have the minimum required data
        if (!ticketId || !travelerName) {
          // Try to get from sessionStorage as fallback
          const storedTraveler = sessionStorage.getItem('traveler_info');
          const storedPackage = sessionStorage.getItem('package_info');

          if (!storedTraveler || !storedPackage) {
            setError("Booking details not found. If you completed the payment, please contact support.");
            setLoading(false);
            return;
          }

          // Use stored data
          const travelerInfo = JSON.parse(storedTraveler);
          const packageInfo = JSON.parse(storedPackage);

          setBookingDetails({
            ticket_id: ticketId || 'PENDING',
            esewa_reference_id: esewaRefId || 'N/A',
            transaction_code: transactionCode || 'N/A',
            traveler: {
              name: travelerName || travelerInfo.name,
              email: travelerEmail || travelerInfo.email,
              traveler_id: travelerId || 'N/A'
            },
            package: {
              id: packageId || packageInfo.id,
              title: packageTitle || packageInfo.title,
              price: packagePrice || packageInfo.price
            },
            payment: {
              amount: paymentAmount || packageInfo.amount,
              date: paymentDate || new Date().toISOString().split('T')[0]
            }
          });
        } else {
          // Build booking details from URL parameters
          setBookingDetails({
            ticket_id: ticketId,
            esewa_reference_id: esewaRefId || 'N/A',
            transaction_code: transactionCode || 'N/A',
            traveler: {
              name: travelerName,
              email: travelerEmail || 'N/A',
              traveler_id: travelerId || 'N/A'
            },
            package: {
              id: packageId,
              title: packageTitle || 'N/A',
              price: packagePrice || '0'
            },
            payment: {
              amount: paymentAmount || '0',
              date: paymentDate || new Date().toISOString().split('T')[0]
            }
          });
        }

        // Clear session storage
        sessionStorage.removeItem('booking_reference');
        sessionStorage.removeItem('traveler_info');
        sessionStorage.removeItem('package_info');

      } catch (err: any) {
        console.error("Error processing payment:", err);
        setError("Failed to load booking details. Please contact support.");
      } finally {
        setLoading(false);
      }
    };

    processPayment();
  }, [searchParams]);

  if (loading) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="flex flex-col justify-center items-center py-40">
          <Loader2 className="h-16 w-16 animate-spin text-primary mb-4" />
          <p className="text-lg text-muted-foreground">Processing your payment...</p>
          <p className="text-sm text-muted-foreground mt-2">Please wait, do not refresh the page</p>
        </div>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen">
        <Navbar />
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <Card>
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                  <span className="text-3xl">❌</span>
                </div>
                <h2 className="text-2xl font-bold mb-2">Payment Processing Error</h2>
                <p className="text-muted-foreground mb-6">{error}</p>
                <div className="flex gap-4 justify-center">
                  <Link to="/">
                    <Button variant="outline">Back to Home</Button>
                  </Link>
                  <Link to="/contact">
                    <Button>Contact Support</Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen">
      <Navbar />
      
      <section className="py-20 bg-background">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-green-100 mb-4">
                <CheckCircle className="h-12 w-12 text-green-600" />
              </div>
              <CardTitle className="text-3xl">Payment Successful!</CardTitle>
              <p className="text-muted-foreground mt-2">
                Your booking has been confirmed
              </p>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Booking Details */}
              <div className="bg-muted/30 p-6 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold border-b pb-2">Booking Details</h3>
                
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Ticket ID</p>
                    <p className="font-semibold">{bookingDetails?.ticket_id}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Transaction Code</p>
                    <p className="font-semibold">{bookingDetails?.transaction_code}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">eSewa Reference</p>
                    <p className="font-semibold">{bookingDetails?.esewa_reference_id}</p>
                  </div>
                </div>

                {/* Traveler Info */}
                {bookingDetails?.traveler && (
                  <div className="border-t pt-4">
                    <h4 className="font-semibold mb-3">Traveler Information</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Name:</span>
                        <span className="font-medium">{bookingDetails.traveler.name}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Email:</span>
                        <span className="font-medium">{bookingDetails.traveler.email}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Traveler ID:</span>
                        <span className="font-medium">{bookingDetails.traveler.traveler_id}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Package Info */}
                {bookingDetails?.package && (
                  <div className="border-t pt-4">
                    <h4 className="font-semibold mb-3">Package Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Package:</span>
                        <span className="font-medium">{bookingDetails.package.title}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Package Price:</span>
                        <span className="font-medium">Rs {parseFloat(bookingDetails.package.price).toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                )}

                {/* Payment Info */}
                {bookingDetails?.payment && (
                  <div className="border-t pt-4">
                    <h4 className="font-semibold mb-3">Payment Details</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Amount Paid:</span>
                        <span className="font-semibold text-green-600">Rs {parseFloat(bookingDetails.payment.amount).toLocaleString()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Payment Date:</span>
                        <span className="font-medium">{bookingDetails.payment.date}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Payment ID:</span>
                        <span className="font-medium">{bookingDetails.payment.payment_id}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Next Steps */}
              <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                <h4 className="font-semibold mb-2 flex items-center">
                  <ArrowRight className="h-5 w-5 mr-2" />
                  What's Next?
                </h4>
                <ul className="text-sm space-y-2 text-muted-foreground">
                  <li>• A confirmation email has been sent to your registered email</li>
                  <li>• Our team will contact you within 24 hours with further details</li>
                  <li>• Please keep your Ticket ID handy for future reference</li>
                  <li>• Check your email for complete itinerary and preparation guidelines</li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 pt-4">
                <Link to="/" className="flex-1">
                  <Button variant="outline" className="w-full">
                    Back to Home
                  </Button>
                </Link>
                <Link to="/" className="flex-1">
                  <Button className="w-full">
                    Browse More Tours
                  </Button>
                </Link>
              </div>

              {/* Support */}
              <div className="text-center text-sm text-muted-foreground border-t pt-4">
                <p>Need help? Contact us at:</p>
                <p className="font-medium mt-1">+977-1-4123456 | info@mahalaxmi.com</p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default PaymentSuccess;
