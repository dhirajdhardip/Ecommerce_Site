from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("store.urls")),
    path("user/", include("users.urls")),
    path("cart/", include("cart.urls")),
    path("wishlist/", include("wishlist.urls")),
    path("compare/", include("compare.urls")),
    path("checkout/", include("orders.urls")),
]

from django.views.static import serve
from django.urls import re_path

# Serve media files (in development and fallback in production)
urlpatterns += [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]