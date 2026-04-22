"""
Django signals for facilities app.

PriceHistory is auto-created every time a FacilityProcedure price changes.
This is triggered automatically — no manual calls needed.
"""
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import FacilityProcedure, PriceHistory


@receiver(pre_save, sender=FacilityProcedure)
def capture_price_history(sender, instance, **kwargs):
    """
    Before saving a FacilityProcedure, check if the price has changed.
    If yes, save the old price to PriceHistory.
    Only fires on updates (not creates — no old price to compare against).
    """
    if instance.pk:
        try:
            old = FacilityProcedure.objects.get(pk=instance.pk)
            if old.price != instance.price:
                PriceHistory.objects.create(
                    facility_procedure=instance,
                    old_price=old.price,
                    new_price=instance.price,
                    # changed_by set in the view if available
                )
        except FacilityProcedure.DoesNotExist:
            pass  # New record, no history to capture
