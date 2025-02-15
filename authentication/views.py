import random
from django.core.mail import send_mail
from .models import CustomUser, OTPCode
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from rest_framework.views import APIView
from .forms import RegisterForm, LoginForm, VerifyOTPForm
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

OTP_STORE = {}

class RegisterView(APIView):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'authentication/register.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if request.method == 'POST':
            email = request.POST.get('email')
            password = request.POST.get('password1')
            confirm_password = request.POST.get('password2')

            if password != confirm_password:
                messages.error(request, "Passwords do not match!")
                return render(request, 'authentication/register.html', {'form': form})

            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, "Email is already registered!")
                return render(request, 'authentication/register.html', {'form': form})
            user = CustomUser.objects.create_user(
                email=email,
                password=password,
                username=email.split('@')[0]
            )
            user.role = request.POST.get('role')
            user.save()
            if user:
                otp_instance, created = OTPCode.objects.get_or_create(user=user)
                otp_instance.code = f"{random.randint(100000, 999999)}"
                otp_instance.created_at = now()
                otp_instance.save()
                #print('it is otp_code=', otp_instance.code)
                send_mail(
                    "Ваш OTP-код",
                    f"Ваш код подтверждения: {otp_instance.code}",
                    settings.EMAIL_HOST_USER,
                    [email],
                    fail_silently=False,
                )

                request.session["email"] = email  # Store email in session

                messages.success(request, "OTP-код отправлен на вашу почту.")
                return redirect("otp_verification")

        return render(request, "authentication/otp_verification.html")


class verify_otp_view(APIView):
    """Отображает форму подтверждения OTP и выполняет аутентификацию."""

    def get(self, request):
        form = VerifyOTPForm(request.POST)
        return render(request, 'authentication/otp_verification.html', {'form': form})

    def post(self, request):
        form = VerifyOTPForm(request.POST)
        email = request.session.get("email")
        user = CustomUser.objects.filter(email=email).first()
        otp = OTPCode.objects.filter(user=user).first()
        if request.method == "POST":
            code = request.POST.get("otp")
            if otp and otp.is_valid() and otp.code == code:
                login(request, user)
                messages.success(request, "Вы успешно вошли!")
                return redirect("home")  # Перенаправляем на success_page

            messages.error(request, "Неверный или просроченный код.")
            return render(request, "authentication/otp_verification.html", {"form": form})
        else:
            form = VerifyOTPForm()
        return render(request, "authentication/otp_verification.html", {"form": form})


class ResendOTPView(APIView):
    def post(self, request):
        # Extract the email from the session
        email = request.session.get("email")
        if not email:
            messages.error(request, "Email not found in session.")
            return redirect("otp_verification")

        # Check if the user exists
        user = CustomUser.objects.filter(email=email).first()
        if not user:
            messages.error(request, "User not found.")
            return redirect("otp_verification")

        # Check if an OTP already exists
        otp_instance = OTPCode.objects.filter(user=user).first()

        # Optional: Cooldown logic to prevent spamming
        if otp_instance and (now() - otp_instance.created_at).total_seconds() < 60:
            messages.error(request, "Please wait before resending OTP.")
            return redirect("otp_verification")

        # Generate a new OTP
        new_otp = f"{random.randint(100000, 999999)}"

        # Update or create the OTP record
        if otp_instance:
            otp_instance.code = new_otp
            otp_instance.created_at = now()
            otp_instance.save()
        else:
            OTPCode.objects.create(user=user, code=new_otp)

        # Send the OTP via email
        send_mail(
            "Ваш новый OTP-код",
            f"Ваш код подтверждения: {new_otp}",
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )

        messages.success(request, "A new OTP has been sent to your email.")
        return redirect("otp_verification")

class LoginView(APIView):
    def get(self, request):
        form = LoginForm()
        return render(request, 'authentication/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "Login successful!")
                return redirect('home')
            else:
                messages.error(request, "Invalid email or password. Please try again.")

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.capitalize()}: {error}")

        return render(request, 'authentication/login.html', {'form': form})


@login_required
def home_view(request):
    return render(request, 'authentication/home.html')


class LogoutView(APIView):
    def get(self, request):
        logout(request)
        return redirect('login')