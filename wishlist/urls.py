from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('', views.WishlistView.as_view(), name='wishlist_detail'),
    path('api/toggle/', views.ToggleWishlistApiView.as_view(), name='wishlist_toggle'),
    path('api/move-to-cart/<int:item_id>/', views.MoveWishlistToCartView.as_view(), name='move_to_cart'),
]
