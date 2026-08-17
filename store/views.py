import json
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.db.models import Q, Min, Max
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Product, Category, Brand, SpecificationKey, 
    ProductSpecification, ProductVariant, VariantAttributeValue,
    Banner, Review, Question
)


class LiveSearchApiView(View):
    """
    Real-Time Autocomplete Search API returning matching product suggestions.
    """
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'status': 'success', 'results': []})

        products = Product.objects.filter(
            Q(title__icontains=query) |
            Q(brand__name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(model_number__icontains=query),
            is_active=True
        ).select_related('brand', 'category').prefetch_related('images')[:6]

        results = []
        for p in products:
            primary_img = p.images.filter(is_primary=True).first() or p.images.first()
            img_url = primary_img.image.url if primary_img else '/static/images/placeholder.png'

            results.append({
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'brand': p.brand.name,
                'category': p.category.name,
                'price': float(p.effective_price),
                'image': img_url,
                'model_number': p.model_number or ''
            })

        return JsonResponse({'status': 'success', 'query': query, 'results': results})


class HomePageView(View):
    """
    Renders Star Tech inspired landing page layout with Hero Banners,
    Quick Category Icons, Featured Products, Deals of the Day, and PC Builder CTA.
    """
    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')
        brands = Brand.objects.filter(is_active=True)
        banners = Banner.objects.filter(is_active=True)
        
        featured_products = Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related('brand', 'category').prefetch_related('images', 'specifications__key')[:8]

        deal_products = Product.objects.filter(
            is_active=True, discount_price__isnull=False
        ).select_related('brand', 'category').prefetch_related('images')[:4]

        context = {
            'categories': categories,
            'brands': brands,
            'banners': banners,
            'featured_products': featured_products,
            'deal_products': deal_products,
        }
        return render(request, 'store/home.html', context)


class ProductDetailView(View):
    """
    Star Tech Detailed Product Page featuring Technical Spec tables (EAV pattern),
    variant pricing selector, warranty info, reviews, Q&A, and related products.
    """
    def get(self, request, slug, *args, **kwargs):
        product = get_object_or_404(
            Product.objects.select_related('brand', 'category').prefetch_related(
                'specifications__key', 'variants__attribute_values__attribute', 'images', 'reviews__user', 'questions__user'
            ),
            slug=slug,
            is_active=True
        )
        
        related_products = Product.objects.filter(
            category=product.category, is_active=True
        ).exclude(id=product.id).select_related('brand')[:4]

        categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')

        context = {
            'product': product,
            'specifications': product.specifications.select_related('key').all(),
            'variants': product.variants.filter(is_active=True),
            'reviews': product.reviews.filter(is_approved=True),
            'questions': product.questions.all(),
            'related_products': related_products,
            'categories': categories,
        }
        return render(request, 'store/product_detail.html', context)


class PcBuilderView(View):
    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(is_active=True, parent__isnull=True).prefetch_related('children')
        
        component_slots = [
            {'type': 'cpu', 'name': 'Processor (CPU)', 'required': True, 'icon': 'cpu'},
            {'type': 'motherboard', 'name': 'Motherboard', 'required': True, 'icon': 'server'},
            {'type': 'ram', 'name': 'Memory (RAM)', 'required': True, 'icon': 'memory'},
            {'type': 'storage', 'name': 'Storage (SSD / HDD)', 'required': True, 'icon': 'database'},
            {'type': 'gpu', 'name': 'Graphics Card (GPU)', 'required': False, 'icon': 'tv'},
            {'type': 'psu', 'name': 'Power Supply Unit (PSU)', 'required': True, 'icon': 'zap'},
            {'type': 'case', 'name': 'Casing / Enclosure', 'required': True, 'icon': 'box'},
            {'type': 'cooler', 'name': 'CPU Cooler', 'required': False, 'icon': 'wind'},
        ]

        context = {
            'categories': categories,
            'component_slots': component_slots,
        }
        return render(request, 'store/pc_builder.html', context)


class PcBuilderApiView(View):
    def get(self, request, component_type, *args, **kwargs):
        products = Product.objects.filter(
            category__component_type=component_type,
            is_active=True
        ).select_related('brand', 'category').prefetch_related('images', 'specifications__key', 'variants')

        data = []
        for p in products:
            primary_img = p.images.filter(is_primary=True).first() or p.images.first()
            img_url = primary_img.image.url if primary_img else '/static/images/placeholder.png'
            
            default_var = p.variants.filter(is_active=True, is_default=True).first() or p.variants.first()
            variant_id = default_var.id if default_var else None

            data.append({
                'id': p.id,
                'variant_id': variant_id,
                'title': p.title,
                'brand': p.brand.name,
                'price': float(p.effective_price),
                'wattage': p.wattage,
                'image': img_url,
                'stock_status': p.stock_status,
                'stock_display': p.get_stock_status_display(),
                'model_number': p.model_number or 'N/A'
            })

        return JsonResponse({'status': 'success', 'component_type': component_type, 'products': data})


class ProductFilterView(View):
    """
    High-Performance AJAX API View for Filtering Tech Products.
    Processes multiple GET parameters/arrays for brands, categories, price bounds,
    stock status, search queries, and dynamic EAV technical specifications.
    """
    def get(self, request, *args, **kwargs):
        queryset = Product.objects.filter(is_active=True).select_related(
            'brand', 'category'
        ).prefetch_related(
            'specifications__key',
            'variants__attribute_values',
            'images'
        )

        def get_param_list(param_name):
            values = request.GET.getlist(param_name) or request.GET.getlist(f'{param_name}[]')
            if not values and request.GET.get(param_name):
                raw = request.GET.get(param_name)
                values = [v.strip() for v in raw.split(',') if v.strip()]
            return values

        search_query = request.GET.get('search', '').strip()
        brand_params = get_param_list('brands')
        category_params = get_param_list('categories')
        stock_params = get_param_list('stock')
        min_price_str = request.GET.get('min_price')
        max_price_str = request.GET.get('max_price')
        sort_by = request.GET.get('sort', 'newest')
        page_num = request.GET.get('page', 1)
        page_size = int(request.GET.get('page_size', 12))

        active_filters = {
            'search': search_query,
            'brands': brand_params,
            'categories': category_params,
            'stock': stock_params,
            'min_price': min_price_str,
            'max_price': max_price_str,
            'specs': {}
        }

        # Global Search query
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(brand__name__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(model_number__icontains=search_query)
            )

        # Filter by Brand
        if brand_params:
            brand_q = Q()
            for b in brand_params:
                if b.isdigit():
                    brand_q |= Q(brand_id=int(b))
                else:
                    brand_q |= Q(brand__slug=b)
            queryset = queryset.filter(brand_q)

        # Filter by Category
        if category_params:
            cat_q = Q()
            for c in category_params:
                category_obj = Category.objects.filter(id=int(c)).first() if c.isdigit() else Category.objects.filter(slug=c).first()
                if category_obj:
                    sub_ids = category_obj.children.values_list('id', flat=True)
                    cat_q |= Q(category_id=category_obj.id) | Q(category_id__in=sub_ids)
            queryset = queryset.filter(cat_q)

        # Filter by Stock Status
        if stock_params:
            queryset = queryset.filter(stock_status__in=stock_params)

        # Dynamic EAV Specifications Filtering
        eav_filters = {}
        for key, val in request.GET.items():
            spec_key_name = None
            if key.startswith('spec_'):
                spec_key_name = key[5:]
            elif key.startswith('specs[') and key.endswith(']'):
                spec_key_name = key[6:-1]

            if spec_key_name:
                val_list = request.GET.getlist(key) or [v.strip() for v in val.split(',') if v.strip()]
                eav_filters[spec_key_name] = val_list

        active_filters['specs'] = eav_filters

        for spec_key, val_list in eav_filters.items():
            if spec_key.isdigit():
                queryset = queryset.filter(
                    specifications__key_id=int(spec_key),
                    specifications__value__in=val_list
                )
            else:
                queryset = queryset.filter(
                    specifications__key__name__iexact=spec_key,
                    specifications__value__in=val_list
                )

        # Price Range Filter
        try:
            if min_price_str:
                min_p = Decimal(min_price_str)
                queryset = queryset.filter(
                    Q(discount_price__gte=min_p) | 
                    Q(discount_price__isnull=True, base_price__gte=min_p) |
                    Q(variants__price__gte=min_p)
                ).distinct()
            if max_price_str:
                max_p = Decimal(max_price_str)
                queryset = queryset.filter(
                    Q(discount_price__lte=max_p) | 
                    Q(discount_price__isnull=True, base_price__lte=max_p) |
                    Q(variants__price__lte=max_p)
                ).distinct()
        except (ValueError, ArithmeticError):
            pass

        aggregate_prices = queryset.aggregate(min_avail=Min('base_price'), max_avail=Max('base_price'))
        min_avail = float(aggregate_prices['min_avail']) if aggregate_prices['min_avail'] is not None else 0.0
        max_avail = float(aggregate_prices['max_avail']) if aggregate_prices['max_avail'] is not None else 0.0

        # Sorting
        sort_map = {
            'price_asc': 'base_price',
            'price_desc': '-base_price',
            'newest': '-created_at',
            'title_asc': 'title',
        }
        queryset = queryset.order_by(sort_map.get(sort_by, '-created_at'))

        # Pagination
        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        products_data = []
        for p in page_obj:
            primary_img = p.images.filter(is_primary=True).first() or p.images.first()
            img_url = primary_img.image.url if primary_img else '/static/images/placeholder.png'

            specs_data = [{'key': spec.key.name, 'value': spec.value} for spec in p.specifications.all()]
            variants_data = [
                {
                    'id': v.id,
                    'sku': v.sku,
                    'title': v.title,
                    'price': str(v.price),
                    'discount_price': str(v.discount_price) if v.discount_price else None,
                    'effective_price': float(v.effective_price),
                    'stock_quantity': v.stock_quantity,
                    'is_in_stock': v.is_in_stock,
                    'is_default': v.is_default
                }
                for v in p.variants.filter(is_active=True)
            ]

            min_price, max_price = p.get_price_range()

            products_data.append({
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'model_number': p.model_number,
                'brand': {'id': p.brand.id, 'name': p.brand.name, 'slug': p.brand.slug},
                'category': {'id': p.category.id, 'name': p.category.name, 'slug': p.category.slug},
                'base_price': str(p.base_price),
                'discount_price': str(p.discount_price) if p.discount_price else None,
                'effective_price': float(p.effective_price),
                'save_amount': float(p.save_amount),
                'discount_percentage': p.discount_percentage,
                'price_range': {'min': float(min_price), 'max': float(max_price)},
                'stock_status': p.stock_status,
                'stock_status_display': p.get_stock_status_display(),
                'is_featured': p.is_featured,
                'primary_image': img_url,
                'specifications': specs_data,
                'variants': variants_data
            })

        return JsonResponse({
            'status': 'success',
            'total_count': paginator.count,
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'price_bounds': {'min': min_avail, 'max': max_avail},
            'active_filters': active_filters,
            'products': products_data
        })


class AddToCartView(View):
    """
    Delegates single item cart addition to Cart helper class.
    """
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            variant_id = data.get('variant_id')
            product_id = data.get('product_id')
            quantity = int(data.get('quantity', 1))

            variant = None
            product = None

            if variant_id:
                variant = ProductVariant.objects.filter(id=variant_id, is_active=True).first()
                if variant:
                    product = variant.product
            if not product and product_id:
                product = Product.objects.filter(id=product_id, is_active=True).first()
                if product:
                    variant = product.variants.filter(is_active=True, is_default=True).first() or product.variants.first()

            if not product and not variant:
                return JsonResponse({'status': 'error', 'message': 'Product unavailable.'}, status=404)

            from cart.cart import Cart
            cart = Cart(request)
            var_id = variant.id if variant else None
            str_var_id = str(var_id) if var_id else str(product.id)

            current_qty = cart.cart.get(str_var_id, {}).get('quantity', 0)
            new_qty = current_qty + quantity

            price = float(variant.effective_price) if variant else float(product.effective_price)
            title = product.title
            var_title = variant.title if variant else 'Standard'

            cart.cart[str_var_id] = {
                'variant_id': var_id,
                'product_id': product.id,
                'product_title': title,
                'variant_title': var_title,
                'unit_price': price,
                'quantity': new_qty,
                'total_price': round(price * new_qty, 2)
            }
            cart.save()

            return JsonResponse({
                'status': 'success',
                'message': f'"{title}" added to cart successfully!',
                'cart_summary': {
                    'total_items': cart.get_total_items(),
                    'subtotal': float(cart.get_subtotal())
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


class ProductCatalogView(View):

    def get(self, request, *args, **kwargs):
        categories = Category.objects.filter(is_active=True).select_related('parent').order_by('display_order', 'name')
        brands = Brand.objects.filter(is_active=True)
        spec_keys = SpecificationKey.objects.all().prefetch_related('product_specs')

        context = {
            'categories': categories,
            'brands': brands,
            'spec_keys': spec_keys,
        }
        return render(request, 'store/product_list.html', context)
