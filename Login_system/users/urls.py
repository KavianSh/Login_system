from django.urls import path
from .views import LoginView, RegisterOTPView, VerifyOTPView, CompleteProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterOTPView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('complete-profile/', CompleteProfileView.as_view(), name='complete_profile'),
]