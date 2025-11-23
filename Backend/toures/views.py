from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Package
from .serializers import PackageSerializer


class PackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CRUD operations on Package model.
    Provides list, create, retrieve, update, partial_update, and destroy actions.
    """
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    
    @action(detail=True, methods=['get'])
    def tickets(self, request, pk=None):
        """Get all tickets for a specific package"""
        package = self.get_object()
        tickets = package.tickets.all()
        from system.serializers import TicketSerializer
        serializer = TicketSerializer(tickets, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a specific package"""
        package = self.get_object()
        payments = package.payments.all()
        from system.serializers import PaymentSerializer
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)
