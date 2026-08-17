from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount_type', 'discount_value', 'min_order_amount', 'active', 'expires_at', 'used_count', 'usage_limit']
    list_filter = ['active', 'discount_type']
    search_fields = ['code']
