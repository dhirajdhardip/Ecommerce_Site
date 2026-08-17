from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from django.utils import timezone

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage Discount (%)'),
        ('fixed', 'Fixed Amount Discount ($)'),
    ]

    code = models.CharField(max_length=50, unique=True, db_index=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES, default='percentage')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    active = models.BooleanField(default=True, db_index=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    usage_limit = models.PositiveIntegerField(default=100)
    used_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"Coupon {self.code} ({self.discount_value}{'%' if self.discount_type == 'percentage' else '$'})"

    def is_valid(self, subtotal=Decimal('0.00')):
        if not self.active:
            return False, "Coupon is inactive."
        if self.expires_at and timezone.now() > self.expires_at:
            return False, "Coupon has expired."
        if self.used_count >= self.usage_limit:
            return False, "Coupon usage limit reached."
        if Decimal(subtotal) < self.min_order_amount:
            return False, f"Minimum order of ${self.min_order_amount} required for this coupon."
        return True, "Valid"

    def calculate_discount(self, subtotal):
        subtotal = Decimal(subtotal)
        if self.discount_type == 'percentage':
            return (subtotal * (self.discount_value / Decimal('100'))).quantize(Decimal('0.01'))
        return min(self.discount_value, subtotal)
