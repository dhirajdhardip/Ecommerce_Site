from django.contrib import admin
from .models import Order, OrderItem, OrderStatusLog

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'variant', 'title', 'unit_price', 'quantity', 'total_price']

class OrderStatusLogInline(admin.TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ['status', 'notes', 'created_at']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'full_name', 'phone', 'district', 'payment_method', 'status', 'grand_total', 'created_at']
    list_filter = ['status', 'payment_method', 'division', 'created_at']
    search_fields = ['order_number', 'full_name', 'phone', 'email']
    inlines = [OrderItemInline, OrderStatusLogInline]
    actions = ['mark_confirmed', 'mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled']

    @admin.action(description="Mark selected orders as Confirmed")
    def mark_confirmed(self, request, queryset):
        for order in queryset:
            order.status = 'confirmed'
            order.save()
            OrderStatusLog.objects.create(order=order, status='confirmed', notes='Updated via admin panel.')
        self.message_user(request, "Selected orders updated to Confirmed.")

    @admin.action(description="Mark selected orders as Processing")
    def mark_processing(self, request, queryset):
        for order in queryset:
            order.status = 'processing'
            order.save()
            OrderStatusLog.objects.create(order=order, status='processing', notes='Updated via admin panel.')
        self.message_user(request, "Selected orders updated to Processing.")

    @admin.action(description="Mark selected orders as Shipped")
    def mark_shipped(self, request, queryset):
        for order in queryset:
            order.status = 'shipped'
            order.save()
            OrderStatusLog.objects.create(order=order, status='shipped', notes='Updated via admin panel.')
        self.message_user(request, "Selected orders updated to Shipped.")

    @admin.action(description="Mark selected orders as Delivered")
    def mark_delivered(self, request, queryset):
        for order in queryset:
            order.status = 'delivered'
            order.save()
            OrderStatusLog.objects.create(order=order, status='delivered', notes='Updated via admin panel.')
        self.message_user(request, "Selected orders updated to Delivered.")

    @admin.action(description="Mark selected orders as Cancelled")
    def mark_cancelled(self, request, queryset):
        for order in queryset:
            order.status = 'cancelled'
            order.save()
            OrderStatusLog.objects.create(order=order, status='cancelled', notes='Updated via admin panel.')
        self.message_user(request, "Selected orders updated to Cancelled.")
