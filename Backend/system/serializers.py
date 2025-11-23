from rest_framework import serializers
from .models import Traveler, Ticket, Payment


class TravelerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traveler
        fields = '__all__'


class TicketSerializer(serializers.ModelSerializer):
    traveler_name = serializers.CharField(source='traveler.name', read_only=True)
    package_title = serializers.CharField(source='package.title', read_only=True)
    
    class Meta:
        model = Ticket
        fields = '__all__'


class PaymentSerializer(serializers.ModelSerializer):
    traveler_name = serializers.CharField(source='traveler.name', read_only=True)
    package_title = serializers.CharField(source='package.title', read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
