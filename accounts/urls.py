from django.urls import path
from accounts.views import login_view, verify_otp_view, logout_view, dashboard_redirect

urlpatterns = [
    path('', dashboard_redirect, name='dashboard'),
    path('login/', login_view, name='login'),
    path('verify-otp/', verify_otp_view, name='verify_otp'),
    path('logout/', logout_view, name='logout'),
]
