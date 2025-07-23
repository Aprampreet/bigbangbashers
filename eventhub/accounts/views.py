from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm
from django.contrib import messages
from django.contrib.auth.models import User
from .tasks import send_registration_email,send_login_email


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_registration_email.delay(user.email, user.username)  # ✅ Registration email
            messages.success(request, "Account created successfully! A confirmation email has been sent.")
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            user = authenticate(username=user.username, password=password)
            if user is not None:
                login(request, user)
                send_login_email.delay(user.email, user.username)  
                return redirect('/')
            else:
                messages.error(request, "Invalid credentials")
        except User.DoesNotExist:
            messages.error(request, "User with that email doesn't exist")
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')
