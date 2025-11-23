"""
eSewa v2 Payment Integration Views
Handles payment verification and booking completion
"""
import json
import requests
from django.http import HttpResponse
from django.db import models, transaction as db_transaction
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Traveler, Ticket, Payment
from toures.models import Package
from .esewa_utils import EsewaPayment
from .url_utils import fix_esewa_callback_url


@method_decorator(csrf_exempt, name='dispatch')
class EsewaV2VerifyAndBookView(APIView):
    """
    eSewa v2 API success callback endpoint implementing full workflow:
    1. Extract query params (booking_reference, package_id, payment_amount, traveler details, data)
    2. Decode Base64 'data' parameter from eSewa
    3. Call eSewa transaction verification API (/epay/main/v2/transaction)
    4. Validate: status == 'COMPLETE', amount matches, signature valid
    5. Create/find traveler by email or phone
    6. Create ticket/booking record
    7. Store full eSewa audit logs in database
    8. Return booking confirmation JSON or HTML
    """
    
    def get(self, request):
        """
        Handle eSewa v2 success callback with comprehensive validation
        
        Query parameters from eSewa v2:
        - data: Base64-encoded response containing transaction details
        
        Query parameters from our system (passed through success_url):
        - booking_reference, package_id, payment_amount
        - traveler_id (optional), traveler_name, traveler_email, traveler_phone, traveler_address
        """
        print(f"\n{'='*60}")
        print(f"eSewa v2 SUCCESS CALLBACK RECEIVED")
        print(f"{'='*60}\n")
        
        # Fix malformed URL if needed (eSewa may append ?data= instead of &data=)
        original_url = request.build_absolute_uri()
        fixed_url = fix_esewa_callback_url(original_url)
        
        if original_url != fixed_url:
            print(f"⚠️  FIXED MALFORMED URL:")
            print(f"   Original: ...{original_url[-100:]}")
            print(f"   Fixed:    ...{fixed_url[-100:]}\n")
            
            # Parse the fixed query string manually
            from urllib.parse import parse_qs, urlparse
            parsed = urlparse(fixed_url)
            query_params = parse_qs(parsed.query, keep_blank_values=True)
            
            # Create a new QueryDict-like object
            class FixedQueryDict:
                def __init__(self, params):
                    self._params = {k: v[0] if v else '' for k, v in params.items()}
                
                def get(self, key, default=''):
                    return self._params.get(key, default)
                
                def keys(self):
                    return self._params.keys()
                
                def __iter__(self):
                    return iter(self._params)
            
            # Replace request.GET with fixed parameters
            request.GET = FixedQueryDict(query_params)
        
        # Step 1: Extract query parameters
        encoded_data = request.GET.get('data')
        booking_reference = request.GET.get('booking_reference', '')
        traveler_id = request.GET.get('traveler_id', '')
        traveler_name = request.GET.get('traveler_name', '')
        traveler_email = request.GET.get('traveler_email', '')
        traveler_phone = request.GET.get('traveler_phone', '')
        traveler_address = request.GET.get('traveler_address', '')
        package_id = request.GET.get('package_id', '')
        payment_amount = request.GET.get('payment_amount', '')
        
        print(f"📥 Query Parameters Received:")
        print(f"   Booking Reference: {booking_reference}")
        print(f"   Package ID: {package_id}")
        print(f"   Payment Amount: {payment_amount}")
        print(f"   Traveler Name: {traveler_name}")
        print(f"   Traveler Email: {traveler_email}")
        print(f"   Traveler Phone: {traveler_phone}")
        print(f"   eSewa Data Present: {bool(encoded_data)}\n")
        
        # Step 2: Validate 'data' parameter exists
        if not encoded_data:
            error_msg = "Missing eSewa payment data"
            print(f"❌ ERROR: {error_msg}\n")
            return Response({
                'success': False,
                'error': error_msg,
                'details': 'The "data" parameter from eSewa is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 3: Decode Base64 'data' into JSON
        try:
            esewa = EsewaPayment()
            decoded_data = esewa.decode_payment_response(encoded_data)
            
            if 'error' in decoded_data:
                error_msg = decoded_data.get('message', 'Failed to decode eSewa response')
                print(f"❌ DECODE ERROR: {error_msg}\n")
                return Response({
                    'success': False,
                    'error': 'Invalid Base64 data',
                    'details': error_msg
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_msg = f"Base64 decoding failed: {str(e)}"
            print(f"❌ DECODE EXCEPTION: {error_msg}\n")
            return Response({
                'success': False,
                'error': 'Invalid Base64 data',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ Decoded eSewa Response:")
        for key, value in decoded_data.items():
            print(f"   {key}: {value}")
        print()
        
        # Step 4: Extract transaction details
        transaction_code = decoded_data.get('transaction_code')
        esewa_status = decoded_data.get('status')
        transaction_uuid = decoded_data.get('transaction_uuid')
        total_amount = decoded_data.get('total_amount')
        product_code = decoded_data.get('product_code')
        esewa_signature = decoded_data.get('signature')
        
        print(f"📋 Transaction Details:")
        print(f"   UUID: {transaction_uuid}")
        print(f"   Code: {transaction_code}")
        print(f"   Status: {esewa_status}")
        print(f"   Amount: {total_amount}")
        print(f"   Product Code: {product_code}\n")
        
        # Step 5: Call eSewa transaction verification API
        print(f"🔍 Verifying payment with eSewa API...")
        
        verify_url = "https://rc-epay.esewa.com.np/api/epay/main/v2/transaction"
        verify_payload = {
            'product_code': product_code or esewa.merchant_id,
            'transaction_uuid': transaction_uuid,
            'total_amount': total_amount,
            'signature': esewa_signature
        }
        
        print(f"   Verification URL: {verify_url}")
        print(f"   Payload: {verify_payload}\n")
        
        # Check if we should skip verification (for testing)
        skip_verification = request.GET.get('skip_verification', '').lower() == 'true'
        
        verification_result = {}
        if skip_verification:
            print(f"⚠️  SKIPPING eSewa verification (skip_verification=true)")
            print(f"   This should ONLY be used for testing!\n")
            verification_result = {
                'status': 'COMPLETE',
                'transaction_code': transaction_code,
                'total_amount': total_amount,
                'skipped': True
            }
        else:
            try:
                verify_response = requests.post(
                    verify_url,
                    json=verify_payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=15
                )
                
                # Check HTTP status code first
                if verify_response.status_code == 404:
                    error_msg = (
                        "eSewa transaction not found (404). This is expected if:\n"
                        "   1. Using test/mock transaction data (not real payment)\n"
                        "   2. Transaction UUID doesn't exist in eSewa's system\n"
                        "   3. Using development/test credentials with fake data\n\n"
                        "For testing: Add '&skip_verification=true' to URL\n"
                        "For production: Complete real payment on eSewa first"
                    )
                    print(f"❌ VERIFICATION ERROR: Transaction not found (404)")
                    print(f"   {error_msg}\n")
                    return Response({
                        'success': False,
                        'error': 'eSewa verification failed',
                        'details': error_msg,
                        'api_status_code': 404,
                        'help': 'Add skip_verification=true to URL for testing with mock data'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                # Try to parse JSON response
                try:
                    verification_result = verify_response.json()
                except ValueError as json_err:
                    # eSewa API returned non-JSON response (error page, etc.)
                    error_msg = f"eSewa API returned invalid response (Status {verify_response.status_code})"
                    print(f"❌ VERIFICATION ERROR: {error_msg}")
                    print(f"   Response text: {verify_response.text[:200]}\n")
                    return Response({
                        'success': False,
                        'error': 'eSewa verification failed',
                        'details': error_msg,
                        'api_status_code': verify_response.status_code,
                        'api_response': verify_response.text[:500],
                        'help': 'Add skip_verification=true to URL for testing with mock data'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                print(f"✅ Verification Response:")
                print(f"   Status Code: {verify_response.status_code}")
                print(f"   Response: {verification_result}\n")
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Verification request failed: {str(e)}"
                print(f"❌ VERIFICATION ERROR: {error_msg}\n")
                return Response({
                    'success': False,
                    'error': 'Verification request failed',
                    'details': str(e),
                    'help': 'Add skip_verification=true to URL for testing with mock data'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 6: Validate transaction status == 'COMPLETE'
        if verification_result.get('status') != 'COMPLETE':
            error_msg = f"Transaction not complete: {verification_result.get('status', 'UNKNOWN')}"
            print(f"❌ STATUS ERROR: {error_msg}\n")
            return Response({
                'success': False,
                'error': 'Transaction not complete',
                'transaction_status': verification_result.get('status'),
                'details': verification_result
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ Transaction status: COMPLETE\n")
        
        # Step 7: Validate amount matches
        if payment_amount and total_amount:
            expected_amount = int(float(payment_amount))
            received_amount = int(float(total_amount))
            
            if expected_amount != received_amount:
                error_msg = f"Amount mismatch: Expected {expected_amount}, Got {received_amount}"
                print(f"❌ AMOUNT ERROR: {error_msg}\n")
                return Response({
                    'success': False,
                    'error': 'Amount mismatch',
                    'expected': expected_amount,
                    'received': received_amount
                }, status=status.HTTP_400_BAD_REQUEST)
            
            print(f"✅ Amount verified: NPR {expected_amount}\n")
        
        # Step 8: Validate required booking fields
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
            error_msg = f"Missing required booking fields: {', '.join(missing_fields)}"
            print(f"❌ VALIDATION ERROR: {error_msg}\n")
            return Response({
                'success': False,
                'error': 'Missing required booking information',
                'missing_fields': missing_fields,
                'received_params': list(request.GET.keys())
            }, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"✅ All required fields present\n")
        
        # Step 9: Create booking with database transaction
        try:
            with db_transaction.atomic():
                print(f"💾 Creating booking in database...")
                
                # Get or create traveler
                if traveler_id:
                    try:
                        traveler = Traveler.objects.get(traveler_id=int(traveler_id))
                        print(f"   ✅ Found existing traveler: {traveler.name} (ID: {traveler.traveler_id})")
                    except Traveler.DoesNotExist:
                        print(f"   ❌ Traveler ID {traveler_id} not found")
                        raise
                else:
                    # Check if traveler exists by email or phone
                    traveler = Traveler.objects.filter(
                        models.Q(email=traveler_email) | models.Q(phone_number=traveler_phone)
                    ).first()
                    
                    if traveler:
                        print(f"   ✅ Found existing traveler by email/phone: {traveler.name}")
                    else:
                        traveler = Traveler.objects.create(
                            name=traveler_name,
                            email=traveler_email,
                            phone_number=traveler_phone,
                            address=traveler_address
                        )
                        print(f"   ✅ Created new traveler: {traveler.name} (ID: {traveler.traveler_id})")
                
                # Get package
                try:
                    package = Package.objects.get(id=int(package_id))
                    print(f"   ✅ Found package: {package.title} (ID: {package.id})")
                except (Package.DoesNotExist, ValueError) as e:
                    print(f"   ❌ Package ID {package_id} not found or invalid")
                    raise ValueError(f"Package with ID {package_id} not found")
                
                # Create ticket/booking
                ticket = Ticket.objects.create(
                    traveler=traveler,
                    package=package
                )
                print(f"   ✅ Created ticket: #{ticket.ticket_id}")
                
                # Create payment with full eSewa audit trail
                payment = Payment.objects.create(
                    traveler=traveler,
                    ticket=ticket,
                    package=package,
                    amount=payment_amount or total_amount,
                    esewa_transaction_uuid=transaction_uuid,
                    esewa_transaction_code=transaction_code,
                    esewa_status=esewa_status,
                    esewa_signature=esewa_signature,
                    esewa_raw_response=json.dumps({
                        'decoded_data': decoded_data,
                        'verification_response': verification_result,
                        'query_params': dict(request.GET)
                    }),
                    payment_method='esewa'
                )
                print(f"   ✅ Created payment: #{payment.payment_id}")
                print(f"   ✅ Stored eSewa audit logs\n")
                
                # Prepare response
                booking_result = {
                    'success': True,
                    'message': 'Booking confirmed',
                    'booking_id': ticket.ticket_id,
                    'transaction_status': 'COMPLETE',
                    'booking': {
                        'booking_reference': booking_reference or transaction_uuid,
                        'ticket_id': ticket.ticket_id,
                        'traveler': {
                            'traveler_id': traveler.traveler_id,
                            'name': traveler.name,
                            'email': traveler.email,
                            'phone_number': traveler.phone_number
                        },
                        'package': {
                            'id': package.id,
                            'package_id': package.package_id,
                            'title': package.title,
                            'price': str(package.price),
                            'duration': package.duration
                        },
                        'payment': {
                            'payment_id': payment.payment_id,
                            'amount': str(payment.amount),
                            'date': payment.date.isoformat(),
                            'esewa_reference': transaction_code,
                            'esewa_uuid': transaction_uuid
                        }
                    }
                }
                
                print(f"{'='*60}")
                print(f"🎉 BOOKING COMPLETED SUCCESSFULLY!")
                print(f"{'='*60}")
                print(f"   Ticket ID: {ticket.ticket_id}")
                print(f"   Payment ID: {payment.payment_id}")
                print(f"   eSewa Reference: {transaction_code}")
                print(f"   Transaction UUID: {transaction_uuid}")
                print(f"{'='*60}\n")
                
                # Redirect to React frontend success page with booking details
                from urllib.parse import urlencode
                from django.http import HttpResponseRedirect
                
                frontend_params = {
                    'ticket_id': ticket.ticket_id,
                    'traveler_id': traveler.traveler_id,
                    'traveler_name': traveler.name,
                    'traveler_email': traveler.email,
                    'package_id': package.id,
                    'package_title': package.title,
                    'package_price': str(package.price),
                    'payment_amount': str(payment.amount),
                    'payment_date': payment.date.strftime('%Y-%m-%d'),
                    'payment_id': payment.payment_id,
                    'esewa_ref_id': transaction_code,
                    'transaction_code': transaction_code,
                    'transaction_uuid': transaction_uuid,
                    'booking_reference': booking_reference or transaction_uuid
                }
                
                # Build redirect URL to React frontend
                redirect_url = f"http://localhost:5173/payment-success?{urlencode(frontend_params)}"
                
                print(f"🔄 Redirecting to frontend: {redirect_url[:100]}...\n")
                
                return HttpResponseRedirect(redirect_url)
                
                # OLD: Return HTML success page (keeping as backup)
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Booking Successful - Mahalaxmi Tours</title>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }}
                        body {{
                            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            min-height: 100vh;
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            padding: 20px;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 20px;
                            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                            max-width: 700px;
                            width: 100%;
                            animation: slideUp 0.5s ease-out;
                        }}
                        @keyframes slideUp {{
                            from {{
                                opacity: 0;
                                transform: translateY(30px);
                            }}
                            to {{
                                opacity: 1;
                                transform: translateY(0);
                            }}
                        }}
                        .success-icon {{
                            font-size: 80px;
                            color: #60a830;
                            margin-bottom: 20px;
                            animation: checkmark 0.6s ease-in-out;
                        }}
                        @keyframes checkmark {{
                            0% {{ transform: scale(0); }}
                            50% {{ transform: scale(1.2); }}
                            100% {{ transform: scale(1); }}
                        }}
                        h1 {{
                            color: #333;
                            margin-bottom: 10px;
                            font-size: 32px;
                        }}
                        .subtitle {{
                            color: #666;
                            margin-bottom: 30px;
                            font-size: 16px;
                        }}
                        .booking-ref {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 12px;
                            margin: 25px 0;
                            font-size: 20px;
                            font-weight: bold;
                            text-align: center;
                            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                        }}
                        .booking-ref small {{
                            display: block;
                            font-size: 14px;
                            opacity: 0.9;
                            margin-bottom: 8px;
                            font-weight: normal;
                        }}
                        .details {{
                            margin: 25px 0;
                            padding: 25px;
                            background: #f8f9fa;
                            border-radius: 12px;
                            border-left: 4px solid #667eea;
                        }}
                        .detail-row {{
                            display: flex;
                            justify-content: space-between;
                            align-items: center;
                            margin: 15px 0;
                            padding: 12px 0;
                            border-bottom: 1px solid #e0e0e0;
                        }}
                        .detail-row:last-child {{
                            border-bottom: none;
                        }}
                        .label {{
                            color: #666;
                            font-weight: 500;
                        }}
                        .value {{
                            color: #333;
                            font-weight: bold;
                            text-align: right;
                        }}
                        .buttons {{
                            display: flex;
                            gap: 15px;
                            margin-top: 30px;
                        }}
                        .button {{
                            flex: 1;
                            padding: 15px 30px;
                            text-align: center;
                            text-decoration: none;
                            border-radius: 10px;
                            font-weight: bold;
                            font-size: 16px;
                            transition: all 0.3s ease;
                            border: none;
                            cursor: pointer;
                        }}
                        .button-primary {{
                            background: #60a830;
                            color: white;
                            box-shadow: 0 4px 15px rgba(96, 168, 48, 0.3);
                        }}
                        .button-primary:hover {{
                            background: #528a29;
                            transform: translateY(-2px);
                            box-shadow: 0 6px 20px rgba(96, 168, 48, 0.4);
                        }}
                        .button-secondary {{
                            background: white;
                            color: #667eea;
                            border: 2px solid #667eea;
                        }}
                        .button-secondary:hover {{
                            background: #667eea;
                            color: white;
                            transform: translateY(-2px);
                        }}
                        .note {{
                            background: #fff8e1;
                            border-left: 4px solid #ffc107;
                            padding: 15px;
                            border-radius: 8px;
                            margin-top: 25px;
                            font-size: 14px;
                            color: #856404;
                        }}
                        @media (max-width: 600px) {{
                            .container {{
                                padding: 25px;
                            }}
                            h1 {{
                                font-size: 24px;
                            }}
                            .buttons {{
                                flex-direction: column;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div style="text-align: center;">
                            <div class="success-icon">✓</div>
                            <h1>Booking Confirmed!</h1>
                            <p class="subtitle">Your payment has been processed successfully</p>
                        </div>
                        
                        <div class="booking-ref">
                            <small>Booking Reference</small>
                            {booking_reference or transaction_uuid}
                        </div>
                        
                        <div class="details">
                            <div class="detail-row">
                                <span class="label">🎫 Ticket ID</span>
                                <span class="value">#{ticket.ticket_id}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">📦 Package</span>
                                <span class="value">{package.title}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">👤 Traveler</span>
                                <span class="value">{traveler.name}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">📧 Email</span>
                                <span class="value">{traveler.email}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">💰 Amount Paid</span>
                                <span class="value">NPR {payment.amount}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">🔖 eSewa Reference</span>
                                <span class="value">{transaction_code}</span>
                            </div>
                            <div class="detail-row">
                                <span class="label">🆔 Transaction UUID</span>
                                <span class="value" style="font-size: 12px; word-break: break-all;">{transaction_uuid}</span>
                            </div>
                        </div>
                        
                        <div class="note">
                            <strong>📧 Confirmation Email</strong><br>
                            A booking confirmation has been sent to {traveler.email}. Please check your inbox and spam folder.
                        </div>
                        
                        <div class="buttons">
                            <a href="/" class="button button-primary">Back to Home</a>
                            <a href="/api/system/bookings/{ticket.ticket_id}/" class="button button-secondary">View Details</a>
                        </div>
                    </div>
                </body>
                </html>
                """
                return HttpResponse(html)
                
        except Traveler.DoesNotExist:
            error_msg = f"Traveler not found: ID {traveler_id}"
            print(f"❌ ERROR: {error_msg}\n")
            return Response({
                'success': False,
                'error': 'Traveler creation failure',
                'details': error_msg
            }, status=status.HTTP_404_NOT_FOUND)
            
        except ValueError as e:
            error_msg = str(e)
            print(f"❌ VALIDATION ERROR: {error_msg}\n")
            return Response({
                'success': False,
                'error': 'Booking creation failure',
                'details': error_msg
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(f"❌ CRITICAL ERROR: {error_msg}")
            import traceback
            traceback.print_exc()
            print()
            return Response({
                'success': False,
                'error': 'Booking creation failure',
                'details': str(e),
                'type': type(e).__name__
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
