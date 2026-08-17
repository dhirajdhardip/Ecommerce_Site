from decimal import Decimal
from store.models import ProductVariant, Product
from .models import Coupon

class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart
        self.coupon_code = self.session.get('coupon_code')

    def save(self):
        self.session.modified = True

    def get_subtotal(self):
        subtotal = Decimal('0.00')
        for item in self.cart.values():
            subtotal += Decimal(str(item['unit_price'])) * int(item['quantity'])
        return subtotal

    def get_shipping_cost(self):
        subtotal = self.get_subtotal()
        if subtotal == Decimal('0.00') or subtotal >= Decimal('500.00'):
            return Decimal('0.00')
        return Decimal('15.00')  # Flat shipping fee under $500

    def get_coupon(self):
        if self.coupon_code:
            try:
                coupon = Coupon.objects.get(code=self.coupon_code, active=True)
                valid, msg = coupon.is_valid(self.get_subtotal())
                if valid:
                    return coupon
            except Coupon.DoesNotExist:
                pass
        return None

    def get_discount(self):
        coupon = self.get_coupon()
        if coupon:
            return coupon.calculate_discount(self.get_subtotal())
        return Decimal('0.00')

    def get_grand_total(self):
        return self.get_subtotal() - self.get_discount() + self.get_shipping_cost()

    def get_total_items(self):
        return sum(item['quantity'] for item in self.cart.values())

    def clear(self):
        self.session['cart'] = {}
        self.session['coupon_code'] = None
        self.save()
