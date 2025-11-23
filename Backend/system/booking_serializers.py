from rest_framework import serializers
from .models import Traveler, Ticket, Payment
from toures.models import Package
from django.db import transaction


class BookingTravelerSerializer(serializers.ModelSerializer):
    """Serializer for traveler information in booking"""
    class Meta:
        model = Traveler
        fields = ['traveler_id', 'name', 'email', 'phone_number', 'address']
        read_only_fields = ['traveler_id']


class BookingPackageSerializer(serializers.ModelSerializer):
    """Serializer for package information in booking"""
    class Meta:
        model = Package
        fields = ['id', 'package_id', 'title', 'description', 'price', 'duration', 'group_size', 'start_date', 'cover_image']
        read_only_fields = ['id', 'package_id', 'title', 'description', 'price', 'duration', 'group_size', 'start_date', 'cover_image']


class BookingPaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment information in booking"""
    class Meta:
        model = Payment
        fields = ['payment_id', 'amount', 'date']
        read_only_fields = ['payment_id', 'date']


class CreateBookingSerializer(serializers.Serializer):
    """
    Serializer for creating a complete booking with traveler, package, and payment info.
    This creates all related records in a single transaction.
    """
    # Traveler information (can be existing or new)
    traveler_id = serializers.IntegerField(required=False, allow_null=True, help_text="Existing traveler ID (optional)")
    traveler_name = serializers.CharField(max_length=100, required=False, help_text="Name for new traveler")
    traveler_email = serializers.EmailField(required=False, help_text="Email for new traveler")
    traveler_phone = serializers.CharField(max_length=20, required=False, help_text="Phone for new traveler")
    traveler_address = serializers.CharField(required=False, help_text="Address for new traveler")
    
    # Package selection
    package_id = serializers.IntegerField(required=True, help_text="ID of the package to book")
    
    # Payment information
    payment_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True, help_text="Payment amount")
    
    def validate(self, data):
        """Validate that we have either traveler_id or new traveler info"""
        traveler_id = data.get('traveler_id')
        
        if not traveler_id:
            # If no traveler_id, we need all traveler fields
            required_fields = ['traveler_name', 'traveler_email', 'traveler_phone', 'traveler_address']
            missing = [f for f in required_fields if not data.get(f)]
            if missing:
                raise serializers.ValidationError(
                    f"If traveler_id is not provided, you must provide: {', '.join(missing)}"
                )
        else:
            # Verify traveler exists
            if not Traveler.objects.filter(traveler_id=traveler_id).exists():
                raise serializers.ValidationError({"traveler_id": "Traveler not found"})
        
        # Verify package exists
        try:
            Package.objects.get(id=data['package_id'])
        except Package.DoesNotExist:
            raise serializers.ValidationError({"package_id": "Package not found"})
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Create traveler (if needed), ticket, and payment in one transaction"""
        # Get or create traveler
        traveler_id = validated_data.get('traveler_id')
        if traveler_id:
            traveler = Traveler.objects.get(traveler_id=traveler_id)
        else:
            traveler = Traveler.objects.create(
                name=validated_data['traveler_name'],
                email=validated_data['traveler_email'],
                phone_number=validated_data['traveler_phone'],
                address=validated_data['traveler_address']
            )
        
        # Get package
        package = Package.objects.get(id=validated_data['package_id'])
        
        # Create ticket
        ticket = Ticket.objects.create(
            traveler=traveler,
            package=package
        )
        
        # Create payment
        payment = Payment.objects.create(
            amount=validated_data['payment_amount'],
            traveler=traveler,
            ticket=ticket,
            package=package
        )
        
        return {
            'traveler': traveler,
            'ticket': ticket,
            'payment': payment,
            'package': package
        }


class BookingDetailSerializer(serializers.Serializer):
    """Serializer for displaying complete booking details"""
    ticket_id = serializers.IntegerField(source='ticket.ticket_id')
    booking_date = serializers.DateTimeField(source='payment.date')
    traveler = BookingTravelerSerializer(source='ticket.traveler')
    package = BookingPackageSerializer(source='ticket.package')
    payment = BookingPaymentSerializer(source='payment')
    
    class Meta:
        fields = ['ticket_id', 'booking_date', 'traveler', 'package', 'payment']
