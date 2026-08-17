from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.CartView.as_view(), name='cart_detail'),
    path('api/update/', views.UpdateCartItemView.as_view(), name='cart_update'),
    path('api/remove/', views.RemoveCartItemView.as_view(), name='cart_remove'),
    path('api/coupon/apply/', views.ApplyCouponView.as_view(), name='apply_coupon'),
]
