from django.contrib import admin
from .models import ShippingAddress

@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'full_name', 'phone', 'division', 'district', 'is_default']
    list_filter = ['division', 'district']
    search_fields = ['full_name', 'phone', 'full_address']
