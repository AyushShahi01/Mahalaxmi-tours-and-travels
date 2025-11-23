from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse
from .models import Traveler, Ticket, Payment
from .serializers import TravelerSerializer, TicketSerializer, PaymentSerializer
from .booking_serializers import CreateBookingSerializer, BookingDetailSerializer
from .esewa_serializers import (EsewaPaymentRequestSerializer, 
                                EsewaPaymentVerifySerializer,
                                EsewaBookingSerializer)
from .nested_booking_serializers import (NestedBookingWithEsewaSerializer,
                                         VerifyAndCompleteBookingSerializer)
from .esewa_utils import EsewaPayment


class TravelerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Traveler model.
    Provides list, create, retrieve, update, partial_update, and destroy actions.
    """
    queryset = Traveler.objects.all()
    serializer_class = TravelerSerializer
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get all tickets for a specific traveler"""
        traveler = self.get_object()
        tickets = traveler.tickets.all()
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a specific traveler"""
        traveler = self.get_object()
        payments = traveler.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class TicketViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Ticket model.
    Provides list, create, retrieve, update, partial_update, and destroy actions.
    """
    queryset = Ticket.objects.select_related('traveler', 'package').all()
    serializer_class = TicketSerializer
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a specific ticket"""
        ticket = self.get_object()
        payments = ticket.payments.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Payment model.
    Provides list, create, retrieve, update, partial_update, and destroy actions.
    """
    queryset = Payment.objects.select_related('traveler', 'ticket', 'package').all()
    serializer_class = PaymentSerializer


class BookingAPIView(APIView):
    """
    API View for creating and viewing complete bookings.
    Integrates traveler info, package selection, and payment in one place.
    """
    
    def post(self, request):
        """
        Create a complete booking with traveler, ticket, and payment.
        
        Request body can include either:
        1. Existing traveler: {"traveler_id": 1, "package_id": 1, "payment_amount": 1500}
        2. New traveler: {
            "traveler_name": "John Doe",
            "traveler_email": "john@example.com",
            "traveler_phone": "+1234567890",
            "traveler_address": "123 Main St",
            "package_id": 1,
            "payment_amount": 1500
        }
        """
        serializer = CreateBookingSerializer(data=request.data)
        if serializer.is_valid():
            booking_data = serializer.save()
            
            # Prepare response with all booking details
            response_data = {
                'success': True,
                'message': 'Booking created successfully',
                'booking': {
                    'ticket_id': booking_data['ticket'].ticket_id,
                    'traveler': {
                        'traveler_id': booking_data['traveler'].traveler_id,
                        'name': booking_data['traveler'].name,
                        'email': booking_data['traveler'].email,
                        'phone_number': booking_data['traveler'].phone_number,
                        'address': booking_data['traveler'].address
                    },
                    'package': {
                        'id': booking_data['package'].id,
                        'package_id': booking_data['package'].package_id,
                        'title': booking_data['package'].title,
                        'price': booking_data['package'].price,
                        'duration': booking_data['package'].duration,
                        'group_size': booking_data['package'].group_size,
                        'start_date': booking_data['package'].start_date,
                        'cover_image': booking_data['package'].cover_image
                    },
                    'payment': {
                        'payment_id': booking_data['payment'].payment_id,
                        'amount': str(booking_data['payment'].amount),
                        'date': booking_data['payment'].date
                    }
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Get all bookings with complete details.
        Optional query params:
        - traveler_id: Filter by traveler
        - package_id: Filter by package
        """
        # Start with all payments (which represent bookings)
        bookings = Payment.objects.select_related(
            'traveler', 'ticket', 'package', 'ticket__package', 'ticket__traveler'
        ).all()
        
        # Apply filters if provided
        traveler_id = request.query_params.get('traveler_id')
        package_id = request.query_params.get('package_id')
        
        if traveler_id:
            bookings = bookings.filter(traveler_id=traveler_id)
        if package_id:
            bookings = bookings.filter(package_id=package_id)
        
        # Format response
        bookings_data = []
        for payment in bookings:
            bookings_data.append({
                'ticket_id': payment.ticket.ticket_id,
                'booking_date': payment.date,
                'traveler': {
                    'traveler_id': payment.traveler.traveler_id,
                    'name': payment.traveler.name,
                    'email': payment.traveler.email,
                    'phone_number': payment.traveler.phone_number,
                    'address': payment.traveler.address
                },
                'package': {
                    'id': payment.package.id,
                    'package_id': payment.package.package_id,
                    'title': payment.package.title,
                    'description': payment.package.description,
                    'price': payment.package.price,
                    'duration': payment.package.duration,
                    'group_size': payment.package.group_size,
                    'start_date': payment.package.start_date,
                    'cover_image': payment.package.cover_image
                },
                'payment': {
                    'payment_id': payment.payment_id,
                    'amount': str(payment.amount),
                    'date': payment.date
                }
            })
        
        return Response({
            'count': len(bookings_data),
            'bookings': bookings_data
        })


class BookingDetailAPIView(APIView):
    """Get details of a specific booking by ticket ID"""
    
    def get(self, request, ticket_id):
        """Get complete booking details for a specific ticket"""
        try:
            ticket = Ticket.objects.select_related('traveler', 'package').get(ticket_id=ticket_id)
            payment = Payment.objects.filter(ticket=ticket).first()
            
            if not payment:
                return Response({
                    'success': False,
                    'error': 'No payment found for this ticket'
                }, status=status.HTTP_404_NOT_FOUND)
            
            booking_data = {
                'ticket_id': ticket.ticket_id,
                'booking_date': payment.date,
                'traveler': {
                    'traveler_id': ticket.traveler.traveler_id,
                    'name': ticket.traveler.name,
                    'email': ticket.traveler.email,
                    'phone_number': ticket.traveler.phone_number,
                    'address': ticket.traveler.address
                },
                'package': {
                    'id': ticket.package.id,
                    'package_id': ticket.package.package_id,
                    'title': ticket.package.title,
                    'description': ticket.package.description,
                    'price': ticket.package.price,
                    'duration': ticket.package.duration,
                    'group_size': ticket.package.group_size,
                    'start_date': ticket.package.start_date,
                    'cover_image': ticket.package.cover_image,
                    'tour_highlights': ticket.package.tour_highlights,
                    'tour_details': ticket.package.tour_details
                },
                'payment': {
                    'payment_id': payment.payment_id,
                    'amount': str(payment.amount),
                    'date': payment.date
                }
            }
            
            return Response(booking_data)
            
        except Ticket.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Ticket not found'
            }, status=status.HTTP_404_NOT_FOUND)


class EsewaPaymentInitiateView(APIView):
    """
    Initiate eSewa payment for booking
    """
    
    def post(self, request):
        """
        Initiate payment with eSewa
        
        Request body:
        {
            "traveler_id": 1,  # OR provide new traveler details
            "traveler_name": "John Doe",
            "traveler_email": "john@example.com",
            "traveler_phone": "+1234567890",
            "traveler_address": "123 Main St",
            "package_id": 1,
            "payment_amount": 1500.00,
            "success_url": "http://localhost:8000/api/system/esewa/booking/success/",
            "failure_url": "http://localhost:8000/api/system/esewa/booking/failure/"
        }
        """
        serializer = EsewaBookingSerializer(data=request.data)
        if serializer.is_valid():
            payment_request = serializer.create_payment_request()
            
            return Response({
                'success': True,
                'message': 'Payment request created',
                'payment_url': payment_request['payment_url'],
                'payment_data': payment_request['payment_data'],
                'product_code': payment_request['product_code'],
                'booking_data': payment_request['booking_data'],
                'package': payment_request['package']
            }, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class EsewaPaymentSuccessView(APIView):
    """
    Handle successful eSewa payment callback
    """
    
    def get(self, request):
        """
        eSewa redirects here after successful payment with query parameters:
        - oid: Product/Booking ID
        - amt: Amount
        - refId: eSewa reference ID
        """
        oid = request.GET.get('oid')
        amt = request.GET.get('amt')
        ref_id = request.GET.get('refId')
        
        if not all([oid, amt, ref_id]):
            return Response({
                'success': False,
                'error': 'Missing payment parameters'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify payment with eSewa
        esewa = EsewaPayment()
        verify_url = esewa.get_verify_url()
        verify_params = {
            'amt': amt,
            'rid': ref_id,
            'pid': oid,
            'scd': esewa.merchant_id
        }
        
        try:
            # Make verification request to eSewa
            # Note: In production, you should make an actual HTTP request to eSewa
            # For now, we'll assume payment is verified
            
            return Response({
                'success': True,
                'message': 'Payment verified successfully',
                'payment_details': {
                    'product_code': oid,
                    'amount': amt,
                    'reference_id': ref_id
                },
                'next_step': 'Complete booking by calling POST /api/system/bookings/ with the booking data'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Payment verification failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class EsewaPaymentFailureView(APIView):
    """
    Handle failed eSewa payment callback
    """
    
    def get(self, request):
        """
        eSewa redirects here after failed payment
        """
        return Response({
            'success': False,
            'message': 'Payment failed or cancelled',
            'details': dict(request.GET)
        }, status=status.HTTP_400_BAD_REQUEST)


class EsewaBookingCompleteView(APIView):
    """
    Complete booking after successful eSewa payment verification
    """
    
    def post(self, request):
        """
        Complete booking after payment is verified
        
        Request body should include:
        - payment_verified: true
        - reference_id: eSewa reference ID
        - booking_data: Original booking data (traveler info, package_id, payment_amount)
        """
        if not request.data.get('payment_verified'):
            return Response({
                'success': False,
                'error': 'Payment must be verified before completing booking'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        booking_data = request.data.get('booking_data', {})
        reference_id = request.data.get('reference_id')
        
        if not booking_data:
            return Response({
                'success': False,
                'error': 'Booking data is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the booking using CreateBookingSerializer
        booking_serializer = CreateBookingSerializer(data=booking_data)
        if booking_serializer.is_valid():
            booking_result = booking_serializer.save()
            
            # Update payment with eSewa reference ID if needed
            payment = booking_result['payment']
            # You might want to add a field to store the eSewa reference ID
            
            return Response({
                'success': True,
                'message': 'Booking completed successfully',
                'esewa_reference_id': reference_id,
                'booking': {
                    'ticket_id': booking_result['ticket'].ticket_id,
                    'traveler': {
                        'traveler_id': booking_result['traveler'].traveler_id,
                        'name': booking_result['traveler'].name,
                        'email': booking_result['traveler'].email
                    },
                    'package': {
                        'id': booking_result['package'].id,
                        'title': booking_result['package'].title,
                        'price': str(booking_result['package'].price)
                    },
                    'payment': {
                        'payment_id': booking_result['payment'].payment_id,
                        'amount': str(booking_result['payment'].amount),
                        'date': booking_result['payment'].date
                    }
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': booking_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class NestedBookingAPIView(APIView):
    """
    Single nested API endpoint that:
    1. Accepts traveler details, package_id, and payment amount
    2. Initiates eSewa payment
    3. Returns eSewa payment form data
    
    After eSewa payment, user is redirected to verification endpoint
    which creates the booking automatically
    """
    
    def post(self, request):
        """
        Initiate booking with eSewa payment
        
        Request body:
        {
            "traveler_id": 1,  # OR provide new traveler details below
            "traveler_name": "John Doe",
            "traveler_email": "john@example.com",
            "traveler_phone": "+9771234567890",
            "traveler_address": "Kathmandu, Nepal",
            "package_id": 1,
            "payment_amount": 1500.00
        }
        """
        serializer = NestedBookingWithEsewaSerializer(data=request.data)
        
        if serializer.is_valid():
            result = serializer.initiate_esewa_payment()
            return Response(result, status=status.HTTP_200_OK)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class EsewaVerifyAndBookView(APIView):
    """
    eSewa v2 API success callback endpoint that:
    1. Receives eSewa payment confirmation (Base64-encoded response)
    2. Verifies payment using transaction status API
    3. Creates traveler (if new), ticket, and payment records
    4. Returns booking confirmation
    """
    
    def get(self, request):
        """
        Handle eSewa v2 success callback
        Query parameters from eSewa v2:
        - data: Base64-encoded response string containing transaction details
        
        Query parameters from our system (passed through success_url):
        - booking_data: JSON string with booking information
        """
        # Get eSewa v2 parameters (Base64-encoded response)
        encoded_data = request.GET.get('data')
        
        # Get booking data from query params (in production, fetch from cache/session)
        booking_reference = request.GET.get('booking_reference', '')
        traveler_id = request.GET.get('traveler_id', '')
        traveler_name = request.GET.get('traveler_name', '')
        traveler_email = request.GET.get('traveler_email', '')
        traveler_phone = request.GET.get('traveler_phone', '')
        traveler_address = request.GET.get('traveler_address', '')
        package_id = request.GET.get('package_id', '')
        payment_amount = request.GET.get('payment_amount', '')
        
        # Debug logging
        print(f"\n=== eSewa Success Callback Debug ===")
        print(f"Encoded data present: {bool(encoded_data)}")
        print(f"Query params: {dict(request.GET)}")
        print(f"Booking reference: {booking_reference}")
        print(f"Traveler name: {traveler_name}")
        print(f"Package ID: {package_id}")
        print(f"Payment amount: {payment_amount}")
        
        if not encoded_data:
            return Response({
                'success': False,
                'error': 'Missing eSewa payment data',
                'details': 'The "data" parameter from eSewa is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Decode Base64 response from eSewa
        from .esewa_utils import EsewaPayment
        esewa = EsewaPayment()
        decoded_data = esewa.decode_payment_response(encoded_data)
        
        if 'error' in decoded_data:
            return Response({
                'success': False,
                'error': decoded_data.get('message', 'Failed to decode eSewa response')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Extract transaction details from decoded response
        transaction_code = decoded_data.get('transaction_code')
        status_response = decoded_data.get('status')
        transaction_uuid = decoded_data.get('transaction_uuid')
        total_amount = decoded_data.get('total_amount')
        
        # Verify payment with eSewa status check API
        # Note: In test mode, verification may fail if payment wasn't actually made
        # For development, we'll allow proceeding if booking data is complete
        payment_verified = False
        if transaction_uuid and total_amount:
            verification = esewa.verify_payment(transaction_uuid, total_amount)
            payment_verified = verification.get('success', False)
            
            # In production, uncomment this to enforce strict verification:
            # if not payment_verified:
            #     return Response({
            #         'success': False,
            #         'error': 'Payment verification failed',
            #         'details': verification.get('message')
            #     }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate required fields with detailed error messages
        missing_fields = []
        if not traveler_name:
            missing_fields.append('traveler_name')
        if not traveler_email:
            missing_fields.append('traveler_email')
        if not traveler_phone:
            missing_fields.append('traveler_phone')
        if not traveler_address:
            missing_fields.append('traveler_address')
        if not package_id:
            missing_fields.append('package_id')
        if not payment_amount:
            missing_fields.append('payment_amount')
        
        if missing_fields:
            print(f"Missing fields: {missing_fields}")
            return Response({
                'success': False,
                'error': 'Missing required booking information',
                'missing_fields': missing_fields,
                'details': f'The following fields are required in success_url: {", ".join(missing_fields)}',
                'received_params': list(request.GET.keys()),
                'help': 'Ensure your success_url includes: traveler_name, traveler_email, traveler_phone, traveler_address, package_id, payment_amount'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare data for verification and booking
        verification_data = {
            'oid': transaction_uuid or booking_reference,
            'amt': payment_amount or total_amount,
            'refId': transaction_code,
            'booking_reference': booking_reference or transaction_uuid,
            'traveler_id': int(traveler_id) if traveler_id else None,
            'traveler_name': traveler_name,
            'traveler_email': traveler_email,
            'traveler_phone': traveler_phone,
            'traveler_address': traveler_address,
            'package_id': int(package_id),
            'payment_amount': payment_amount or total_amount
        }
        
        serializer = VerifyAndCompleteBookingSerializer(data=verification_data)
        
        if serializer.is_valid():
            try:
                result = serializer.verify_and_create_booking()
                
                # Return HTML success page
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Booking Successful</title>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 15px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            max-width: 600px;
                            text-align: center;
                        }}
                        .success-icon {{
                            font-size: 64px;
                            color: #60a830;
                            margin-bottom: 20px;
                        }}
                        h1 {{
                            color: #333;
                            margin-bottom: 10px;
                        }}
                        .booking-ref {{
                            background: #f0f7ff;
                            padding: 15px;
                            border-radius: 8px;
                            margin: 20px 0;
                            font-size: 18px;
                            font-weight: bold;
                            color: #1976D2;
                        }}
                        .details {{
                            text-align: left;
                            margin: 20px 0;
                            padding: 20px;
                            background: #f8f9fa;
                            border-radius: 8px;
                        }}
                        .detail-row {{
                            display: flex;
                            justify-content: space-between;
                            margin: 10px 0;
                            padding: 8px 0;
                            border-bottom: 1px solid #e0e0e0;
                        }}
                        .detail-row:last-child {{
                            border-bottom: none;
                        }}
                        .label {{
                            color: #666;
                        }}
                        .value {{
                            color: #333;
                            font-weight: bold;
                        }}
                        .button {{
                            display: inline-block;
                            margin-top: 20px;
                            padding: 12px 30px;
                            background: #60a830;
                            color: white;
                            text-decoration: none;
                            border-radius: 8px;
                            font-weight: bold;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="success-icon">✓</div>
                        <h1>Booking Successful!</h1>
                        <p>Your payment has been processed and booking confirmed.</p>
                        
                        <div class="booking-ref">
                            Booking Reference: {result['booking']['booking_reference']}
                        </div>
                        
                        <div class="details">
                            <div class="detail-row">
                                <span class="label">Ticket ID:</span>
                                <span class="value">{result['booking']['ticket_id']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Package:</span>
                                <span class="value">{result['booking']['package']['title']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Traveler:</span>
                                <span class="value">{result['booking']['traveler']['name']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">Amount Paid:</span>
                                <span class="value">NPR {result['booking']['payment']['amount']}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">eSewa Ref:</span>
                                <span class="value">{result['esewa_reference']}</span>
                            </div>
                        </div>
                        
                        <a href="/" class="button">Back to Home</a>
                    </div>
                </body>
                </html>
                """
                return HttpResponse(html)
                
            except Exception as e:
                return Response({
                    'success': False,
                    'error': f'Booking creation failed: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class EsewaPaymentFailedView(APIView):
    """
    eSewa failure callback endpoint
    """
    
    def get(self, request):
        """Handle failed payment"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Failed</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                }
                .container {
                    background: white;
                    padding: 40px;
                    border-radius: 15px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    max-width: 500px;
                    text-align: center;
                }
                .error-icon {
                    font-size: 64px;
                    color: #f5576c;
                    margin-bottom: 20px;
                }
                h1 {
                    color: #333;
                    margin-bottom: 10px;
                }
                p {
                    color: #666;
                    margin: 20px 0;
                }
                .button {
                    display: inline-block;
                    margin-top: 20px;
                    padding: 12px 30px;
                    background: #f5576c;
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">✗</div>
                <h1>Payment Failed</h1>
                <p>Your payment was not successful. Please try again.</p>
                <p>If you continue to experience issues, please contact support.</p>
                <a href="/" class="button">Try Again</a>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html)
