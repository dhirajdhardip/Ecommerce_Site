import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from .cart import Cart
from .models import Coupon
from store.models import ProductVariant, Product

class CartView(View):
    def get(self, request):
        cart = Cart(request)
        return render(request, 'cart/cart.html', {'cart': cart})

class UpdateCartItemView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            item_key = str(data.get('item_key'))
            action = data.get('action') # 'increase', 'decrease', 'update'
            new_qty = data.get('quantity')

            cart = Cart(request)
            if item_key in cart.cart:
                if action == 'increase':
                    cart.cart[item_key]['quantity'] += 1
                elif action == 'decrease':
                    cart.cart[item_key]['quantity'] -= 1
                    if cart.cart[item_key]['quantity'] < 1:
                        del cart.cart[item_key]
                elif action == 'update' and new_qty is not None:
                    qty = int(new_qty)
                    if qty < 1:
                        del cart.cart[item_key]
                    else:
                        cart.cart[item_key]['quantity'] = qty

                cart.save()

            return JsonResponse({
                'status': 'success',
                'cart_summary': {
                    'total_items': cart.get_total_items(),
                    'subtotal': float(cart.get_subtotal()),
                    'shipping': float(cart.get_shipping_cost()),
                    'discount': float(cart.get_discount()),
                    'grand_total': float(cart.get_grand_total())
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class RemoveCartItemView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            item_key = str(data.get('item_key'))
            cart = Cart(request)
            if item_key in cart.cart:
                del cart.cart[item_key]
                cart.save()
            return JsonResponse({
                'status': 'success',
                'cart_summary': {
                    'total_items': cart.get_total_items(),
                    'subtotal': float(cart.get_subtotal()),
                    'grand_total': float(cart.get_grand_total())
                }
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

class ApplyCouponView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            code = data.get('coupon_code', '').strip()
            cart = Cart(request)

            try:
                coupon = Coupon.objects.get(code__iexact=code, active=True)
                valid, msg = coupon.is_valid(cart.get_subtotal())
                if valid:
                    request.session['coupon_code'] = coupon.code
                    request.session.modified = True
                    return JsonResponse({
                        'status': 'success',
                        'message': f"Coupon '{coupon.code}' applied successfully!",
                        'cart_summary': {
                            'subtotal': float(cart.get_subtotal()),
                            'discount': float(cart.get_discount()),
                            'grand_total': float(cart.get_grand_total())
                        }
                    })
                return JsonResponse({'status': 'error', 'message': msg}, status=400)
            except Coupon.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Invalid coupon code.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
