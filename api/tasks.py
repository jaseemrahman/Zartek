from celery import shared_task
from api.models import Ride

@shared_task
def update_ride_location(ride_id, new_location):
    ride = Ride.objects.get(id=ride_id)
    ride.current_location = new_location
    ride.save()