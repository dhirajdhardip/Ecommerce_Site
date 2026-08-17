from django.contrib import admin
from .models import WishlistItem

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_key', 'product', 'created_at']
    search_fields = ['product__title', 'session_key']
