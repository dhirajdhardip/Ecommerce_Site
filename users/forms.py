from django import forms
from django.contrib.auth.models import User
from .models import ShippingAddress

class UserRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Choose Password', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name', 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-sm text-slate-200'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        cpwd = cleaned_data.get("confirm_password")
        if pwd != cpwd:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'phone', 'division', 'district', 'area', 'full_address', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
            'phone': forms.TextInput(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
            'division': forms.Select(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
            'district': forms.TextInput(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
            'area': forms.TextInput(attrs={'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
            'full_address': forms.Textarea(attrs={'rows': 3, 'class': 'w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm text-slate-200'}),
        }
