from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from admin_tools.admin import custom_admin_site


urlpatterns = [
    path("admin/", custom_admin_site.urls),
    # path('admin/', admin.site.urls),
    path('', include('homepage.urls')),
    path('goods/', include('goods.urls')),
    path('discounts/', include('discounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)