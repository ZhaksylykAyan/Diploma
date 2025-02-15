from django.urls import path
from .views import RegisterView, verify_otp_view, ResendOTPView, LoginView, home_view, LogoutView
urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('home/', home_view, name='home'),
    path('verify_otp/', verify_otp_view.as_view(), name='otp_verification'),
    path('resend_otp/', ResendOTPView.as_view(), name='resend_otp'),
]