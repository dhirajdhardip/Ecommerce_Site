from .models import Category, Brand

def categories_processor(request):
    """Provides global categories and brands to all templates for mega menu navigation."""
    categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')
    brands = Brand.objects.filter(is_active=True)[:10]
    return {
        'nav_categories': categories,
        'nav_brands': brands,
    }
