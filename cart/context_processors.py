from .cart import Cart

def cart_processor(request):
    """Exposes cart instance to all Django templates."""
    cart = Cart(request)
    return {
        'cart': cart,
        'cart_total_items': cart.get_total_items(),
        'cart_subtotal': cart.get_subtotal(),
        'cart_grand_total': cart.get_grand_total(),
    }
