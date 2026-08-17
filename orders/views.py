from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.db import transaction
from cart.cart import Cart
from .models import Order, OrderItem, OrderStatusLog
from users.models import ShippingAddress
from store.models import ProductVariant, Product

class CheckoutView(View):
    def get(self, request):
        cart = Cart(request)
        if cart.get_total_items() == 0:
            messages.warning(request, "Your cart is currently empty.")
            return redirect('store:catalog')

        default_address = None
        if request.user.is_authenticated:
            default_address = ShippingAddress.objects.filter(user=request.user, is_default=True).first() or ShippingAddress.objects.filter(user=request.user).first()

        context = {
            'cart': cart,
            'default_address': default_address,
        }
        return render(request, 'orders/checkout.html', context)

    def post(self, request):
        cart = Cart(request)
        if cart.get_total_items() == 0:
            messages.error(request, "Your cart is empty.")
            return redirect('store:catalog')

        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        division = request.POST.get('division', 'dhaka').strip()
        district = request.POST.get('district', '').strip()
        area = request.POST.get('area', '').strip()
        full_address = request.POST.get('full_address', '').strip()
        payment_method = request.POST.get('payment_method', 'cod').strip()
        order_notes = request.POST.get('order_notes', '').strip()

        if not (full_name and phone and district and full_address):
            messages.error(request, "Please fill in all required shipping fields.")
            return render(request, 'orders/checkout.html', {'cart': cart})

        # Server-side validation of stock & prices
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    full_name=full_name,
                    email=email or (request.user.email if request.user.is_authenticated else ''),
                    phone=phone,
                    division=division,
                    district=district,
                    area=area,
                    full_address=full_address,
                    payment_method=payment_method,
                    order_notes=order_notes,
                    subtotal=cart.get_subtotal(),
                    shipping_cost=cart.get_shipping_cost(),
                    discount_amount=cart.get_discount(),
                    grand_total=cart.get_grand_total(),
                    status='pending'
                )

                for item_key, item_data in cart.cart.items():
                    var_id = item_data.get('variant_id')
                    prod_id = item_data.get('product_id')
                    qty = int(item_data.get('quantity', 1))

                    variant = None
                    product = None
                    if var_id:
                        variant = ProductVariant.objects.filter(id=var_id).first()
                        if variant:
                            product = variant.product
                    if not product and prod_id:
                        product = Product.objects.filter(id=prod_id).first()

                    if not product and not variant:
                        continue

                    price = variant.effective_price if variant else product.effective_price
                    item_title = f"{product.title} ({variant.title})" if variant else product.title

                    # Deduct stock if variant exists
                    if variant and variant.stock_quantity >= qty:
                        variant.stock_quantity -= qty
                        variant.save()

                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        variant=variant,
                        title=item_title,
                        unit_price=price,
                        quantity=qty,
                        total_price=price * qty
                    )

                OrderStatusLog.objects.create(
                    order=order,
                    status='pending',
                    notes='Order placed successfully.'
                )

                cart.clear()
                return redirect('orders:confirmation', order_number=order.order_number)

        except Exception as e:
            messages.error(request, f"Order placement failed: {str(e)}")
            return render(request, 'orders/checkout.html', {'cart': cart})


class OrderConfirmationView(View):
    def get(self, request, order_number):
        order = get_object_or_404(Order.objects.prefetch_related('items'), order_number=order_number)
        return render(request, 'orders/confirmation.html', {'order': order})


class OrderDetailView(View):
    def get(self, request, order_number):
        order = get_object_or_404(Order.objects.prefetch_related('items', 'status_logs'), order_number=order_number)
        return render(request, 'orders/detail.html', {'order': order})
