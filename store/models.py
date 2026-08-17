from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User
from decimal import Decimal


class Category(models.Model):
    """Hierarchical category model supporting multi-level tech product trees."""
    COMPONENT_TYPE_CHOICES = [
        ('none', 'Not a PC Component'),
        ('cpu', 'Processor (CPU)'),
        ('motherboard', 'Motherboard'),
        ('ram', 'Memory (RAM)'),
        ('storage', 'Storage (SSD/HDD)'),
        ('gpu', 'Graphics Card (GPU)'),
        ('psu', 'Power Supply (PSU)'),
        ('case', 'Casing'),
        ('cooler', 'CPU Cooler'),
    ]

    name = models.CharField(max_length=120, db_index=True)
    slug = models.SlugField(max_length=140, unique=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children'
    )
    description = models.TextField(blank=True, null=True)
    icon_name = models.CharField(max_length=50, default='cpu', help_text='Icon class or SVG key')
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    component_type = models.CharField(
        max_length=20, 
        choices=COMPONENT_TYPE_CHOICES, 
        default='none',
        help_text='Maps category to PC Builder slot'
    )
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Brand(models.Model):
    """Tech manufacturer/brand model (e.g., ASUS, MSI, Intel, AMD, Corsair)."""
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True)
    logo = models.ImageField(upload_to='brands/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Core product model representing tech hardware item."""
    STOCK_STATUS_CHOICES = [
        ('in_stock', 'In Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('pre_order', 'Pre-Order'),
        ('upcoming', 'Upcoming'),
    ]

    title = models.CharField(max_length=255, db_index=True)
    slug = models.SlugField(max_length=280, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    model_number = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    description = models.TextField()
    base_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))],
        db_index=True
    )
    discount_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    wattage = models.PositiveIntegerField(
        default=0, 
        help_text='Power consumption in Watts for PC Builder calculation'
    )
    warranty = models.CharField(max_length=100, default='1 Year Brand Warranty')
    stock_status = models.CharField(
        max_length=20, 
        choices=STOCK_STATUS_CHOICES, 
        default='in_stock',
        db_index=True
    )
    is_active = models.BooleanField(default=True, db_index=True)
    is_featured = models.BooleanField(default=False, db_index=True)
    is_deal_of_day = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'brand', 'is_active']),
            models.Index(fields=['base_price', 'is_active']),
        ]

    def __str__(self):
        return f"{self.brand.name} - {self.title}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand.name}-{self.title}")
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price < self.base_price:
            return self.discount_price
        return self.base_price

    @property
    def save_amount(self):
        if self.discount_price and self.discount_price < self.base_price:
            return self.base_price - self.discount_price
        return Decimal('0.00')

    @property
    def discount_percentage(self):
        if self.discount_price and self.discount_price < self.base_price:
            savings = self.base_price - self.discount_price
            return int((savings / self.base_price) * 100)
        return 0

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 5.0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    def get_price_range(self):
        active_variants = self.variants.filter(is_active=True)
        if active_variants.exists():
            prices = [v.effective_price for v in active_variants]
            return min(prices), max(prices)
        return self.effective_price, self.effective_price


# =====================================================================
# EAV (Entity-Attribute-Value) Specification Pattern Models
# =====================================================================

class SpecificationKey(models.Model):
    name = models.CharField(max_length=100, db_index=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='spec_keys'
    )
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name_plural = "Specification Keys"
        ordering = ['display_order', 'name']
        unique_together = ('name', 'category')

    def __str__(self):
        if self.category:
            return f"{self.category.name} -> {self.name}"
        return self.name


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='specifications'
    )
    key = models.ForeignKey(
        SpecificationKey, 
        on_delete=models.CASCADE, 
        related_name='product_specs'
    )
    value = models.CharField(max_length=255, db_index=True)

    class Meta:
        verbose_name_plural = "Product Specifications"
        unique_together = ('product', 'key')
        indexes = [
            models.Index(fields=['key', 'value']),
            models.Index(fields=['product', 'key']),
        ]

    def __str__(self):
        return f"{self.product.title} | {self.key.name}: {self.value}"


# =====================================================================
# Multi-Variant Pricing & Inventory Models
# =====================================================================

class VariantAttribute(models.Model):
    name = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name


class VariantAttributeValue(models.Model):
    attribute = models.ForeignKey(
        VariantAttribute, 
        on_delete=models.CASCADE, 
        related_name='values'
    )
    value = models.CharField(max_length=120)

    class Meta:
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    sku = models.CharField(max_length=80, unique=True, db_index=True)
    title = models.CharField(max_length=200)
    price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_price = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    stock_quantity = models.PositiveIntegerField(default=0)
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    attribute_values = models.ManyToManyField(
        VariantAttributeValue, 
        related_name='product_variants'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['price']
        indexes = [
            models.Index(fields=['product', 'is_active']),
            models.Index(fields=['sku']),
        ]

    def __str__(self):
        return f"{self.product.title} - {self.title} (${self.effective_price})"

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def is_in_stock(self):
        return self.stock_quantity > 0


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-is_primary', 'display_order']

    def __str__(self):
        return f"Image for {self.product.title}"


# =====================================================================
# Reviews, Q&A, and Hero Banners
# =====================================================================

class Banner(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='banners/', blank=True, null=True)
    button_text = models.CharField(max_length=50, default='Shop Now')
    button_link = models.CharField(max_length=255, default='/catalog/')
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order']

    def __str__(self):
        return self.title


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} review on {self.product.title} ({self.rating}★)"


class Question(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Q by {self.user.username} on {self.product.title}"
