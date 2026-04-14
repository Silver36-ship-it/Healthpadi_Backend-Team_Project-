from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/providers/', include('providers.urls')),
    path('api/facilities/', include('facilities.urls')),
    path('api/users/', include('user.urls')),
    path('api/search/', include('search.urls')),
    path('api/reports/', include('reports.urls')),
]