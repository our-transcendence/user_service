"""
URL configuration for auth project.

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
from django.urls import path
from login import endpoint

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', endpoint.login_endpoint),
    path('register/', endpoint.register_endpoint),
    path('refresh/', endpoint.refresh_auth_token),
    path('test/', endpoint.test_decorator),
    path('public_key/', endpoint.pubkey_retrieval),
    path('enable_totp/', endpoint.set_totp),
    path('otp/', endpoint.otp_submit),
    path('login_42/', endpoint.login_42_page),
    path('token_42/', endpoint.token_42)
]
