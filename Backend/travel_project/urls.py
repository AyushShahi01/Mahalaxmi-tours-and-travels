"""
URL configuration for travel_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from system.esewa_v2_views import EsewaV2VerifyAndBookView
from system.views import EsewaPaymentFailedView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/system/', include('system.urls')),
    path('api/toures/', include('toures.urls')),
    # eSewa v2 callbacks at root level (for direct eSewa integration)
    path('api/esewa/v2/success/', EsewaV2VerifyAndBookView.as_view(), name='esewa-v2-callback-success'),
    path('api/esewa/v2/failure/', EsewaPaymentFailedView.as_view(), name='esewa-v2-callback-failure'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
