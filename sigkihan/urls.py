"""
URL configuration for sigkihan project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    # Swagger UI
    path('swagger/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path("redoc", SpectacularRedocView.as_view(), name="redoc"),
    path('api/', include('users.urls')),
    path('api/', include('refriges.urls')),
    path('api/', include('foods.urls')),
    path('api/refrigerators/', include('notifications.urls')),
    path('auth/', include('auth.urls')),
    # path('api/groups/', include('groups.urls')),
    # path('api/refriges/', include('refriges.urls')),
    # path('api/invitations/', include('invitations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
