from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import User
from throttling.models import FailedLoginAttempt, OTPRequest
from django.contrib.auth import authenticate
import random

# Set the block duration for too many failed attempts (1 hour)
BLOCK_DURATION = 60 * 60  # 1 ساعت بر حسب ثانیه

# Check if the user is blocked due to failed attempts or OTP requests
def is_blocked(model, ip, phone):
    record = model.objects.filter(ip_address=ip, phone_number=phone).first()
    if record and record.attempts >= 3:
        delta = timezone.now() - record.last_attempt
        if delta.total_seconds() < BLOCK_DURATION:
            return True
    return False

def increase_attempt(model, ip, phone):
    obj, created = model.objects.get_or_create(ip_address=ip, phone_number=phone)
    obj.attempts += 1
    obj.save()

def reset_attempts(model, ip, phone):
    model.objects.filter(ip_address=ip, phone_number=phone).delete()

# LoginView handles the login API request
class LoginView(APIView):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        phone = request.data.get('phone_number')
        password = request.data.get('password')

        if is_blocked(FailedLoginAttempt, ip, phone):
            return Response({"error": "Too many failed attempts. Try again later."}, status=429)

        user = authenticate(phone_number=phone, password=password)
        if user:
            reset_attempts(FailedLoginAttempt, ip, phone)
            return Response({"message": "Login successful."})
        else:
            increase_attempt(FailedLoginAttempt, ip, phone)
            return Response({"error": "Invalid credentials."}, status=401)

# RegisterOTPView handles the OTP request for user registration
class RegisterOTPView(APIView):
    def post(self, request):
        ip = request.META.get('REMOTE_ADDR')
        phone = request.data.get('phone_number')

        if is_blocked(OTPRequest, ip, phone):
            return Response({"error": "Too many requests. Try again later."}, status=429)

        code = random.randint(100000, 999999)
        request.session[f"otp_{phone}"] = str(code)
        increase_attempt(OTPRequest, ip, phone)
        return Response({"message": "OTP sent.", "otp": code})  # فقط برای تست، در واقعیت باید پیامک شود

# VerifyOTPView handles OTP verification during registration
class VerifyOTPView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        code = request.data.get('code')
        real_code = request.session.get(f"otp_{phone}")

        if code == real_code:
            reset_attempts(OTPRequest, request.META.get('REMOTE_ADDR'), phone)
            user, created = User.objects.get_or_create(phone_number=phone)
            return Response({"message": "OTP verified.", "user_exists": not created})
        else:
            increase_attempt(OTPRequest, request.META.get('REMOTE_ADDR'), phone)
            return Response({"error": "Invalid code."}, status=400)

# CompleteProfileView allows users to complete their profile after OTP verification
class CompleteProfileView(APIView):
    def post(self, request):
        phone = request.data.get('phone_number')
        name = request.data.get('full_name')
        email = request.data.get('email')
        password = request.data.get('password')

        user = User.objects.filter(phone_number=phone).first()
        if user:
            user.full_name = name
            user.email = email
            user.set_password(password)
            user.save()
            return Response({"message": "Profile completed."})
        return Response({"error": "User not found."}, status=404)
