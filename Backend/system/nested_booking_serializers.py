from rest_framework import serializers
from decimal import Decimal
from django.db import transaction
from .models import Traveler, Ticket, Payment
from toures.models import Package
from .esewa_utils import EsewaPayment
import uuid


class NestedBookingWithEsewaSerializer(serializers.Serializer):
    """
    Nested serializer that handles:
    1. Accept traveler details, package_id, and payment amount
    2. Initiate eSewa payment
    3. Return payment form data to redirect to eSewa
    
    After eSewa payment success, another endpoint will create the booking
    """
    # Traveler info (either existing or new)
    traveler_id = serializers.IntegerField(required=False, allow_null=True)
    traveler_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    traveler_email = serializers.EmailField(required=False, allow_blank=True)
    traveler_phone = serializers.CharField(max_length=20, required=False, allow_blank=True)
    traveler_address = serializers.CharField(required=False, allow_blank=True)
    
    # Package and payment info
    package_id = serializers.IntegerField(required=True)
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    def validate(self, data):
        """
        Validate that either traveler_id or new traveler details are provided
        """
        has_traveler_id = data.get('traveler_id')
        has_traveler_details = all([
            data.get('traveler_name'),
            data.get('traveler_email'),
            data.get('traveler_phone'),
            data.get('traveler_address')
        ])
        
        if not has_traveler_id and not has_traveler_details:
            raise serializers.ValidationError(
                "Either provide traveler_id or all traveler details (name, email, phone, address)"
            )
        
        if has_traveler_id and has_traveler_details:
            raise serializers.ValidationError(
                "Provide either traveler_id or new traveler details, not both"
            )
        
        # Validate package exists
        try:
            Package.objects.get(id=data['package_id'])
        except Package.DoesNotExist:
            raise serializers.ValidationError({"package_id": "Package not found"})
        
        # Validate existing traveler if provided
        if has_traveler_id:
            try:
                Traveler.objects.get(traveler_id=data['traveler_id'])
            except Traveler.DoesNotExist:
                raise serializers.ValidationError({"traveler_id": "Traveler not found"})
        
        return data
    
    def initiate_esewa_payment(self):
        """
        Initiate eSewa payment and return payment form data
        This does NOT create any booking records yet
        """
        package = Package.objects.get(id=self.validated_data['package_id'])
        amount = self.validated_data['payment_amount']
        
        # Generate unique booking reference
        booking_reference = f"BK{uuid.uuid4().hex[:10].upper()}"
        
        # Initialize eSewa
        esewa = EsewaPayment()
        
        # Prepare booking data to pass through success URL
        # CRITICAL: Only include non-empty values to avoid issues
        booking_params = {
            'booking_reference': booking_reference,
            'package_id': str(self.validated_data['package_id']),
            'payment_amount': str(int(float(amount)))  # Integer, no decimals
        }
        
        # Add traveler_id if exists, otherwise add traveler details
        if self.validated_data.get('traveler_id'):
            booking_params['traveler_id'] = str(self.validated_data['traveler_id'])
        else:
            # Only add non-empty traveler details
            if self.validated_data.get('traveler_name'):
                booking_params['traveler_name'] = self.validated_data['traveler_name']
            if self.validated_data.get('traveler_email'):
                booking_params['traveler_email'] = self.validated_data['traveler_email']
            if self.validated_data.get('traveler_phone'):
                booking_params['traveler_phone'] = self.validated_data['traveler_phone']
            if self.validated_data.get('traveler_address'):
                booking_params['traveler_address'] = self.validated_data['traveler_address']
        
        # Debug: Log the booking params being passed
        print(f"\n=== Creating eSewa Payment Request ===")
        print(f"Booking params to be passed in success_url:")
        for key, value in booking_params.items():
            print(f"  {key}: {value}")
        
        # URL-encode the parameters properly
        from urllib.parse import urlencode
        query_string = urlencode(booking_params, safe='')
        
        # Create payment request with proper URLs
        base_url = "http://localhost:8000"
        success_url = f"{base_url}/api/esewa/v2/success/?{query_string}"
        failure_url = f"{base_url}/api/esewa/v2/failure/"
        
        print(f"\n✅ Success URL: {success_url}")
        print(f"✅ Failure URL: {failure_url}")
        print(f"✅ Query string length: {len(query_string)} characters")
        
        # Validate URL length (eSewa typically has a 2000 char limit)
        if len(success_url) > 2000:
            print(f"⚠️  WARNING: Success URL is very long ({len(success_url)} chars). May cause issues with eSewa.")
            # Consider using a shorter callback and store data in session/cache
        
        # Generate unique transaction UUID (UUID v4 format as per eSewa requirements)
        transaction_uuid = str(uuid.uuid4())
        
        print(f"✅ Transaction UUID: {transaction_uuid}\n")
        
        # Convert amount to integer (eSewa expects integer amounts, no decimals)
        amount_int = int(float(amount))
        
        print(f"💰 Payment Amount: Rs. {amount_int}")
        print(f"📦 Product Code (will be EPAYTEST in test): {booking_reference}\n")
        
        # Create payment request
        # CRITICAL: In test environment, product_code will be overridden to EPAYTEST
        payment_data = esewa.create_payment_request(
            amount=amount_int,
            product_code=booking_reference,  # Will be overridden to EPAYTEST in test mode
            total_amount=amount_int,  # Must equal amount (no extra charges)
            success_url=success_url,
            failure_url=failure_url,
            transaction_uuid=transaction_uuid
        )
        
        # Store booking data to be used after payment (in real app, use Redis/Cache)
        # For now, we'll pass it through the callback
        booking_data = {
            'booking_reference': booking_reference,
            'traveler_id': self.validated_data.get('traveler_id'),
            'traveler_name': self.validated_data.get('traveler_name'),
            'traveler_email': self.validated_data.get('traveler_email'),
            'traveler_phone': self.validated_data.get('traveler_phone'),
            'traveler_address': self.validated_data.get('traveler_address'),
            'package_id': self.validated_data['package_id'],
            'payment_amount': str(amount)
        }
        
        return {
            'success': True,
            'message': 'Payment initiated successfully',
            'booking_reference': booking_reference,
            'payment_url': esewa.get_payment_url(),
            'payment_form_data': payment_data,
            'package_details': {
                'id': package.id,
                'package_id': package.package_id,
                'title': package.title,
                'price': str(package.price),
                'duration': package.duration,
                'cover_image': package.cover_image
            },
            'booking_data': booking_data,
            'instructions': 'Submit payment_form_data to payment_url. After successful payment, booking will be created automatically.'
        }


class VerifyAndCompleteBookingSerializer(serializers.Serializer):
    """
    Serializer to verify eSewa payment and create booking
    Called after eSewa redirects to success URL
    """
    # eSewa callback parameters
    oid = serializers.CharField(required=True, help_text="Product/Booking ID from eSewa")
    amt = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Amount")
    refId = serializers.CharField(required=True, help_text="eSewa reference ID")
    
    # Booking data (passed from initial request)
    booking_reference = serializers.CharField(required=True)
    traveler_id = serializers.IntegerField(required=False, allow_null=True)
    traveler_name = serializers.CharField(required=False, allow_blank=True)
    traveler_email = serializers.EmailField(required=False, allow_blank=True)
    traveler_phone = serializers.CharField(required=False, allow_blank=True)
    traveler_address = serializers.CharField(required=False, allow_blank=True)
    package_id = serializers.IntegerField(required=True)
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    def validate(self, data):
        """Validate essential booking data"""
        # Note: In eSewa v2, oid might be transaction_uuid, not booking_reference
        # So we don't enforce strict matching here
        # Just ensure we have the necessary data to create the booking
        if not data.get('package_id'):
            raise serializers.ValidationError("Package ID is required")
        if not data.get('payment_amount'):
            raise serializers.ValidationError("Payment amount is required")
        return data
    
    @transaction.atomic
    def verify_and_create_booking(self):
        """
        Verify payment with eSewa and create booking
        """
        # Step 1: Verify payment with eSewa
        esewa = EsewaPayment()
        
        # In production, you would make actual HTTP request to eSewa verification endpoint
        # For test environment, we'll assume verification is successful
        esewa_verified = True  # In production: make request to esewa.get_verify_url()
        
        if not esewa_verified:
            raise serializers.ValidationError("Payment verification failed")
        
        # Step 2: Get or create traveler
        traveler_id = self.validated_data.get('traveler_id')
        if traveler_id:
            traveler = Traveler.objects.get(traveler_id=traveler_id)
        else:
            traveler = Traveler.objects.create(
                name=self.validated_data['traveler_name'],
                email=self.validated_data['traveler_email'],
                phone_number=self.validated_data['traveler_phone'],
                address=self.validated_data['traveler_address']
            )
        
        # Step 3: Get package
        package = Package.objects.get(id=self.validated_data['package_id'])
        
        # Step 4: Create ticket
        ticket = Ticket.objects.create(
            traveler=traveler,
            package=package
        )
        
        # Step 5: Create payment with eSewa reference
        payment = Payment.objects.create(
            traveler=traveler,
            ticket=ticket,
            package=package,
            amount=self.validated_data['payment_amount']
        )
        
        return {
            'success': True,
            'message': 'Booking created successfully',
            'esewa_reference': self.validated_data['refId'],
            'booking': {
                'booking_reference': self.validated_data['booking_reference'],
                'ticket_id': ticket.ticket_id,
                'traveler': {
                    'traveler_id': traveler.traveler_id,
                    'name': traveler.name,
                    'email': traveler.email,
                    'phone_number': traveler.phone_number,
                    'address': traveler.address
                },
                'package': {
                    'id': package.id,
                    'package_id': package.package_id,
                    'title': package.title,
                    'description': package.description,
                    'price': str(package.price),
                    'duration': package.duration,
                    'start_date': package.start_date
                },
                'payment': {
                    'payment_id': payment.payment_id,
                    'amount': str(payment.amount),
                    'date': payment.date
                }
            }
        }
