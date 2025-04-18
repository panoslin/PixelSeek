"""
URL configuration for pixelseek project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import (
    path,
    include,
)
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter

# Create a router and register API URLs
router = DefaultRouter()

urlpatterns = [
                  path('admin/', admin.site.urls),
                  path('api-auth/', include('rest_framework.urls')),
                  path('api/', include([
                      path('', include(router.urls)),
                      path('videos/', include('videos.urls')),
                      path('users/', include('users.urls')),
                      # path('payments/', include('payments.urls')),
                  ])),
                  path('', RedirectView.as_view(url='/api/', permanent=False)),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
