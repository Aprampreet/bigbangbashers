# eventhub/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('galactic/binary/warp/drive/admin/entry/gn9911/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    # Assuming your create event URL is in core.urls
    path('', include('core.urls')), 
]

handler404 = 'core.views.custom_404_view'

# This line is ONLY for local development.
# In production (DEBUG=False), WhiteNoise handles static files.
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
