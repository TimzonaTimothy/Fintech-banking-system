"""bank URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
# from two_factor.urls import urlpatterns as tf_urls
from .views import *
urlpatterns = [
    # path("", include(tf_urls)),
    path('admin/', admin.site.urls),
    path('', home, name="home"),
    path('about',about, name="about"),
    path('services',services, name="services"),
    path('faq',faq, name="faq"),
    path('terms',terms, name="terms"),
    path('contact',contact, name="contact"),
    path('sign_in',sign_in, name="sign_in"),
    path('sign_up',sign_up, name="sign_up"),
    path('logout',user_logout, name="logout"),
    path('activate/<uidb64>/<token>/', activate, name='activate'),
    path('otp', otp_view, name='otp'),
    path('forget_password',forgetpassword, name="forget_password"),
    path('resetpassword_validate/<uidb64>/<token>/', resetpassword_validate, name='resetpassword_validate'),
    path('resetpassword', resetpassword, name='resetpassword'),
    path('account/', include('account.urls')),
    path('', include('core.urls')),
]
if settings.DEBUG:
   urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
