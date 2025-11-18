from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('music.urls')),
]

# Serve media and static files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    # STATICFILES_DIRS may contain a Path; ensure we pick the first entry
    static_dirs = getattr(settings, 'STATICFILES_DIRS', [])
    if static_dirs:
        urlpatterns += static(settings.STATIC_URL, document_root=str(static_dirs[0]))