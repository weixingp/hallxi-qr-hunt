"""hallxiqr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from qrhunt import views as main_view
from django.conf import settings

# Account and admin module
urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('allauth.urls')),
    path('account/check/', main_view.check_registered),
    path('account/profile/', main_view.user_details)
]

# Game Core URLs
core = [
    path('', main_view.home),
    path('scan', main_view.scan_qr),
    path('location/<str:uuid>/', main_view.location_main),
    path('location/access-denied', main_view.location_denied)
]

urlpatterns += core

# Development media root setting
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
