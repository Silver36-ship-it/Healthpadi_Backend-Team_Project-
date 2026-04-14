from django.urls import path
from . import views

urlpatterns = [
    path('', views.provider_list, name='provider-list'),
    path('create/', views.provider_create, name='provider-create'),
    path('<int:pk>/', views.provider_detail, name='provider-detail'),
    path('<int:pk>/update/', views.provider_update, name='provider-update'),
    path('<int:pk>/delete/', views.provider_delete, name='provider-delete'),
]
