import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .models import WishlistItem
from store.models import Product
from cart.cart import Cart

class WishlistView(View):
    def get(self, request):
        if request.user.is_authenticated:
            items = WishlistItem.objects.filter(user=request.user).select_related('product__brand')
        else:
            s_key = request.session.session_key
            items = WishlistItem.objects.filter(session_key=s_key).select_related('product__brand') if s_key else []
        return render(request, 'wishlist/wishlist.html', {'wishlist_items': items})

class ToggleWishlistApiView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data.get('product_id')
            product = get_object_or_404(Product, id=product_id)

            if not request.session.session_key:
                request.session.create()

            s_key = request.session.session_key
            user = request.user if request.user.is_authenticated else None

            if user:
                item, created = WishlistItem.objects.get_or_create(user=user, product=product)
            else:
                item, created = WishlistItem.objects.get_or_create(session_key=s_key, product=product)

            if not created:
                item.delete()
                added = False
                msg = f"'{product.title}' removed from Wishlist."
            else:
                added = True
                msg = f"'{product.title}' added to Wishlist!"

            count = WishlistItem.objects.filter(user=user).count() if user else WishlistItem.objects.filter(session_key=s_key).count()

            return JsonResponse({'status': 'success', 'added': added, 'message': msg, 'total_wishlist': count})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class MoveWishlistToCartView(View):
    def post(self, request, item_id):
        try:
            wishlist_item = get_object_or_404(WishlistItem, id=item_id)
            product = wishlist_item.product
            variant = product.variants.filter(is_active=True, is_default=True).first() or product.variants.first()

            cart = Cart(request)
            var_id = variant.id if variant else None
            str_var_id = str(var_id) if var_id else str(product.id)

            cart.cart[str_var_id] = {
                'variant_id': var_id,
                'product_id': product.id,
                'product_title': product.title,
                'variant_title': variant.title if variant else 'Standard',
                'unit_price': float(product.effective_price),
                'quantity': 1,
                'total_price': float(product.effective_price)
            }
            cart.save()
            wishlist_item.delete()

            return JsonResponse({
                'status': 'success',
                'message': f"Moved '{product.title}' to Cart!",
                'cart_summary': {'total_items': cart.get_total_items(), 'subtotal': float(cart.get_subtotal())}
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
