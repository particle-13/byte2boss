from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.conf import settings
from .models import User, OTP
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from google.oauth2 import id_token
from google.auth.transport import requests






#google login view
class GoogleLoginView(APIView):
    def post(self, request):
        # The frontend sends 'id_token' (rename your frontend field if needed)
        token = request.data.get("id_token")

        if not token:
            return Response({"error": "No token provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            #  Verify Google ID token
            idinfo = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            # Extract email & name
            email = idinfo.get("email")
            name = idinfo.get("name", "")

            if not email:
                return Response({"error": "Email not found in Google data"}, status=status.HTTP_400_BAD_REQUEST)

            #Create or fetch user
            user, created = User.objects.get_or_create(email=email, defaults={"name": name})
            user.is_verified = True
            user.save()

            #Generate JWT tokens
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "Google login successful",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "email": user.email,
                "name": user.name
            }, status=status.HTTP_200_OK)

        except ValueError:
            return Response({"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





#signup view
class SignupView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        name = request.data.get('name')

        # CASE 1: User already exists
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.is_verified:
                return Response({"error": "User already exists and is verified. Please login."}, status=400)
            else:
                # resend OTP
                otp = OTP.generate_otp(email)
                send_mail(
                    subject="Your Byte2Boss OTP Code",
                    message=f"Your new verification code is {otp.code}. It will expire in 5 minutes.",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[email],
                )
                return Response({"message": "User exists but not verified. OTP resent."}, status=200)

        # CASE 2: New user → create user
        user = User.objects.create_user(email=email, name=name, password=password)
        user.is_verified = False
        user.save()

        otp = OTP.generate_otp(email)
        send_mail(
            subject="Your Byte2Boss OTP Code",
            message=f"Your verification code is {otp.code}. It will expire in 5 minutes.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to email"}, status=201)


#verify otp view
class VerifyOTPView(APIView):
    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('otp')

        try:
            otp = OTP.objects.filter(email=email).latest('created_at')
        except OTP.DoesNotExist:
            return Response({"error": "No OTP found"}, status=400)

        if otp.code != code:
            return Response({"error": "Invalid OTP"}, status=400)
        if not otp.is_valid():
            return Response({"error": "OTP expired"}, status=400)

        user = User.objects.get(email=email)
        user.is_verified = True
        user.save()

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "name" :  user.name,
            "email": user.email
        },status=200
        )

#login view 
class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response({"error": "Email and password are required"}, status=400)

        # Authenticate user
        user = authenticate(request, email=email, password=password)

        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        if not user.is_verified:
            return Response({"error": "Account not verified. Please verify OTP first."}, status=403)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "name" :  user.name,
            "email": user.email
        },status=200)
