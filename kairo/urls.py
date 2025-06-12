from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/matches/', include('matches.urls')),
    path('api/messages/', include('kairo_messages.urls')),
    path('api/premium/', include('premium.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 