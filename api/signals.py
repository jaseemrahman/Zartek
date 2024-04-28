from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ride

@receiver(post_save, sender=Ride)
def ride_status_changed(sender, instance, created, **kwargs):
    if instance.status == 'STARTED' and not instance.driver_accepted:
        from .tasks import update_ride_location
        update_ride_location.delay(instance.id)