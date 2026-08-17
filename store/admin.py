from django.contrib import admin
from .models import (
    Category, Brand, Product, SpecificationKey, 
    ProductSpecification, VariantAttribute, VariantAttributeValue, 
    ProductVariant, ProductImage
)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 2
    autocomplete_fields = ['key']


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    filter_horizontal = ['attribute_values']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'slug', 'is_active', 'display_order']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'website', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'brand', 'category', 'base_price', 'discount_price', 'stock_status', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'stock_status', 'brand', 'category']
    search_fields = ['title', 'model_number', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProductImageInline, ProductSpecificationInline, ProductVariantInline]


@admin.register(SpecificationKey)
class SpecificationKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'display_order']
    list_filter = ['category']
    search_fields = ['name']


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ['product', 'key', 'value']
    list_filter = ['key']
    search_fields = ['product__title', 'key__name', 'value']


@admin.register(VariantAttribute)
class VariantAttributeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(VariantAttributeValue)
class VariantAttributeValueAdmin(admin.ModelAdmin):
    list_display = ['attribute', 'value']
    list_filter = ['attribute']


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product', 'sku', 'title', 'price', 'discount_price', 'stock_quantity', 'is_default', 'is_active']
    list_filter = ['is_active', 'is_default']
    search_fields = ['sku', 'title', 'product__title']
