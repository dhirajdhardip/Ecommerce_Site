from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.CheckoutView.as_view(), name='checkout'),
    path('confirmation/<str:order_number>/', views.OrderConfirmationView.as_view(), name='confirmation'),
    path('detail/<str:order_number>/', views.OrderDetailView.as_view(), name='detail'),
]
