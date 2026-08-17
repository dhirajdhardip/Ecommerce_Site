from django.db import models
from django.contrib.auth.models import User
from store.models import Product

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', null=True, blank=True)
    session_key = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='in_wishlists')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username if self.user else self.session_key} - {self.product.title}"
