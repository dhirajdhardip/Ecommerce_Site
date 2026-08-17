from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from .forms import UserRegisterForm, ShippingAddressForm
from .models import ShippingAddress

class RegisterView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        form = UserRegisterForm()
        return render(request, 'users/register.html', {'form': form})

    def post(self, request):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            messages.success(request, f"Welcome to TechVault, {user.username}!")
            return redirect('users:profile')
        return render(request, 'users/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('users:profile')
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect(request.GET.get('next') or 'users:profile')
        messages.error(request, "Invalid username or password.")
        return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have logged out successfully.")
    return redirect('store:home')

@login_required
def profile_view(request):
    addresses = ShippingAddress.objects.filter(user=request.user)
    orders = request.user.orders.all() if hasattr(request.user, 'orders') else []
    return render(request, 'users/profile.html', {
        'addresses': addresses,
        'orders': orders,
    })
