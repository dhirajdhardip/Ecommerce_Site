from django.urls import path
from . import views

app_name = 'compare'

urlpatterns = [
    path('', views.CompareView.as_view(), name='compare_detail'),
    path('api/toggle/', views.ToggleCompareApiView.as_view(), name='compare_toggle'),
    path('api/clear/', views.ClearCompareApiView.as_view(), name='compare_clear'),
]
