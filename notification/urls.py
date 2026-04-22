from django.urls import path
from .views import notification_list, mark_notification_read, mark_all_read

urlpatterns = [
    path('', notification_list, name='notification-list'),
    path('<int:pk>/read/', mark_notification_read, name='notification-read'),
    path('read-all/', mark_all_read, name='notification-read-all'),
]
