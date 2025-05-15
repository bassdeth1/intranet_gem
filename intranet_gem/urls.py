# /workspaces/intranet_gem/intranet_gem/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Inclusión explícita del namespace para intranet_core
    # El segundo 'intranet_core' en la tupla es el app_name que Django usará para construir el namespace completo.
    # El 'namespace' kwarg es el instance namespace. Para una sola instancia de la app, suelen ser iguales.
    path('', include(('intranet_core.urls', 'intranet_core'), namespace='intranet_core')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)