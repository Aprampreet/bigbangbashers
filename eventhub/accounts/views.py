# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from .tasks import send_registration_email, send_login_email
from celery.exceptions import OperationalError  # Import the specific Celery exception
import logging

logger = logging.getLogger(__name__)

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                # Attempt to queue the registration email task
                send_registration_email.delay(user.email, user.username)
                messages.success(request, "Account created successfully! A confirmation email has been sent.")
            except OperationalError as e:
                # This block runs ONLY if Redis is down
                logger.error(f"Celery email task failed for user {user.username}: {e}")
                messages.warning(request, "Account created, but we couldn’t send the confirmation email due to a connection issue.")
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if not email or not password:
            messages.error(request, "Please fill all fields")
            return render(request, 'accounts/login.html')

        try:
            user_obj = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "No account found with this email")
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=user_obj.username, password=password)
        if user is not None:
            login(request, user)
            try:
                # Optionally send login email, but don't let it block the user
                send_login_email.delay(user.email, user.username)
            except OperationalError as e:
                # If Redis is down, just log it and continue.
                # The user experience for logging in should be seamless.
                logger.error(f"Celery login email task failed for user {user.username}: {e}")
            return redirect('/')
        else:
            messages.error(request, "Incorrect password")
    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')