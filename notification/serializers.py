from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            'id', 'message', 'notification_type', 'channel_type',
            'is_read', 'reference_id', 'created_at', 'read_at',
        ]
        read_only_fields = ['id', 'reference_id', 'created_at']
