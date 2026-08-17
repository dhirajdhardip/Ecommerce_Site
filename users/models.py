from django.db import models
from django.contrib.auth.models import User

class ShippingAddress(models.Model):
    DIVISION_CHOICES = [
        ('dhaka', 'Dhaka'),
        ('chattogram', 'Chattogram'),
        ('rajshahi', 'Rajshahi'),
        ('khulna', 'Khulna'),
        ('barishal', 'Barishal'),
        ('sylhet', 'Sylhet'),
        ('rangpur', 'Rangpur'),
        ('mymensingh', 'Mymensingh'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shipping_addresses')
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    division = models.CharField(max_length=50, choices=DIVISION_CHOICES, default='dhaka')
    district = models.CharField(max_length=80)
    area = models.CharField(max_length=80)
    full_address = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Shipping Addresses"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.full_name} - {self.area}, {self.district}"
