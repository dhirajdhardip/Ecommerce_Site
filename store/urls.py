from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('pc-builder/', views.PcBuilderView.as_view(), name='pc_builder'),
    path('api/pc-builder/<str:component_type>/', views.PcBuilderApiView.as_view(), name='pc_builder_api'),
    path('api/products/filter/', views.ProductFilterView.as_view(), name='product_filter'),
    path('api/search/live/', views.LiveSearchApiView.as_view(), name='live_search'),
    path('api/cart/add/', views.AddToCartView.as_view(), name='cart_add'),
    path('api/ai-recommendations/', views.AiRecommendationApiView.as_view(), name='ai_recommendations'),
]
