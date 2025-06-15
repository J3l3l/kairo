from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache
import os
from django.http import FileResponse

# Serve React index.html for all non-API routes
@never_cache
def serve_react(request):
    index_path = os.path.join(settings.BASE_DIR, 'kairo/static/index.html')
    return FileResponse(open(index_path, 'rb'))

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/matches/', include('matches.urls')),
    path('api/messages/', include('kairo_messages.urls')),
    path('api/premium/', include('premium.urls')),
    # Catch-all for React frontend
    path('', serve_react),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 