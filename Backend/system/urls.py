from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (TravelerViewSet, TicketViewSet, PaymentViewSet, 
                   BookingAPIView, BookingDetailAPIView,
                   EsewaPaymentInitiateView, EsewaPaymentSuccessView,
                   EsewaPaymentFailureView, EsewaBookingCompleteView,
                   NestedBookingAPIView, EsewaVerifyAndBookView,
                   EsewaPaymentFailedView)
from .esewa_v2_views import EsewaV2VerifyAndBookView

router = DefaultRouter()
router.register(r'travelers', TravelerViewSet, basename='traveler')
router.register(r'tickets', TicketViewSet, basename='ticket')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('', include(router.urls)),
    path('bookings/', BookingAPIView.as_view(), name='booking-create-list'),
    path('bookings/<int:ticket_id>/', BookingDetailAPIView.as_view(), name='booking-detail'),
    
    # Nested API - Single endpoint for complete booking flow with eSewa
    path('book-with-esewa/', NestedBookingAPIView.as_view(), name='nested-booking-esewa'),
    
    # eSewa payment endpoints (legacy/separate flow)
    path('esewa/initiate/', EsewaPaymentInitiateView.as_view(), name='esewa-initiate'),
    path('esewa/booking/success/', EsewaPaymentSuccessView.as_view(), name='esewa-success'),
    path('esewa/booking/failure/', EsewaPaymentFailureView.as_view(), name='esewa-failure'),
    path('esewa/booking/complete/', EsewaBookingCompleteView.as_view(), name='esewa-complete-booking'),
    
    # eSewa v2 verification and booking completion (NEW - Full implementation)
    path('esewa/v2/verify-and-book/', EsewaV2VerifyAndBookView.as_view(), name='esewa-v2-verify-and-book'),
    path('esewa/v2/success/', EsewaV2VerifyAndBookView.as_view(), name='esewa-v2-success'),  # Success callback
    path('esewa/v2/failure/', EsewaPaymentFailedView.as_view(), name='esawa-v2-failure'),  # Failure callback
    
    # eSewa verification and booking completion (for nested API - legacy)
    path('esewa/verify-and-book/', EsewaV2VerifyAndBookView.as_view(), name='esewa-verify-and-book'),
    path('esewa/verify/', EsewaV2VerifyAndBookView.as_view(), name='esewa-verify'),  # Alias for easier access
    path('esewa/payment-failed/', EsewaPaymentFailedView.as_view(), name='esewa-payment-failed'),
    path('esewa/failed/', EsewaPaymentFailedView.as_view(), name='esewa-failed'),  # Alias for easier access
]
