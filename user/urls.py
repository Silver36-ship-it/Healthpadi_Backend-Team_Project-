from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import register, login_view, me

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('me/', me, name='me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
