from django.conf import settings
from django.utils import timezone
from django.core.mail import send_mail
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from notification.models import Notification
from notification.serializers import NotificationSerializer


# ── Helper functions called from signals ─────────────────────────────────────

def create_user_notification(user):
    """Send welcome notification when a new user registers."""
    notification = Notification.objects.create(
        user=user,
        notification_type='welcome',
        message=(
            f"Welcome to HealthPadi, {user.first_name}!\n"
            "You can now search for medical procedure prices across Nigeria."
        ),
    )
    send_mail(
        subject="Welcome to HealthPadi!",
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # FIXED: use settings value
        recipient_list=[user.email],
        fail_silently=False,  # Temporarily set to False to catch errors
    )


def create_provider_notification(provider_user, provider_name, provider_email):
    """Send welcome notification when a provider registers."""
    notification = Notification.objects.create(
        user=provider_user,
        notification_type='welcome',
        message=(
            f"Welcome to HealthPadi, {provider_name}!\n"
            "You can now claim your facility and publish official price lists."
        ),
    )
    send_mail(
        subject="Welcome to HealthPadi — Provider Account",
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # FIXED
        recipient_list=[provider_email],
        fail_silently=True,
    )


def notify_provider_of_claim_result(user, facility_name, approved=True):
    """Notify provider when their facility claim is approved or rejected."""
    if approved:
        message = (
            f"Your claim for {facility_name} has been approved! "
            "You can now publish official prices for this facility."
        )
        notif_type = 'price_submission'
    else:
        message = (
            f"Your claim for {facility_name} was not approved. "
            "Please contact support if you believe this is an error."
        )
        notif_type = 'general'

    notification = Notification.objects.create(
        user=user,
        notification_type=notif_type,
        message=message,
    )
    send_mail(
        subject=f"HealthPadi: Facility Claim {'Approved' if approved else 'Rejected'}",
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # FIXED
        recipient_list=[user.email],
        fail_silently=True,
    )


def notify_provider_of_report(provider_user, facility_name, procedure):
    """Notify provider when a patient reports a price discrepancy at their facility."""
    notification = Notification.objects.create(
        user=provider_user,
        notification_type='price_submission',
        message=(
            f"A patient has reported a price discrepancy for '{procedure}' "
            f"at {facility_name}. Please review your published prices."
        ),
    )
    send_mail(
        subject="HealthPadi: Price Discrepancy Report Received",
        message=notification.message,
        from_email=settings.DEFAULT_FROM_EMAIL,  # FIXED
        recipient_list=[provider_user.email],
        fail_silently=True,
    )


# ── API Endpoints ─────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """List all notifications for the current user."""
    notifications = Notification.objects.filter(user=request.user)
    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_notification_read(request, pk):
    """Mark a single notification as read."""
    try:
        notification = Notification.objects.get(pk=pk, user=request.user)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)

    notification.is_read = True
    notification.read_at = timezone.now()
    notification.save()
    return Response({'message': 'Notification marked as read'})


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all of the current user's notifications as read."""
    Notification.objects.filter(user=request.user, is_read=False).update(
        is_read=True, read_at=timezone.now()
    )
    return Response({'message': 'All notifications marked as read'})
