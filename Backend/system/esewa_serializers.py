from rest_framework import serializers
from decimal import Decimal
from .esewa_utils import EsewaPayment


class EsewaPaymentRequestSerializer(serializers.Serializer):
    """
    Serializer for initiating eSewa payment
    """
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    product_code = serializers.CharField(max_length=100, required=True, 
                                         help_text="Unique booking/product identifier")
    success_url = serializers.URLField(required=False, 
                                       help_text="URL to redirect after successful payment")
    failure_url = serializers.URLField(required=False, 
                                       help_text="URL to redirect after failed payment")
    
    def validate_amount(self, value):
        """Validate amount is positive"""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")
        return value
    
    def create_payment(self):
        """
        Create eSewa payment request
        """
        esewa = EsewaPayment()
        
        amount = self.validated_data['amount']
        product_code = self.validated_data['product_code']
        success_url = self.validated_data.get('success_url', 'http://localhost:8000/api/system/esewa/success/')
        failure_url = self.validated_data.get('failure_url', 'http://localhost:8000/api/system/esewa/failure/')
        
        payment_data = esewa.create_payment_request(
            amount=amount,
            product_code=product_code,
            total_amount=amount,
            success_url=success_url,
            failure_url=failure_url
        )
        
        return {
            'payment_url': esewa.get_payment_url(),
            'payment_data': payment_data,
            'merchant_id': esewa.merchant_id
        }


class EsewaPaymentVerifySerializer(serializers.Serializer):
    """
    Serializer for verifying eSewa payment
    """
    oid = serializers.CharField(max_length=100, required=True, 
                                 help_text="Product/Booking ID")
    amt = serializers.DecimalField(max_digits=10, decimal_places=2, required=True,
                                    help_text="Transaction amount")
    refId = serializers.CharField(max_length=100, required=True,
                                   help_text="eSewa reference ID")
    
    def verify_payment(self):
        """
        Verify payment with eSewa
        """
        esewa = EsewaPayment()
        
        verify_data = esewa.verify_payment(
            amount=self.validated_data['amt'],
            ref_id=self.validated_data['refId'],
            product_id=self.validated_data['oid']
        )
        
        return {
            'verify_url': esewa.get_verify_url(),
            'verify_data': verify_data,
            'status': 'pending_verification'
        }


class EsewaBookingSerializer(serializers.Serializer):
    """
    Combined serializer for eSewa payment + booking creation
    """
    # Traveler info (either existing or new)
    traveler_id = serializers.IntegerField(required=False)
    traveler_name = serializers.CharField(max_length=100, required=False)
    traveler_email = serializers.EmailField(required=False)
    traveler_phone = serializers.CharField(max_length=20, required=False)
    traveler_address = serializers.CharField(required=False)
    
    # Package info
    package_id = serializers.IntegerField(required=True)
    
    # Payment info
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    
    # eSewa callback URLs
    success_url = serializers.URLField(required=False)
    failure_url = serializers.URLField(required=False)
    
    def validate(self, data):
        """
        Validate that either traveler_id or new traveler details are provided
        """
        has_traveler_id = 'traveler_id' in data
        has_traveler_details = all(k in data for k in ['traveler_name', 'traveler_email', 
                                                         'traveler_phone', 'traveler_address'])
        
        if not has_traveler_id and not has_traveler_details:
            raise serializers.ValidationError(
                "Either provide traveler_id or all traveler details (name, email, phone, address)"
            )
        
        if has_traveler_id and has_traveler_details:
            raise serializers.ValidationError(
                "Provide either traveler_id or new traveler details, not both"
            )
        
        return data
    
    def create_payment_request(self):
        """
        Create eSewa payment request for booking
        Generate a unique product code for this booking attempt
        """
        import uuid
        from toures.models import Package
        
        # Validate package exists
        try:
            package = Package.objects.get(id=self.validated_data['package_id'])
        except Package.DoesNotExist:
            raise serializers.ValidationError({"package_id": "Package not found"})
        
        # Generate unique product code for this booking
        product_code = f"BOOKING_{uuid.uuid4().hex[:12].upper()}"
        
        esewa = EsewaPayment()
        amount = self.validated_data['payment_amount']
        success_url = self.validated_data.get('success_url', 
                                               'http://localhost:8000/api/system/esewa/booking/success/')
        failure_url = self.validated_data.get('failure_url',
                                               'http://localhost:8000/api/system/esewa/booking/failure/')
        
        payment_data = esewa.create_payment_request(
            amount=amount,
            product_code=product_code,
            total_amount=amount,
            success_url=success_url,
            failure_url=failure_url
        )
        
        # Store booking data temporarily (you might want to save this in cache or session)
        return {
            'payment_url': esewa.get_payment_url(),
            'payment_data': payment_data,
            'product_code': product_code,
            'booking_data': {
                'traveler_id': self.validated_data.get('traveler_id'),
                'traveler_name': self.validated_data.get('traveler_name'),
                'traveler_email': self.validated_data.get('traveler_email'),
                'traveler_phone': self.validated_data.get('traveler_phone'),
                'traveler_address': self.validated_data.get('traveler_address'),
                'package_id': self.validated_data['package_id'],
                'payment_amount': str(amount),
            },
            'package': {
                'id': package.id,
                'title': package.title,
                'price': str(package.price)
            }
        }
