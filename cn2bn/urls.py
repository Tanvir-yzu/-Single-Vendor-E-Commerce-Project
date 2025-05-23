from django.contrib import admin
from django.urls import path,include
from . import settings
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('products.urls')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('payment/', include('payment.urls')),
    path('', include('dashboard.urls')),
]


urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "FM TRADE INTERNATIONAL Admin"
admin.site.site_title = "FM TRADE INTERNATIONAL Portal"
admin.site.index_title = "Welcome to FM TRADE INTERNATIONAL"