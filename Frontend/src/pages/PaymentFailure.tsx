import { useEffect } from "react";
import { useSearchParams, Link, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { XCircle, ArrowLeft, RefreshCw } from "lucide-react";

const PaymentFailure = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  // Get stored package info for retry
  const packageInfo = sessionStorage.getItem('package_info');
  const packageData = packageInfo ? JSON.parse(packageInfo) : null;

  useEffect(() => {
    // Log the failure parameters from eSewa
    const params = Object.fromEntries(searchParams.entries());
    console.log("Payment failed with params:", params);
  }, [searchParams]);

  const handleRetry = () => {
    if (packageData?.id) {
      // Redirect back to booking page with the same package
      navigate(`/book-now?id=${packageData.id}`);
    } else {
      navigate('/');
    }
  };

  return (
    <div className="min-h-screen">
      <Navbar />
      
      <section className="py-20 bg-background">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8">
          <Card>
            <CardHeader className="text-center">
              <div className="mx-auto flex items-center justify-center h-20 w-20 rounded-full bg-red-100 mb-4">
                <XCircle className="h-12 w-12 text-red-600" />
              </div>
              <CardTitle className="text-3xl">Payment Failed</CardTitle>
              <p className="text-muted-foreground mt-2">
                Your payment could not be processed
              </p>
            </CardHeader>
            
            <CardContent className="space-y-6">
              {/* Failure Information */}
              <div className="bg-muted/30 p-6 rounded-lg space-y-4">
                <h3 className="text-lg font-semibold">What happened?</h3>
                <p className="text-sm text-muted-foreground">
                  Your payment through eSewa was either cancelled or could not be completed. 
                  This could be due to:
                </p>
                <ul className="text-sm text-muted-foreground space-y-2 ml-4">
                  <li>• Payment was cancelled by you</li>
                  <li>• Insufficient balance in your eSewa account</li>
                  <li>• Technical issue with the payment gateway</li>
                  <li>• Session timeout</li>
                </ul>
              </div>

              {/* Package Info (if available) */}
              {packageData && (
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg">
                  <h4 className="font-semibold mb-2">Your Selected Package</h4>
                  <div className="space-y-2 text-sm">
                    <p className="font-medium">{packageData.title}</p>
                    <p className="text-muted-foreground">
                      Price: Rs {parseFloat(packageData.price).toLocaleString()}
                    </p>
                  </div>
                </div>
              )}

              {/* Next Steps */}
              <div className="bg-amber-50 dark:bg-amber-950 p-4 rounded-lg">
                <h4 className="font-semibold mb-2">What can you do?</h4>
                <ul className="text-sm space-y-2 text-muted-foreground">
                  <li>• Try the payment again with sufficient balance</li>
                  <li>• Contact our support team for alternative payment methods</li>
                  <li>• Verify your eSewa account is active and working</li>
                  <li>• Use a different payment method if available</li>
                </ul>
              </div>

              {/* Action Buttons */}
              <div className="space-y-3 pt-4">
                {packageData && (
                  <Button 
                    className="w-full" 
                    onClick={handleRetry}
                  >
                    <RefreshCw className="h-5 w-5 mr-2" />
                    Try Payment Again
                  </Button>
                )}
                
                <div className="flex gap-4">
                  <Link to="/" className="flex-1">
                    <Button variant="outline" className="w-full">
                      <ArrowLeft className="h-5 w-5 mr-2" />
                      Back to Home
                    </Button>
                  </Link>
                  <Link to="/contact" className="flex-1">
                    <Button variant="outline" className="w-full">
                      Contact Support
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Support Information */}
              <div className="text-center text-sm text-muted-foreground border-t pt-4">
                <p className="font-semibold mb-2">Need Assistance?</p>
                <div className="space-y-1">
                  <p><strong>Phone:</strong> +977-1-4123456</p>
                  <p><strong>Email:</strong> info@mahalaxmi.com</p>
                  <p><strong>WhatsApp:</strong> +977-9841234567</p>
                </div>
                <p className="mt-3 text-xs">
                  Our support team is available 24/7 to help you complete your booking
                </p>
              </div>

              {/* No Charges Note */}
              <div className="bg-green-50 dark:bg-green-950 p-3 rounded-lg text-center">
                <p className="text-sm text-green-800 dark:text-green-200">
                  ✓ No charges were made to your account
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default PaymentFailure;
